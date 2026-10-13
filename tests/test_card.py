import pytest

from src.classes.card import Card
from src.classes.hand import Hand


def make_hand(*ranks: str, is_split: bool = False) -> Hand:
    """Build a hand from ranks only; suit doesn't matter for scoring."""
    return Hand([Card(rank, "♠") for rank in ranks], is_split=is_split)


# --- construction ----------------------------------------------------------

def test_hand_holds_the_given_cards():
    cards = [Card("A", "♠"), Card("K", "♥")]
    assert Hand(cards).cards == cards


def test_empty_hand_raises():
    with pytest.raises(ValueError, match="empty"):
        Hand([])


def test_is_split_defaults_to_false():
    assert Hand([Card("2", "♠")]).is_split is False


def test_is_split_can_be_set():
    assert Hand([Card("2", "♠")], is_split=True).is_split is True


# --- card_number and add_card ----------------------------------------------

def test_card_number():
    assert make_hand("2", "3").card_number == 2
    assert make_hand("2", "3", "4").card_number == 3


def test_add_card_updates_count_and_value():
    hand = make_hand("5", "6")
    hand.add_card(Card("10", "♥"))
    assert hand.card_number == 3
    assert hand.value == 21


def test_add_card_puts_the_card_last():
    hand = make_hand("5", "6")
    new_card = Card("K", "♦")
    hand.add_card(new_card)
    assert hand.cards[-1] == new_card


# --- value -----------------------------------------------------------------

@pytest.mark.parametrize("ranks, expected", [
    (("2", "3"), 5),
    (("K", "Q"), 20),
    (("10", "5", "8"), 23),        # bust, no aces to save it
    (("A", "6"), 17),              # soft 17
    (("A", "6", "10"), 17),        # ace drops to 1 -> hard 17
    (("A", "K"), 21),
    (("A", "A"), 12),              # one ace as 11, one as 1
    (("A", "A", "A"), 13),
    (("A", "A", "9"), 21),
    (("A", "A", "A", "A"), 14),
    (("A", "5", "5", "K"), 21),    # 11+5+5+10 = 31 -> 21
    (("A", "10", "10"), 21),       # three-card 21, not a blackjack
    (("K", "Q", "J"), 30),
])
def test_value(ranks, expected):
    assert make_hand(*ranks).value == expected


def test_add_card_can_bust():
    hand = make_hand("10", "6")
    hand.add_card(Card("K", "♥"))
    assert hand.value == 26


# --- is_soft ---------------------------------------------------------------

@pytest.mark.parametrize("ranks, expected", [
    (("A", "6"), True),
    (("A", "6", "10"), False),     # ace forced down to 1
    (("10", "5"), False),
    (("A", "A"), True),            # one ace still counts as 11
    (("A", "A", "9"), True),
    (("A", "K"), True),
    (("A", "5", "5", "K"), False),
    (("2", "3"), False),
])
def test_is_soft(ranks, expected):
    assert make_hand(*ranks).is_soft is expected


def test_hitting_a_soft_hand_can_turn_it_hard():
    hand = make_hand("A", "6")
    assert hand.is_soft and hand.value == 17
    hand.add_card(Card("10", "♥"))
    assert not hand.is_soft and hand.value == 17


# --- is_blackjack ----------------------------------------------------------

@pytest.mark.parametrize("ranks", [("A", "K"), ("10", "A"), ("A", "Q"), ("J", "A")])
def test_ace_plus_ten_value_card_is_blackjack(ranks):
    assert make_hand(*ranks).is_blackjack


def test_three_card_21_is_not_blackjack():
    hand = make_hand("A", "5", "5")
    assert hand.value == 21
    assert not hand.is_blackjack


def test_two_card_non_21_is_not_blackjack():
    assert not make_hand("10", "9").is_blackjack


def test_split_hand_21_is_not_blackjack():
    hand = make_hand("A", "K", is_split=True)
    assert hand.value == 21
    assert not hand.is_blackjack