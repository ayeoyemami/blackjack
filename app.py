"""
app.py  –  Flask web server for the Blackjack RL project.

The backend is entirely built on the game engine written by teammates:
  Card, Hand, State  (data layer)
  Game               (game orchestration)
  QLearningAgent, SARSAAgent  (RL agents, pre-trained on startup)

This file adds only the web API layer.  Nothing in src/ is modified.

Endpoints
---------
GET  /                      Serve the main page
POST /api/new-game          Start a new hand; returns initial game state
POST /api/action            Send "hit" or "stand"; returns updated state
POST /api/ai-game           Play a full game with an RL agent;
                            returns every intermediate state so the
                            frontend can animate them
GET  /api/results           Return training statistics from the CSV files
"""

import csv
import os
import random
import sys
import uuid

from flask import Flask, jsonify, render_template, request, session

# Make the teammates' modules importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from Card import Card, Rank, Suit
from Hand import Hand
from State import State
from RLAgents import QLearningAgent, SARSAAgent

app = Flask(__name__)
app.secret_key = "bj-demo-secret"   # needed for Flask sessions

# ── Active game sessions (game_id → GameSession) ──────────────────────────────
_sessions: dict = {}

# ── Pre-trained agents (loaded once on startup) ───────────────────────────────
_agents: dict = {}


# ─────────────────────────────────────────────────────────────────────────────
# GameSession  –  step-by-step game controller
#
# Game.run() is a full blocking loop designed for agents, so we cannot use it
# directly for a web API.  GameSession reimplements the same rules using the
# teammates' Card, Hand, and State classes, but exposes a turn-by-turn API.
# ─────────────────────────────────────────────────────────────────────────────

