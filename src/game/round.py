from ..classes.deck import Deck
from ..classes.hand import Hand
from .dealer import dealer_play


class Round:
    """
    Game logic of a round.

    Attributes:
    round_number: Indicates the number of round
    """

    round_number: int
