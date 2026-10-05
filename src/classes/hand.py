from dataclasses import dataclass
from .card import Card


@dataclass
class Hand:
    """
    Attributes:
        cards: Cards contained in the hand.
        is_split: Indicates whether the hand comes from splitting a previous hand.

    Properties:
        card_number: Number of cards contained in the hand.
        is_blackjack: Indicates whether the hand is a blackjack.
        value: Sum of the values of all the hand's cards.
        is_soft: Indicates whether the hand is soft (has at least one Ace acting as 11).
    """

    cards: list[Card]
    is_split: bool = False

    @property
    def card_number(self) -> int:
        return len(self.cards)

    @property
    def is_blackjack(self) -> bool:
        return self.card_number == 2 and self.value == 21 and not self.is_split

    # evaluate function provided by Claude
    def _evaluate(self) -> tuple[int, bool]:
        total = sum(c.cardvalue for c in self.cards)
        soft_aces = sum(1 for c in self.cards if c.rank == 'A')
        while total > 21 and soft_aces > 0:
            total -= 10
            soft_aces -= 1
        return total, soft_aces > 0

    @property
    def value(self) -> int:
        return self._evaluate()[0]

    @property
    def is_soft(self) -> bool:
        return self._evaluate()[1]

    def __post_init__(self) -> None:
        if self.card_number == 0:
            raise ValueError(f"Hand cannot be empty.")

    def add_card(self, x: Card) -> None:
        self.cards.append(x)