from dataclasses import dataclass, field
from typing import List
from .card import Card


@dataclass
class Hand:
    """
    Attributes:
        cards: Cards contained in the hand.
        cardnumber: Number of cards contained in the hand.
        value: Sum of the values of all the hand's cards
    """

    cards: List[Card]

    @property
    def card_number(self) -> int:
        return len(self.cards)

    @property
    def is_blackjack(self) -> bool:
        return self.card_number == 2 and self.value == 21

    @property
    def value(self) -> int:
        return sum(x.cardvalue for x in self.cards)
    
    def __post_init__(self) -> None:
        if self.card_number == 0:
            raise ValueError(f"Hand cannot be empty.")

        if self.value <= 0:
            raise ValueError(f"Hand cannot have value less or equal to zero.")

    def add_card(self, x: Card):
        self.cards.append(x)