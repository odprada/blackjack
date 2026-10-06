from .card import Card, RANKS, SUITS
import random


class Deck:
    """
    Attributes
    cards: List of cards contained in the deck, initially a standard 52-card deck.

    Methods:
    draw: Shows the top card (last element from the card list) and removes it from the deck.
    shuffle: Applies random.shuffle() to the deck's cards.

    """

    def __init__(self) -> None:
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]

    def __len__(self) -> int:
        return len(self.cards)

    def draw(self) -> Card:
        if not self.cards:
            raise IndexError("Deck is already empty.")
        return self.cards.pop()

    def shuffle(self) -> None:
        random.shuffle(self.cards)