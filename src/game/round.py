from dataclasses import dataclass, field
    
from ..classes.deck import Deck
from ..classes.hand import Hand

OUTCOMES = {
    "player_win": "You win!",
    "player_blackjack": "Blackjack!",
    "dealer_win": "Dealer wins",
    "tie": "Tie",
}

stand_value = 17
bust_value = 21

@dataclass
class Round:
    """
    Game logic of a single round.

    Attributes:
        deck: Deck used for the game.
        player_hand: The player's hand.
        dealer_hand: The dealer's hand.
        player_stood: Whether the player has ended their turn.

    Properties:
        player_bust: Indicates whether the player's hand is over 21.
        is_over: Indicates whether the round has ended.
        outcome: Indicates who won through a string, or None while the round is still going.

    The dealer stands on all 17s (as opposed to hitting on soft 17s like in some rulesets).
    """

    deck: Deck
    player_hand: Hand = field(init=False)
    dealer_hand: Hand = field(init=False)
    player_stood: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        self.player_hand = Hand([self.deck.draw(), self.deck.draw()])
        self.dealer_hand = Hand([self.deck.draw(), self.deck.draw()])

    @property
    def player_bust(self) -> bool:
        return self.player_hand.value > bust_value

    @property
    def is_over(self) -> bool:
        return (
            self.player_hand.is_blackjack
            or self.dealer_hand.is_blackjack
            or self.player_bust
            or self.player_stood
        )

    @property
    def outcome(self) -> str | None:
        if not self.is_over:
            return None
 
        player, dealer = self.player_hand, self.dealer_hand
 
        if player.is_blackjack or dealer.is_blackjack:
            if player.is_blackjack and dealer.is_blackjack:
                return OUTCOMES["tie"]
            return OUTCOMES["player_blackjack"] if player.is_blackjack else OUTCOMES["dealer_win"]
        if self.player_bust:
            return OUTCOMES["dealer_win"]
        if dealer.value > 21 or player.value > dealer.value:
            return OUTCOMES["player_win"]
        if player.value < dealer.value:
            return OUTCOMES["dealer_win"]
        return OUTCOMES["tie"]

    def hit(self) -> None:
        if self.is_over:
            return
        self.player_hand.add_card(self.deck.draw())

    def stand(self) -> None:
        if self.is_over:
            return
        self.player_stood = True
        while self.dealer_hand.value < stand_value:
            self.dealer_hand.add_card(self.deck.draw())