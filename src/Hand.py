# Hand.py

from typing import List
from Card import Card, Rank, get_value, display_card

class Hand:
    cards: List[Card]

    def score(self) -> int:
        total = sum(get_value(card) for card in self.cards)
        high_ace_count = sum(card.rank == Rank.Ace for card in self.cards)

        while total > 21 and high_ace_count:
            total -= 10
            high_ace_count -= 1

        return total

    def has_high_ace(self) -> bool:
        total = sum(get_value(card) for card in self.cards)
        high_ace_count = sum(card.rank == Rank.Ace for card in self.cards)

        while total > 21 and high_ace_count:
            total -= 10
            high_ace_count -= 1

        return bool(high_ace_count)

    # string representation of a hand
    def str(self) -> str:
        return ', '.join(display_card(card) for card in self.cards)
