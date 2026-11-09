# Controller.py

import random
from GameState import GameState
from Card import Card, Rank, Suit, display_card, display_hand
from Agents import Agent

class Controller:
    def __init__(self, game_state: GameState, agent: Agent):
        self.agent = agent
        self.game_state = game_state

    def start_game(self):
        # fill & shuffle deck, deal initial hands
        self.game_state.deck = [Card(suit, rank) for suit in Suit for rank in Rank]
        random.shuffle(self.game_state.deck)
        self.game_state.hand = [self.game_state.deck.pop(), self.game_state.deck.pop()]
        self.game_state.dealer_hand = [self.game_state.deck.pop(), self.game_state.deck.pop()]

        # reveal info
        print(f"upcard: {display_card(self.game_state.get_dealer_first_card())}")
        print(f"hand: {display_hand(self.game_state.get_hand())} = {self.game_state.get_hand_sum()}")

        # resolve initial push (tie)
        if self.game_state.get_hand_sum() == 21 and self.game_state.get_dealer_hand_sum() == 21:
            print("push: both have 21")
            return

        # resolve initial blackjack
        if self.game_state.get_hand_sum() == 21:
            print("win: blackjack")
            return

        # resolve initial dealer blackjack
        if self.game_state.get_dealer_hand_sum() == 21:
            print(f"dealer hand: {display_hand(self.game_state.dealer_hand)} = {self.game_state.get_dealer_hand_sum()}")
            print("loss: dealer blackjack")
            return
        
        # game loop
        while True:
            # get action from agent
            action = self.agent.get_action(self.game_state.get_hand_sum(), self.game_state.get_dealer_first_card())

            if action not in ["hit", "stand"]:
                print("bad action")
                return
            
            # process action
            if action == "stand":
                print(f"final hand: {display_hand(self.game_state.get_hand())} = {self.game_state.get_hand_sum()}")

                # dealer finishes
                self.resolve_game()
                return

            # process hit action
            self.game_state.hand.append(self.game_state.deck.pop())
            print(f"hand: {display_hand(self.game_state.get_hand())} = {self.game_state.get_hand_sum()}")

            # bust
            if self.game_state.get_hand_sum() > 21:
                print(f"loss: bust with {self.game_state.get_hand_sum()}")
                return

            # blackjack
            if self.game_state.get_hand_sum() == 21:
                self.resolve_game()
                return

    # after player stands or hits 21, dealer plays and game is resolved
    def resolve_game(self):
        # dealer finishes
        while self.game_state.get_dealer_hand_sum() < 17:
            self.game_state.dealer_hand.append(self.game_state.deck.pop())

        print(f"dealer ending hand: {display_hand(self.game_state.dealer_hand)} = {self.game_state.get_dealer_hand_sum()}")

        if self.game_state.get_dealer_hand_sum() > 21:
            print(f"win: dealer bust with {self.game_state.get_dealer_hand_sum()}")
            return

        if self.game_state.get_dealer_hand_sum() > self.game_state.get_hand_sum():
            print(f"loss: {self.game_state.get_dealer_hand_sum()} > {self.game_state.get_hand_sum()}")
            return

        elif self.game_state.get_dealer_hand_sum() < self.game_state.get_hand_sum():
            print(f"win: {self.game_state.get_hand_sum()} > {self.game_state.get_dealer_hand_sum()}")
            return

        elif self.game_state.get_dealer_hand_sum() == self.game_state.get_hand_sum():
            print(f"push: {self.game_state.get_hand_sum()}")
            return
