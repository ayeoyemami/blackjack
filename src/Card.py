# Card.py

from enum import Enum, auto
from dataclasses import dataclass

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

@dataclass(frozen=True)
class Card:
    suit: Suit
    rank: Rank

    def value(self) -> int:
        # face cards worth 10
        if self.rank in {Rank.Jack, Rank.Queen, Rank.King}:
            return 10
        
        # ace is 1 or 11
        elif self.rank == Rank.Ace:
            # get_hand_sum depends on this returning 11
            return 11

        # number cards worth their rank
        else:
            return self.rank.value

    # string representation of a card
    # rank as digit for numbers, letter for face cards, and A for ace
    # suit as symbols ♥ ♦ ♣ ♠
    def str(self) -> str:
        if self.rank in {Rank.Jack, Rank.Queen, Rank.King}:
            rank_str = self.rank.name[0]  # J, Q, K
        elif self.rank == Rank.Ace:
            rank_str = 'A'
        else:
            rank_str = str(self.rank.value)

        suit_str = {
            Suit.Hearts: '♥',
            Suit.Diamonds: '♦',
            Suit.Clubs: '♣',
            Suit.Spades: '♠'
        }[self.suit]

        return f"{rank_str}{suit_str}"
