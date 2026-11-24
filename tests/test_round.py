import pytest

from src.classes.card import Card
from src.classes.deck import Deck
from src.game import round as round_module
from src.game.round import MAX_PLAYERS, OUTCOMES, STAND_VALUE, TARGET, Round
from src.game.seat import TARGET as SEAT_TARGET

WIN = "You win!"
BLACKJACK = "Blackjack!"
LOSS = "Dealer wins"
TIE = "Tie"

Cards = tuple[str, str]


def stacked_deck(*ranks: str) -> Deck:
    """A deck that deals the given ranks in order (the first rank is drawn first)."""
    deck = Deck()
    deck.cards = [Card(rank, "♠") for rank in reversed(ranks)]
    return deck


def rigged_round(players: list[Cards], dealer: Cards, draws: tuple[str, ...] = ()) -> Round:
    """
    Start a round with fixed hands.

    Cards are dealt one at a time around the table: every player's first card, the dealer's
    first card, every player's second card, the dealer's second card. `draws` are the cards
    that come next, in the order they are drawn (player hits and dealer draws share them).
    """
    order = (
        [first for first, _ in players] + [dealer[0]]
        + [second for _, second in players] + [dealer[1]]
        + list(draws)
    )
    return Round(stacked_deck(*order), len(players))


def outcomes(rnd: Round) -> list[str | None]:
    return [rnd.outcome(seat) for seat in rnd.seats]


# --- module contract -------------------------------------------------------

def test_names_used_by_the_gui_are_exported() -> None:
    for name in ("MAX_PLAYERS", "OUTCOMES", "Round", "TARGET"):
        assert hasattr(round_module, name)


def test_target_is_shared_with_seat() -> None:
    assert TARGET == SEAT_TARGET == 21


def test_outcome_messages() -> None:
    assert set(OUTCOMES.values()) == {WIN, BLACKJACK, LOSS, TIE}


# --- dealing ---------------------------------------------------------------

@pytest.mark.parametrize("num_players", range(1, MAX_PLAYERS + 1))
def test_every_seat_and_the_dealer_get_two_cards(num_players: int) -> None:
    deck = Deck()
    rnd = Round(deck, num_players)
    assert len(rnd.seats) == num_players
    assert all(seat.hand.card_number == 2 for seat in rnd.seats)
    assert rnd.dealer_hand.card_number == 2
    assert len(deck) == 52 - 2 * (num_players + 1)


def test_default_is_one_player() -> None:
    assert len(Round(Deck()).seats) == 1


def test_cards_are_dealt_one_at_a_time_around_the_table() -> None:
    rnd = rigged_round([("2", "3"), ("4", "5")], ("6", "7"))
    assert [c.rank for c in rnd.seats[0].hand.cards] == ["2", "3"]
    assert [c.rank for c in rnd.seats[1].hand.cards] == ["4", "5"]
    assert [c.rank for c in rnd.dealer_hand.cards] == ["6", "7"]


def test_seats_are_named_in_turn_order() -> None:
    rnd = Round(Deck(), 3)
    assert [seat.name for seat in rnd.seats] == ["Player 1", "Player 2", "Player 3"]


@pytest.mark.parametrize("num_players", [0, -1, MAX_PLAYERS + 1])
def test_invalid_player_count_raises(num_players: int) -> None:
    with pytest.raises(ValueError, match="between 1 and"):
        Round(Deck(), num_players)


def test_round_starts_on_the_first_seat() -> None:
    rnd = rigged_round([("5", "6"), ("7", "8")], ("9", "7"))
    assert rnd.active_seat is rnd.seats[0]
    assert rnd.current == 0
    assert not rnd.dealer_turn
    assert not rnd.is_over


# --- naturals at the start of the round ------------------------------------

def test_player_with_blackjack_is_skipped() -> None:
    rnd = rigged_round([("A", "K"), ("5", "6")], ("9", "7"))
    assert rnd.active_seat is rnd.seats[1]
    assert not rnd.dealer_turn


