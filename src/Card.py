# Card.py

from enum import Enum, auto
from dataclasses import dataclass
from typing import List

class Suit(Enum):
    Hearts = auto()
    Diamonds = auto()
    Clubs = auto()
    Spades = auto()

class Rank(Enum):
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13
    Ace = 14

@dataclass
class Card:
    suit: Suit
    rank: Rank

def get_value(card: Card) -> int:

    # face cards worth 10
    if card.rank in {Rank.Jack, Rank.Queen, Rank.King}:
        return 10
    
    # assuming aces is 11 for this project
    elif card.rank == Rank.Ace:
        return 11

    # number cards worth their rank
    else:
        return card.rank.value

# string representation of a card
# rank as digit for numbers, letter for face cards, and A for ace
# suit as symbols ♥ ♦ ♣ ♠
def display_card(card: Card) -> str:
    if card.rank in {Rank.Jack, Rank.Queen, Rank.King}:
        rank_display = card.rank.name[0]  # J, Q, K
    elif card.rank == Rank.Ace:
        rank_display = 'A'
    else:
        rank_display = str(card.rank.value)

    suit_display = {
        Suit.Hearts: '♥',
        Suit.Diamonds: '♦',
        Suit.Clubs: '♣',
        Suit.Spades: '♠'
    }[card.suit]

    return f"{rank_display}{suit_display}"

# string representation of a hand
def display_hand(hand: List[Card]) -> str:
    return ', '.join(display_card(card) for card in hand)
