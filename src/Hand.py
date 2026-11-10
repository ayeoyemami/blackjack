# Hand.py

from typing import List
from Card import Card, Rank, get_value, display_card

def hand_sum(hand: List[Card]) -> int:
    total = sum(get_value(card) for card in hand)
    high_ace_count = sum(card.rank == Rank.Ace for card in hand)

    while total > 21 and high_ace_count:
        total -= 10
        high_ace_count -= 1

    return total

def has_high_ace(hand: List[Card]) -> bool:
    total = sum(get_value(card) for card in hand)
    high_ace_count = sum(card.rank == Rank.Ace for card in hand)

    while total > 21 and high_ace_count:
        total -= 10
        high_ace_count -= 1

    return bool(high_ace_count)

# string representation of a hand
def display_hand(hand: List[Card]) -> str:
    return ', '.join(display_card(card) for card in hand)