def test_if_every_player_has_blackjack_the_dealer_plays_at_once() -> None:
    rnd = rigged_round([("A", "K")], ("9", "7"))
    assert rnd.dealer_turn
    assert rnd.active_seat is None


def test_dealer_blackjack_ends_the_players_turns_at_once() -> None:
    rnd = rigged_round([("5", "6"), ("10", "8")], ("A", "K"))
    assert rnd.dealer_turn
    assert rnd.active_seat is None
    assert rnd.is_over
    assert outcomes(rnd) == [LOSS, LOSS]


# --- hit -------------------------------------------------------------------

def test_hit_gives_the_active_seat_the_next_deck_card() -> None:
    rnd = rigged_round([("5", "6")], ("9", "7"), draws=("2",))
    rnd.hit()
    hand = rnd.seats[0].hand
    assert hand.card_number == 3
    assert hand.cards[-1].rank == "2"
    assert hand.value == 13


def test_hit_without_busting_keeps_the_same_seat_active() -> None:
    rnd = rigged_round([("2", "3"), ("4", "5")], ("9", "7"), draws=("4",))
    rnd.hit()
    assert rnd.active_seat is rnd.seats[0]


def test_hit_that_busts_passes_the_turn() -> None:
    rnd = rigged_round([("10", "6"), ("5", "6")], ("9", "7"), draws=("K",))
    rnd.hit()
    assert rnd.seats[0].bust
    assert rnd.active_seat is rnd.seats[1]


def test_hit_to_21_passes_the_turn_automatically() -> None:
    rnd = rigged_round([("5", "6"), ("2", "3")], ("9", "7"), draws=("10",))
    rnd.hit()
    assert rnd.seats[0].hand.value == 21
    assert rnd.active_seat is rnd.seats[1]


def test_hit_by_the_last_player_busting_starts_the_dealer_turn() -> None:
    rnd = rigged_round([("10", "6")], ("9", "7"), draws=("K",))
    rnd.hit()
    assert rnd.dealer_turn
    assert rnd.active_seat is None


# --- stand -----------------------------------------------------------------

def test_stand_marks_the_seat_and_passes_the_turn() -> None:
    rnd = rigged_round([("10", "8"), ("10", "7")], ("9", "7"))
    first = rnd.seats[0]
    rnd.stand()
    assert first.stood
    assert rnd.active_seat is rnd.seats[1]
    assert not rnd.dealer_turn


def test_stand_does_not_draw_a_card() -> None:
    deck = stacked_deck("10", "9", "8", "7", "2")
    rnd = Round(deck, 1)
    left = len(deck)
    rnd.stand()
    assert len(deck) == left
    assert rnd.seats[0].hand.card_number == 2


def test_players_play_in_seat_order_and_then_the_dealer() -> None:
    rnd = rigged_round([("2", "3"), ("4", "5"), ("6", "7")], ("8", "9"))
    order: list[str] = []
    while (seat := rnd.active_seat) is not None:
        order.append(seat.name)
        rnd.stand()
    assert order == ["Player 1", "Player 2", "Player 3"]
    assert rnd.dealer_turn


def test_hit_and_stand_do_nothing_during_the_dealer_turn() -> None:
    rnd = rigged_round([("10", "8")], ("10", "9"), draws=("5",))
    rnd.stand()
    assert rnd.dealer_turn
    cards_left = len(rnd.deck)

    rnd.hit()
    rnd.stand()

    assert len(rnd.deck) == cards_left
    assert rnd.seats[0].hand.card_number == 2
    assert rnd.dealer_hand.card_number == 2


# --- dealer ----------------------------------------------------------------

def test_dealer_does_not_draw_before_the_players_are_done() -> None:
    rnd = rigged_round([("2", "3")], ("5", "6"))
    assert not rnd.dealer_must_draw
    assert rnd.dealer_step() is False
    assert rnd.dealer_hand.card_number == 2


