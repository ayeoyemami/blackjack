# State.py

from dataclasses import dataclass
from Card import Rank

@dataclass
class State:
    hand_score: int
    upcard_rank: Rank
    has_high_ace: bool
