from .card import Card, RANKS, SUITS


class Deck:
    """
    Attributes
    cards: List of cards contained in the deck, initially a standard 52-card deck.

    Methods:
    draw: Shows a card and removes it from the deck.

    """

    def __init__(self) -> None:
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]

    def draw(self) -> Card:
        if not self.cards:
            raise IndexError("Deck is already empty.")
        return self.cards.pop()

    def __len__(self) -> int:
        return len(self.cards)