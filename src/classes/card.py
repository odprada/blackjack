from dataclasses import dataclass

RANKS = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A')
SUITS = ("♠", "♥", "♦", "♣")


@dataclass(frozen=True, order=False)
class Card:
    """
    Attributes:
        rank: One of RANKS.
        suit: One of SUITS.

    Properties:
        card_value: The actual value of the card, obtained with a method using the rank.

    The value of A is set to 11, and cases when its value has to be 1 are handled through the Hand class.

    """

    rank: str
    suit: str

    @property
    def card_value(self) -> int:
        if self.rank in ('J', 'Q', 'K'):
            return 10
        elif self.rank == 'A':
            return 11
        return int(self.rank)

    def __post_init__(self) -> None:
        if self.rank not in RANKS:
            raise ValueError(f"Invalid rank: {self.rank!r}")
        if self.suit not in SUITS:
            raise ValueError(f"Invalid suit: {self.suit!r}")

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"