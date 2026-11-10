# Controller.py

import random
from typing import List
from GameState import GameState
from Card import Card, Rank, Suit, display_card
from Hand import display_hand, has_high_ace
from Agents import Agent
from State import State

class Controller:
    h: List[Card]

    def __init__(self, game_state: GameState, agent: Agent):
        self.agent = agent
        self.game_state = game_state

    def run(self):
        # fill & shuffle deck, deal initial hands, show upcard and player hand
        self.game_state.deck = [Card(suit, rank) for suit in Suit for rank in Rank]
        random.shuffle(self.game_state.deck)
        self.game_state.hand = [self.game_state.deck.pop(), self.game_state.deck.pop()]
        self.game_state.dealer_hand = [self.game_state.deck.pop(), self.game_state.deck.pop()]
        print(f"upcard: {display_card(self.game_state.get_dealer_first_card())}")
        print(f"hand: {display_hand(self.game_state.get_hand())} = {self.game_state.get_agent_hand_sum()}")

        # resolve initial push (tie)
        if self.game_state.get_agent_hand_sum() == 21 and self.game_state.get_dealer_hand_sum() == 21:
            print("push: both have 21")
            return 0

        # resolve initial blackjack
        if self.game_state.get_agent_hand_sum() == 21:
            print("win: blackjack")
            return 1

        # resolve initial dealer blackjack
        if self.game_state.get_dealer_hand_sum() == 21:
            print(f"dealer hand: {display_hand(self.game_state.dealer_hand)} = {self.game_state.get_dealer_hand_sum()}")
            print("loss: dealer blackjack")
            return -1
        
        # game loop
        while True:
            # record states for observation
            hand_sum = self.game_state.get_agent_hand_sum()
            upcard = self.game_state.get_dealer_first_card()

            # get action from agent
            action = self.agent.get_action(State(hand_sum, upcard.rank, has_high_ace(self.game_state.hand)))
            
            # process stand
            if action == "stand":
                print(f"final hand: {display_hand(self.game_state.get_hand())} = {self.game_state.get_agent_hand_sum()}")

                # dealer finishes, observe, and end game
                reward = self.resolve_game()
                self.agent.observe(State(hand_sum, upcard.rank, has_high_ace(self.game_state.hand)), action, reward, State(self.game_state.get_agent_hand_sum(), upcard.rank, has_high_ace(self.game_state.hand)), True)
                return reward
                
            # process hit action
            self.game_state.hand.append(self.game_state.deck.pop())
            print(f"hand: {display_hand(self.game_state.get_hand())} = {self.game_state.get_agent_hand_sum()}")

            # bust
            if self.game_state.get_agent_hand_sum() > 21:
                print(f"loss: bust with {self.game_state.get_agent_hand_sum()}")
                reward = -1
                self.agent.observe(State(hand_sum, upcard.rank, has_high_ace(self.game_state.hand)), action, reward, State(self.game_state.get_agent_hand_sum(), upcard.rank, has_high_ace(self.game_state.hand)), True)
                return reward

            # 21
            if self.game_state.get_agent_hand_sum() == 21:
                reward = self.resolve_game()
                self.agent.observe(State(hand_sum, upcard.rank, has_high_ace(self.game_state.hand)), action, reward, State(self.game_state.get_agent_hand_sum(), upcard.rank, has_high_ace(self.game_state.hand)), True)
                return reward

            # observe non-terminal hit
            self.agent.observe(State(hand_sum, upcard.rank, has_high_ace(self.game_state.hand)), action, 0, State(self.game_state.get_agent_hand_sum(), upcard.rank, has_high_ace(self.game_state.hand)), False)

    # after player stands or hits 21, dealer plays and game is resolved
    def resolve_game(self):
        # dealer finishes
        while self.game_state.get_dealer_hand_sum() < 17:
            self.game_state.dealer_hand.append(self.game_state.deck.pop())

        print(f"dealer ending hand: {display_hand(self.game_state.dealer_hand)} = {self.game_state.get_dealer_hand_sum()}")

        # win b/c dealer bust
        if self.game_state.get_dealer_hand_sum() > 21:
            print(f"win: dealer bust with {self.game_state.get_dealer_hand_sum()}")
            return 1

        # loss b/c dealer has higher hand
        if self.game_state.get_dealer_hand_sum() > self.game_state.get_agent_hand_sum():
            print(f"loss: {self.game_state.get_dealer_hand_sum()} > {self.game_state.get_agent_hand_sum()}")
            return -1

        # win b/c dealer has lower hand
        elif self.game_state.get_dealer_hand_sum() < self.game_state.get_agent_hand_sum():
            print(f"win: {self.game_state.get_agent_hand_sum()} > {self.game_state.get_dealer_hand_sum()}")
            return 1

        # push b/c hands equal
        elif self.game_state.get_dealer_hand_sum() == self.game_state.get_agent_hand_sum():
            print(f"push: {self.game_state.get_agent_hand_sum()}")
            return 0
