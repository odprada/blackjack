from dataclasses import dataclass, field

from ..classes.deck import Deck
from ..classes.hand import Hand

OUTCOMES = {
    "player_win": "You win!",
    "player_blackjack": "Blackjack!",
    "dealer_win": "Dealer wins",
    "tie": "Tie",
}

STAND_VALUE = 17
BUST_VALUE = 21
MAX_PLAYERS = 4


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


@dataclass
class Round:
    """
    Game logic of a single round with 1 to MAX_PLAYERS players against the dealer.

    Attributes:
        deck: Deck used for the game.
        num_players: Number of seats.
        seats: The players' seats, in turn order.
        dealer_hand: The dealer's hand.
        current: Index of the seat whose turn it is (== len(seats) once all are done).
        dealer_turn: True once every player is done and the dealer takes over.

    Properties:
        active_seat: The seat whose turn it is, or None during the dealer's turn / after the round.
        dealer_must_draw: The dealer still has to take a card.
        is_over: The round has ended.

    The dealer stands on all 17s. The dealer plays one card at a time through dealer_step(),
    so the GUI can animate it; play_dealer() runs the whole turn at once.
    """

    deck: Deck
    num_players: int = 1
    seats: list[Seat] = field(init=False)
    dealer_hand: Hand = field(init=False)
    current: int = field(default=0, init=False)
    dealer_turn: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if not 1 <= self.num_players <= MAX_PLAYERS:
            raise ValueError(f"num_players must be between 1 and {MAX_PLAYERS}.")

        hands: list[list] = [[] for _ in range(self.num_players + 1)]
        for _ in range(2):
            for cards in hands:
                cards.append(self.deck.draw())

        self.seats = [
            Seat(f"Player {i + 1}", Hand(cards)) for i, cards in enumerate(hands[:-1])
        ]
        self.dealer_hand = Hand(hands[-1])
        self._advance()

    @property
    def active_seat(self) -> Seat | None:
        return None if self.dealer_turn else self.seats[self.current]

    @property
    def dealer_must_draw(self) -> bool:
        return (
            self.dealer_turn
            and self.dealer_hand.value < STAND_VALUE
            and any(seat.live for seat in self.seats)
        )

    @property
    def is_over(self) -> bool:
        return self.dealer_turn and not self.dealer_must_draw

    def _advance(self) -> None:
        """Move to the next seat that still has a decision to make; hand over to the dealer when none is left."""
        if self.dealer_hand.is_blackjack:
            self.current = len(self.seats)
        while self.current < len(self.seats) and self.seats[self.current].done:
            self.current += 1
        if self.current >= len(self.seats):
            self.dealer_turn = True

    def hit(self) -> None:
        if self.dealer_turn:
            return
        self.active_seat.hand.add_card(self.deck.draw())
        self._advance()

    def stand(self) -> None:
        if self.dealer_turn:
            return
        self.active_seat.stood = True
        self._advance()

    def dealer_step(self) -> bool:
        """Dealer takes one card if the rules say so. Returns True if a card was drawn."""
        if not self.dealer_must_draw:
            return False
        self.dealer_hand.add_card(self.deck.draw())
        return True

    def play_dealer(self) -> None:
        while self.dealer_step():
            pass

    def outcome(self, seat: Seat) -> str | None:
        """Result for one seat, or None while the round is still going."""
        if not self.is_over:
            return None

        player, dealer = seat.hand, self.dealer_hand

        if player.is_blackjack or dealer.is_blackjack:
            if player.is_blackjack and dealer.is_blackjack:
                return OUTCOMES["tie"]
            return OUTCOMES["player_blackjack"] if player.is_blackjack else OUTCOMES["dealer_win"]
        if seat.bust:
            return OUTCOMES["dealer_win"]
        if dealer.value > BUST_VALUE or player.value > dealer.value:
            return OUTCOMES["player_win"]
        if player.value < dealer.value:
            return OUTCOMES["dealer_win"]
        return OUTCOMES["tie"]