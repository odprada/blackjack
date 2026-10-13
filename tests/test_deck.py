import random

import pytest

from src.classes.card import RANKS, SUITS, Card
from src.classes.deck import Deck


def shuffled(seed: int | None) -> Deck:
    deck = Deck(seed=seed)
    deck.shuffle()
    return deck


# --- a fresh deck ----------------------------------------------------------

def test_new_deck_has_52_cards():
    assert len(Deck()) == 52


def test_new_deck_has_every_rank_and_suit_exactly_once():
    expected = {Card(rank, suit) for suit in SUITS for rank in RANKS}
    deck = Deck()
    assert len(deck.cards) == len(set(deck.cards)) == 52
    assert set(deck.cards) == expected


def test_new_deck_is_not_shuffled_until_asked():
    assert Deck().cards == Deck().cards


# --- draw ------------------------------------------------------------------

def test_draw_returns_the_top_card_and_removes_it():
    deck = Deck()
    top = deck.cards[-1]
    assert deck.draw() == top
    assert len(deck) == 51
    assert top not in deck.cards


def test_draws_are_all_different_cards():
    deck = Deck()
    drawn = [deck.draw() for _ in range(52)]
    assert len(set(drawn)) == 52


def test_drawing_from_an_empty_deck_raises():
    deck = Deck()
    for _ in range(52):
        deck.draw()
    assert len(deck) == 0
    with pytest.raises(IndexError, match="empty"):
        deck.draw()


# --- shuffle and seeds -----------------------------------------------------

def test_shuffle_changes_the_order():
    assert shuffled(1).cards != Deck().cards


def test_shuffle_keeps_the_same_52_cards():
    deck = shuffled(7)
    assert len(deck) == 52
    assert len(set(deck.cards)) == 52
    assert set(deck.cards) == set(Deck().cards)


def test_same_seed_gives_same_order():
    assert shuffled(42).cards == shuffled(42).cards


def test_different_seeds_give_different_orders():
    assert shuffled(1).cards != shuffled(2).cards


def test_unseeded_decks_do_not_all_shuffle_the_same():
    orders = {tuple(shuffled(None).cards) for _ in range(5)}
    assert len(orders) > 1


def test_seed_is_stored():
    assert Deck(seed=42).seed == 42
    assert Deck().seed is None


def test_repeated_shuffles_of_one_deck_are_reproducible():
    first, second = Deck(seed=3), Deck(seed=3)
    for _ in range(3):
        first.shuffle()
        second.shuffle()
    assert first.cards == second.cards


def test_seeded_shuffle_does_not_touch_global_random_state():
    state = random.getstate()
    shuffled(42)
    assert random.getstate() == state


def test_draws_follow_the_seeded_order():
    a, b = shuffled(9), shuffled(9)
    assert [a.draw() for _ in range(5)] == [b.draw() for _ in range(5)]