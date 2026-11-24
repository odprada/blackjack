import dataclasses

import pytest

from src.classes.card import FACE_RANKS, RANKS, SUITS, Card


# --- card_value ------------------------------------------------------------

@pytest.mark.parametrize("rank, expected", [
    ("2", 2), ("3", 3), ("4", 4), ("5", 5), ("6", 6),
    ("7", 7), ("8", 8), ("9", 9), ("10", 10),
])
def test_number_cards_are_worth_their_face_value(rank: str, expected: int) -> None:
    assert Card(rank, "♠").card_value == expected


@pytest.mark.parametrize("rank", ["J", "Q", "K"])
def test_face_cards_are_worth_10(rank: str) -> None:
    assert Card(rank, "♥").card_value == 10


def test_ace_is_worth_11() -> None:
    assert Card("A", "♦").card_value == 11


@pytest.mark.parametrize("suit", SUITS)
def test_value_does_not_depend_on_suit(suit: str) -> None:
    assert Card("K", suit).card_value == 10
    assert Card("7", suit).card_value == 7


# --- validation ------------------------------------------------------------

@pytest.mark.parametrize("rank", ["1", "0", "11", "a", "k", "Joker", "", " A"])
def test_invalid_rank_raises(rank: str) -> None:
    with pytest.raises(ValueError, match="Invalid rank"):
        Card(rank, "♠")


def test_non_string_rank_raises() -> None:
    with pytest.raises(ValueError, match="Invalid rank"):
        Card(10, "♠")  # type: ignore[arg-type]


@pytest.mark.parametrize("suit", ["S", "x", "", "♠♠"])
def test_invalid_suit_raises(suit: str) -> None:
    with pytest.raises(ValueError, match="Invalid suit"):
        Card("A", suit)


def test_every_rank_and_suit_combination_is_valid() -> None:
    cards = {Card(rank, suit) for rank in RANKS for suit in SUITS}
    assert len(cards) == 52


def test_constants_describe_a_standard_deck() -> None:
    assert len(RANKS) == 13
    assert len(SUITS) == 4
    assert set(FACE_RANKS) <= set(RANKS)


# --- equality, hashing, immutability, str ----------------------------------

def test_cards_with_the_same_rank_and_suit_are_equal() -> None:
    assert Card("A", "♠") == Card("A", "♠")


def test_cards_with_a_different_rank_or_suit_are_not_equal() -> None:
    assert Card("A", "♠") != Card("A", "♥")
    assert Card("A", "♠") != Card("K", "♠")


def test_equal_cards_hash_the_same() -> None:
    assert len({Card("Q", "♦"), Card("Q", "♦")}) == 1


def test_card_is_immutable() -> None:
    card = Card("K", "♣")
    with pytest.raises(dataclasses.FrozenInstanceError):
        card.rank = "A"  # type: ignore[misc]


def test_str_is_rank_followed_by_suit() -> None:
    assert str(Card("A", "♠")) == "A♠"
    assert str(Card("10", "♥")) == "10♥"