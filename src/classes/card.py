from dataclasses import dataclass
from typing import List

RANKS = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A')
SUITS = ("♠", "♥", "♦", "♣")


@dataclass(frozen=False, order=False)
class Card:
    """
    Attributes:
        rank: One of RANKS.
        suit: One of SUITS.
    """

    rank: str
    suit: str

    @property
    def cardvalue(self) -> int:
        if self.rank in ('J', 'Q', 'K'):
            return 10
        elif self.rank == 'A':
            return 11
        return int(self.rank)

    def __post_init__(self) -> None:
        if self.rank not in RANKS:
            raise ValueError(f"Invalid rank.")
        if self.suit not in SUITS:
            raise ValueError(f"Invalid suit.")

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"