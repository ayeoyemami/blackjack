# Game.py

import random

from Card import Card, Rank, Suit
from Hand import Hand
from Agents import Agent
from State import State

class Game:
    def __init__(self, agent: Agent, output):
        self.agent = agent
        self.output = output
        self.hand = Hand()
        self.dealer_hand = Hand()
        self.deck = []

    def run(self):
        # fill & shuffle deck, deal initial hands
        self.deck = [Card(suit, rank) for suit in Suit for rank in Rank]
        random.shuffle(self.deck)
        self.hand.cards = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand.cards = [self.deck.pop(), self.deck.pop()] 

        # show upcard and player hand
        upcard = self.dealer_hand.cards[0]
        self.output(f"upcard: {upcard.str()}")
        self.output(f"hand: {self.hand.str()} = {self.hand.score()}")

        # resolve initial push (tie)
        if self.hand.score() == 21 and self.dealer_hand.score() == 21:
            self.output("push: both have 21")
            return 0

        # resolve initial blackjack
        if self.hand.score() == 21:
            self.output("win: blackjack")
            return 1

        # resolve initial dealer blackjack
        if self.dealer_hand.score() == 21:
            self.output(f"dealer hand: {self.dealer_hand.str()} = {self.dealer_hand.score()}")
            self.output("loss: dealer blackjack")
            return -1
        
        # game loop
        while True:
            # record sum for observation
            current_sum = self.hand.score()
            current_high_ace = self.hand.has_high_ace()

            # get action from agent
            action = self.agent.get_action(State(current_sum, upcard.rank, current_high_ace))
            
            # process stand
            if action == "stand":
                self.output(f"final hand: {self.hand.str()} = {self.hand.score()}")

                # dealer finishes, observe, and end game
                reward = self.resolve_game()
                self.agent.observe(
                    State(current_sum, upcard.rank, current_high_ace),
                    action,
                    reward,
                    State(self.hand.score(), upcard.rank, self.hand.has_high_ace()),
                    True
                )
                return reward
                
            # process hit
            self.hand.cards.append(self.deck.pop())
            self.output(f"hand: {self.hand.str()} = {self.hand.score()}")

            # bust
            if self.hand.score() > 21:
                self.output(f"loss: bust with {self.hand.score()}")
                reward = -1
                self.agent.observe(
                    State(current_sum, upcard.rank, current_high_ace),
                    action,
                    reward,
                    State(self.hand.score(), upcard.rank, self.hand.has_high_ace()),
                    True
                )
                return reward

            # 21
            if self.hand.score() == 21:
                reward = self.resolve_game()
                self.agent.observe(
                    State(current_sum, upcard.rank, current_high_ace),
                    action,
                    reward,
                    State(self.hand.score(), upcard.rank, self.hand.has_high_ace()),
                    True
                )
                return reward

            # observe non-terminal hit
            self.agent.observe(
                State(current_sum, upcard.rank, current_high_ace),
                action,
                0,
                State(self.hand.score(), upcard.rank, self.hand.has_high_ace()),
                False
            )

    # after player stands or hits 21, dealer plays and game is resolved
    def resolve_game(self):
        # dealer finishes
        while self.dealer_hand.score() < 17:
            self.dealer_hand.cards.append(self.deck.pop())

        self.output(f"dealer ending hand: {self.dealer_hand.str()} = {self.dealer_hand.score()}")

        # win b/c dealer bust
        if self.dealer_hand.score() > 21:
            self.output(f"win: dealer bust with {self.dealer_hand.score()}")
            return 1

        # loss b/c dealer has higher hand
        if self.dealer_hand.score() > self.hand.score():
            self.output(f"loss: {self.dealer_hand.score()} > {self.hand.score()}")
            return -1

        # win b/c dealer has lower hand
        elif self.dealer_hand.score() < self.hand.score():
            self.output(f"win: {self.hand.score()} > {self.dealer_hand.score()}")
            return 1

        # push b/c hands equal
        elif self.dealer_hand.score() == self.hand.score():
            self.output(f"push: {self.hand.score()}")
            return 0
