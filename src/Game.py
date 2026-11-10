# Controller.py

import random
from typing import List

from Card import Card, Rank, Suit, display_card
from Hand import hand_sum, display_hand, has_high_ace
from Agents import Agent
from State import State

class Game:
    hand: List[Card]
    dealer_hand: List[Card]
    deck:List[Card]

    def __init__(self, agent: Agent):
        self.agent = agent

    def run(self):
        # fill & shuffle deck, deal initial hands, show upcard and player hand
        self.deck = [Card(suit, rank) for suit in Suit for rank in Rank]
        random.shuffle(self.deck)
        self.hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]

        upcard = self.dealer_hand[0]
        print(f"upcard: {display_card(upcard)}")
        print(f"hand: {display_hand(self.hand)} = {hand_sum(self.hand)}")

        # resolve initial push (tie)
        if hand_sum(self.hand) == 21 and hand_sum(self.dealer_hand) == 21:
            print("push: both have 21")
            return 0

        # resolve initial blackjack
        if hand_sum(self.hand) == 21:
            print("win: blackjack")
            return 1

        # resolve initial dealer blackjack
        if hand_sum(self.dealer_hand) == 21:
            print(f"dealer hand: {display_hand(self.dealer_hand)} = {hand_sum(self.dealer_hand)}")
            print("loss: dealer blackjack")
            return -1
        
        # game loop
        while True:
            # record sum for observation
            current_sum = hand_sum(self.hand)
            current_high_ace = has_high_ace(self.hand)

            # get action from agent
            action = self.agent.get_action(State(current_sum, upcard.rank, current_high_ace))
            
            # process stand
            if action == "stand":
                print(f"final hand: {display_hand(self.hand)} = {hand_sum(self.hand)}")

                # dealer finishes, observe, and end game
                reward = self.resolve_game()
                self.agent.observe(State(current_sum, upcard.rank, current_high_ace), action, reward, State(hand_sum(self.hand), upcard.rank, has_high_ace(self.hand)), True)
                return reward
                
            # process hit action
            self.hand.append(self.deck.pop())
            print(f"hand: {display_hand(self.hand)} = {hand_sum(self.hand)}")

            # bust
            if hand_sum(self.hand) > 21:
                print(f"loss: bust with {hand_sum(self.hand)}")
                reward = -1
                self.agent.observe(State(current_sum, upcard.rank, current_high_ace), action, reward, State(hand_sum(self.hand), upcard.rank, has_high_ace(self.hand)), True)
                return reward

            # 21
            if hand_sum(self.hand) == 21:
                reward = self.resolve_game()
                self.agent.observe(State(current_sum, upcard.rank, current_high_ace), action, reward, State(hand_sum(self.hand), upcard.rank, has_high_ace(self.hand)), True)
                return reward

            # observe non-terminal hit
            self.agent.observe(State(current_sum, upcard.rank, current_high_ace), action, 0, State(hand_sum(self.hand), upcard.rank, has_high_ace(self.hand)), False)

    # after player stands or hits 21, dealer plays and game is resolved
    def resolve_game(self):
        # dealer finishes
        while hand_sum(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())

        print(f"dealer ending hand: {display_hand(self.dealer_hand)} = {hand_sum(self.dealer_hand)}")

        # win b/c dealer bust
        if hand_sum(self.dealer_hand) > 21:
            print(f"win: dealer bust with {hand_sum(self.dealer_hand)}")
            return 1

        # loss b/c dealer has higher hand
        if hand_sum(self.dealer_hand) > hand_sum(self.hand):
            print(f"loss: {hand_sum(self.dealer_hand)} > {hand_sum(self.hand)}")
            return -1

        # win b/c dealer has lower hand
        elif hand_sum(self.dealer_hand) < hand_sum(self.hand):
            print(f"win: {hand_sum(self.hand)} > {hand_sum(self.dealer_hand)}")
            return 1

        # push b/c hands equal
        elif hand_sum(self.dealer_hand) == hand_sum(self.hand):
            print(f"push: {hand_sum(self.hand)}")
            return 0