def test_dealer_must_draw_below_17() -> None:
    rnd = rigged_round([("10", "8")], ("10", "6"))
    rnd.stand()
    assert rnd.dealer_must_draw


@pytest.mark.parametrize("dealer", [
    ("10", "7"),                   # hard 17
    ("A", "6"),                    # soft 17: the dealer stands
    ("K", "Q"),                    # 20
])
def test_dealer_stands_on_17_or_more(dealer: Cards) -> None:
    rnd = rigged_round([("10", "8")], dealer)
    rnd.stand()
    assert STAND_VALUE == 17
    assert not rnd.dealer_must_draw
    rnd.play_dealer()
    assert rnd.dealer_hand.card_number == 2


def test_dealer_step_draws_exactly_one_card_at_a_time() -> None:
    rnd = rigged_round([("10", "8")], ("10", "2"), draws=("3", "K"))
    rnd.stand()
    assert rnd.dealer_step() is True      # 12 -> 15
    assert rnd.dealer_hand.value == 15
    assert rnd.dealer_step() is True      # 15 -> 25, bust
    assert rnd.dealer_hand.value == 25
    assert rnd.dealer_step() is False
    assert rnd.dealer_hand.card_number == 4


def test_play_dealer_draws_until_17_or_more() -> None:
    rnd = rigged_round([("10", "8")], ("10", "2"), draws=("2", "3", "K"))
    rnd.stand()
    rnd.play_dealer()
    assert rnd.dealer_hand.value == 17    # 12 + 2 + 3
    assert rnd.dealer_hand.card_number == 4
    assert len(rnd.deck) == 1             # the K stays in the deck


def test_dealer_with_a_soft_hand_below_17_keeps_drawing() -> None:
    rnd = rigged_round([("10", "8")], ("A", "5"), draws=("10", "2"))
    rnd.stand()
    rnd.play_dealer()
    # soft 16, +10 becomes hard 16, +2 makes 18
    assert rnd.dealer_hand.value == 18
    assert rnd.dealer_hand.card_number == 4


def test_dealer_does_not_draw_when_every_player_busted() -> None:
    rnd = rigged_round([("10", "6")], ("10", "5"), draws=("K", "2"))
    rnd.hit()
    assert not rnd.dealer_must_draw
    rnd.play_dealer()
    assert rnd.dealer_hand.card_number == 2
    assert rnd.is_over


def test_dealer_does_not_draw_when_every_player_has_blackjack() -> None:
    rnd = rigged_round([("A", "K"), ("K", "A")], ("10", "6"), draws=("2",))
    assert rnd.dealer_turn
    assert not rnd.dealer_must_draw
    rnd.play_dealer()
    assert rnd.dealer_hand.card_number == 2


def test_dealer_draws_if_at_least_one_player_is_still_in() -> None:
    rnd = rigged_round([("10", "6"), ("K", "Q")], ("10", "6"), draws=("K", "2"))
    rnd.hit()                             # player 1 busts
    rnd.stand()                           # player 2 stands on 20
    assert rnd.dealer_must_draw
    rnd.play_dealer()
    assert rnd.dealer_hand.value == 18


# --- is_over ---------------------------------------------------------------

def test_round_is_not_over_during_the_players_turns() -> None:
    rnd = rigged_round([("10", "8")], ("10", "9"))
    assert not rnd.is_over


def test_round_is_not_over_while_the_dealer_still_has_to_draw() -> None:
    rnd = rigged_round([("10", "8")], ("10", "6"), draws=("2",))
    rnd.stand()
    assert rnd.dealer_turn
    assert not rnd.is_over


def test_round_is_over_once_the_dealer_is_finished() -> None:
    rnd = rigged_round([("10", "8")], ("10", "6"), draws=("2",))
    rnd.stand()
    rnd.play_dealer()
    assert rnd.is_over


