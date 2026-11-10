# GameState.py

from Hand import hand_sum

class GameState:
    def __init__(self):
        self.hand = []
        self.deck = []
        self.dealer_hand = []

    def get_hand(self):
        return self.hand

    def get_agent_hand_sum(self):
        return hand_sum(self.hand)

    def get_dealer_first_card(self):
        return self.dealer_hand[0] if self.dealer_hand else None

    def get_dealer_hand_sum(self):
        return hand_sum(self.dealer_hand)
