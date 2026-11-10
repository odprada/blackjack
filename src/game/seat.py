from dataclasses import dataclass

from ..classes.hand import Hand

BUST_VALUE = 21

@dataclass
class Seat:
    """
    One player's place at the table.

    Attributes:
        name: Display name.
        hand: The player's hand.
        stood: Whether the player has ended their turn.

    Properties:
        bust: Hand is over 21.
        done: Nothing left to do this round (stood, bust, or already on 21).
        live: Still has to be played against by the dealer (not bust, not a natural blackjack).
    """

    name: str
    hand: Hand
    stood: bool = False

    @property
    def bust(self) -> bool:
        return self.hand.value > BUST_VALUE

    @property
    def done(self) -> bool:
        return self.stood or self.bust or self.hand.value == BUST_VALUE

    @property
    def live(self) -> bool:
        return not self.bust and not self.hand.is_blackjack