class GameSession:
    """
    Manages one blackjack hand step by step.

    Uses Card and Hand from the teammates' code for all game logic.
    The state is serialisable to JSON for the frontend.
    """

    def __init__(self):
        # Build and shuffle a standard 52-card deck (same as Game.py)
        self.deck = [Card(suit, rank) for suit in Suit for rank in Rank]
        random.shuffle(self.deck)

        # Deal initial two cards each
        self.player = Hand()
        self.dealer = Hand()
        self.player.cards = [self.deck.pop(), self.deck.pop()]
        self.dealer.cards = [self.deck.pop(), self.deck.pop()]

        self.upcard = self.dealer.cards[0]   # the visible dealer card
        self.done   = False
        self.result = None   # "win" | "loss" | "push"
        self.message = ""

        # Check for immediate blackjacks on deal
        self._check_initial()

    # ── Actions ───────────────────────────────────────────────────────────────

    def hit(self):
        """Player draws one card."""
        if self.done:
            return

        self.player.cards.append(self.deck.pop())
        score = self.player.score()

        if score > 21:
            self.done    = True
            self.result  = "loss"
            self.message = f"Bust! ({score})"
        elif score == 21:
            self._resolve()
        # else: game continues

    def stand(self):
        """Player stands; dealer plays out and game is resolved."""
        if self.done:
            return
        self._resolve()

    # ── State serialisation ───────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """
        Return a JSON-ready snapshot of the game state.

        dealer_cards is None while the hand is in progress (hole card hidden).
        """
        return {
            "player_cards":  [_card_to_dict(c) for c in self.player.cards],
            "player_score":  self.player.score(),
            "dealer_upcard": _card_to_dict(self.upcard),
            # Reveal full dealer hand only after the game ends
            "dealer_cards":  [_card_to_dict(c) for c in self.dealer.cards]
                             if self.done else None,
            "dealer_score":  self.dealer.score() if self.done else None,
            "done":    self.done,
            "result":  self.result,
            "message": self.message,
        }

    def get_rl_state(self) -> State:
        """Return the current State for passing to an RL agent."""
        return State(
            self.player.score(),
            self.upcard.rank,
            self.player.has_high_ace(),
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _check_initial(self):
        p21 = self.player.score() == 21
        d21 = self.dealer.score() == 21

        if p21 and d21:
            self.done    = True
            self.result  = "push"
            self.message = "Push — both have blackjack"
        elif p21:
            self.done    = True
            self.result  = "win"
            self.message = "Blackjack!"
        elif d21:
            self.done    = True
            self.result  = "loss"
            self.message = "Dealer has blackjack"

    def _resolve(self):
        """Dealer draws to 17+, then compare hands."""
        while self.dealer.score() < 17:
            self.dealer.cards.append(self.deck.pop())

        p = self.player.score()
        d = self.dealer.score()

        if d > 21:
            self.result  = "win"
            self.message = f"Dealer busts ({d})!"
        elif p > d:
            self.result  = "win"
            self.message = f"Win — {p} vs {d}"
        elif p < d:
            self.result  = "loss"
            self.message = f"Loss — {p} vs {d}"
        else:
            self.result  = "push"
            self.message = f"Push — {p}"

        self.done = True


# ── Helpers ───────────────────────────────────────────────────────────────────

def _card_to_dict(card: Card) -> dict:
    """Convert a Card to a JSON-friendly dict."""
    rank_str = card.str()[:-1]   # everything before the suit symbol
    suit_str = card.str()[-1]    # the suit symbol
    return {
        "rank": rank_str,
        "suit": suit_str,
        "red":  card.suit in (Suit.Hearts, Suit.Diamonds),
    }


def _train_agent(cls, episodes: int = 8_000) -> QLearningAgent:
    """Train an agent silently and return it ready for evaluation."""
    agent = cls(alpha=0.1, gamma=0.9, epsilon=0.1)
    agent.training = True

    # Inline game loop (same as train_agents.py) — avoids importing Game
    # so that we keep the import surface minimal
    from Game import Game
    for i in range(episodes):
        agent.epsilon = max(0.05, 0.3 * (0.9995 ** i))
        Game(agent, lambda _: None).run()

    agent.training = False
    agent.epsilon  = 0
    return agent


# ── Startup: pre-train agents ─────────────────────────────────────────────────

print("Pre-training Q-learning agent…", flush=True)
_agents["qlearning"] = _train_agent(QLearningAgent)
print("Pre-training SARSA agent…",      flush=True)
_agents["sarsa"]     = _train_agent(SARSAAgent)
print("Agents ready.", flush=True)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/new-game", methods=["POST"])
def new_game():
    """Start a new hand and return the initial game state."""
    game_id = str(uuid.uuid4())
    gs = GameSession()
    _sessions[game_id] = gs
    state = gs.to_dict()
    state["game_id"] = game_id
    return jsonify(state)


@app.route("/api/action", methods=["POST"])
def action():
    """
    Process a player action (hit / stand).

    Body: { game_id, action }
    """
    body    = request.get_json()
    game_id = body.get("game_id")
    act     = body.get("action")

    gs = _sessions.get(game_id)
    if gs is None:
        return jsonify({"error": "game not found"}), 404

    if act == "hit":
        gs.hit()
    elif act == "stand":
        gs.stand()

    state = gs.to_dict()
    state["game_id"] = game_id
    return jsonify(state)


@app.route("/api/ai-game", methods=["POST"])
def ai_game():
    """
    Play a complete game with one of the pre-trained RL agents.

    Body: { agent: "qlearning" | "sarsa" }

    Returns an ordered list of state snapshots so the frontend can
    animate each step (deal → hits → stand → reveal).
    """
    body       = request.get_json()
    agent_key  = body.get("agent", "qlearning")
    agent      = _agents.get(agent_key)

    if agent is None:
        return jsonify({"error": "unknown agent"}), 400

    gs     = GameSession()
    steps  = [gs.to_dict()]        # snapshot after the initial deal

    while not gs.done:
        rl_state = gs.get_rl_state()
        move     = agent.get_action(rl_state)

        if move == "hit":
            gs.hit()
        else:
            gs.stand()

        steps.append(gs.to_dict())

    return jsonify({"steps": steps, "agent": agent_key})


@app.route("/api/results")
def results():
    """
    Return experiment statistics from the CSV files produced by
    the teammates' train_agents.py script.
    """
    base = os.path.dirname(__file__)
    rows = []
    path = os.path.join(base, "experiment_results.csv")
    if os.path.exists(path):
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))

    curves = []
    path2  = os.path.join(base, "learning_curves.csv")
    if os.path.exists(path2):
        with open(path2, newline="") as f:
            curves = list(csv.DictReader(f))

    return jsonify({"results": rows, "curves": curves})


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=False, port=5000)
