import pytest

from src.classes.card import Card
from src.classes.hand import Hand
from src.game.seat import TARGET, Seat


def make_seat(*ranks: str, stood: bool = False) -> Seat:
    """Build a seat from ranks only; suit doesn't matter for scoring."""
    return Seat("Player 1", Hand([Card(rank, "♠") for rank in ranks]), stood=stood)


# --- construction ----------------------------------------------------------

def test_target_is_21() -> None:
    assert TARGET == 21


def test_seat_keeps_its_name_and_hand() -> None:
    hand = Hand([Card("2", "♠"), Card("3", "♥")])
    seat = Seat("Alice", hand)
    assert seat.name == "Alice"
    assert seat.hand is hand


def test_seat_has_not_stood_by_default() -> None:
    assert make_seat("2", "3").stood is False


# --- bust ------------------------------------------------------------------

@pytest.mark.parametrize("ranks, expected", [
    (("10", "10"), False),         # 20
    (("10", "6", "5"), False),     # exactly 21 is not a bust
    (("A", "K"), False),           # blackjack
    (("A", "6", "10"), False),     # ace drops to 1 -> 17
    (("A", "A", "K"), False),      # 12
    (("10", "10", "2"), True),     # 22
    (("10", "5", "8"), True),      # 23, no ace to save it
    (("10", "6", "K"), True),      # 26
])
def test_bust(ranks: tuple[str, ...], expected: bool) -> None:
    assert make_seat(*ranks).bust is expected


# --- done ------------------------------------------------------------------

def test_open_hand_that_has_not_stood_is_not_done() -> None:
    assert not make_seat("10", "5").done


def test_stood_seat_is_done() -> None:
    assert make_seat("10", "5", stood=True).done


def test_standing_later_makes_the_seat_done() -> None:
    seat = make_seat("10", "5")
    assert not seat.done
    seat.stood = True
    assert seat.done


def test_bust_seat_is_done() -> None:
    assert make_seat("10", "6", "K").done


@pytest.mark.parametrize("ranks", [
    ("A", "K"),                    # blackjack
    ("5", "6", "10"),              # three-card 21
    ("A", "5", "5"),               # soft 21 reached with three cards
])
def test_seat_on_21_is_done(ranks: tuple[str, ...]) -> None:
    assert make_seat(*ranks).done


def test_seat_on_20_is_not_done() -> None:
    assert not make_seat("K", "Q").done


def test_adding_a_card_can_finish_the_seat() -> None:
    seat = make_seat("10", "6")
    assert not seat.done
    seat.hand.add_card(Card("K", "♥"))
    assert seat.done and seat.bust


# --- live ------------------------------------------------------------------

@pytest.mark.parametrize("ranks", [
    ("10", "7"),
    ("K", "Q"),
    ("5", "6", "10"),              # three-card 21 is not a blackjack, so it is live
])
def test_normal_hand_is_live(ranks: tuple[str, ...]) -> None:
    assert make_seat(*ranks).live


def test_bust_seat_is_not_live() -> None:
    assert not make_seat("10", "6", "K").live


def test_blackjack_seat_is_not_live() -> None:
    assert not make_seat("A", "K").live


def test_standing_does_not_change_whether_a_seat_is_live() -> None:
    assert make_seat("10", "2", stood=True).live
    assert not make_seat("10", "6", "K", stood=True).live