def test_outcome_is_none_until_the_round_is_over() -> None:
    rnd = rigged_round([("10", "8"), ("10", "7")], ("10", "6"), draws=("2",))
    assert outcomes(rnd) == [None, None]
    rnd.stand()
    rnd.stand()
    assert outcomes(rnd) == [None, None]  # dealer has not drawn yet
    rnd.play_dealer()
    assert None not in outcomes(rnd)


# --- outcome: one player ---------------------------------------------------

@pytest.mark.parametrize("player, dealer, actions, draws, expected", [
    pytest.param(("A", "K"), ("K", "Q"), [], (), BLACKJACK, id="blackjack beats 20"),
    pytest.param(("A", "K"), ("A", "Q"), [], (), TIE, id="both blackjack"),
    pytest.param(("K", "Q"), ("A", "K"), [], (), LOSS, id="dealer blackjack beats 20"),
    pytest.param(("10", "6"), ("10", "6"), ["hit"], ("K",), LOSS, id="player bust"),
    pytest.param(("5", "7"), ("10", "6"), ["stand"], ("K",), WIN, id="dealer bust"),
    pytest.param(("10", "9"), ("10", "8"), ["stand"], (), WIN, id="19 beats 18"),
    pytest.param(("10", "8"), ("10", "9"), ["stand"], (), LOSS, id="18 loses to 19"),
    pytest.param(("10", "8"), ("9", "9"), ["stand"], (), TIE, id="18 ties 18"),
    pytest.param(("10", "8"), ("A", "6"), ["stand"], (), WIN, id="dealer stands on soft 17"),
    pytest.param(("K", "Q"), ("10", "6"), ["stand"], ("5",), LOSS, id="dealer draws to 21"),
    pytest.param(("5", "5"), ("K", "Q"), ["hit"], ("A",), WIN, id="three-card 21 beats 20"),
    pytest.param(("5", "5"), ("5", "6"), ["hit"], ("A", "10"), TIE, id="three-card 21 ties 21"),
])
def test_outcome(player: Cards, dealer: Cards, actions: list[str],
                 draws: tuple[str, ...], expected: str) -> None:
    rnd = rigged_round([player], dealer, draws)
    for action in actions:
        getattr(rnd, action)()
    rnd.play_dealer()
    assert rnd.outcome(rnd.seats[0]) == expected


# --- outcome: several players ----------------------------------------------

def test_blackjack_beats_a_dealer_three_card_21() -> None:
    rnd = rigged_round([("A", "K"), ("10", "8")], ("5", "6"), draws=("10",))
    rnd.stand()                           # player 2 stands on 18
    rnd.play_dealer()
    assert rnd.dealer_hand.value == 21 and rnd.dealer_hand.card_number == 3
    assert outcomes(rnd) == [BLACKJACK, LOSS]


def test_a_busted_player_still_loses_when_the_dealer_busts() -> None:
    rnd = rigged_round([("10", "6"), ("10", "8")], ("10", "6"), draws=("K", "K"))
    rnd.hit()                             # player 1 busts
    rnd.stand()                           # player 2 stands on 18
    rnd.play_dealer()
    assert rnd.dealer_hand.value == 26
    assert outcomes(rnd) == [LOSS, WIN]


def test_each_seat_is_compared_with_the_dealer_separately() -> None:
    rnd = rigged_round([("10", "9"), ("10", "8"), ("10", "7")], ("10", "8"))
    for _ in range(3):
        rnd.stand()
    rnd.play_dealer()
    assert outcomes(rnd) == [WIN, TIE, LOSS]


def test_full_table_of_four_players() -> None:
    rnd = rigged_round(
        [("2", "3"), ("2", "4"), ("2", "5"), ("2", "6")], ("10", "7"),
    )
    for _ in range(3):
        rnd.stand()
        assert not rnd.dealer_turn
    rnd.stand()
    assert rnd.dealer_turn
    rnd.play_dealer()
    assert rnd.dealer_hand.card_number == 2
    assert outcomes(rnd) == [LOSS, LOSS, LOSS, LOSS]