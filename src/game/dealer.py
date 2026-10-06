from ..classes.deck import Deck
from ..classes.hand import Hand

deck = Deck()

def dealer_play(deck: Deck) -> Hand:
    """Dealer stands on 17"""
    hand = Hand([deck.draw(), deck.draw()])

    while hand.value < 17:
        hand.add_card(deck.draw())

    return hand