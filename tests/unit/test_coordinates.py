"""Tests for immutable coordinates and fixed action tokens (M2-01)."""

from dataclasses import FrozenInstanceError

import pytest

from p2p_thief_agent.domain.coordinates import Action, Coordinate, DomainError


def test_coordinate_is_immutable_and_hashable() -> None:
    """Coordinates are frozen and usable as set/dict keys."""
    cell = Coordinate(3, 3)

    assert {cell: 1}[Coordinate(3, 3)] == 1
    with pytest.raises(FrozenInstanceError):
        cell.row = 4  # type: ignore[misc]


def test_coordinate_preserves_row_column_order() -> None:
    """Serialization keeps confirmed row-then-column order."""
    assert Coordinate(1, 2).to_list() == [1, 2]
    assert Coordinate.from_pair([4, 5]) == Coordinate(4, 5)
    assert Coordinate.from_pair((6, 7)) == Coordinate(6, 7)


@pytest.mark.parametrize("bad", [True, False])
def test_coordinate_rejects_booleans(bad: object) -> None:
    """Booleans are not accepted as integer indices."""
    with pytest.raises(DomainError):
        Coordinate(bad, 0)  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", [1.0, "1", None, 2.5])
def test_coordinate_rejects_non_integers(bad: object) -> None:
    """Floats, strings, and None are rejected."""
    with pytest.raises(DomainError):
        Coordinate(0, bad)  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", ["ab", b"ab", [1], [1, 2, 3], 5, {1, 2}])
def test_from_pair_rejects_malformed_pairs(bad: object) -> None:
    """Only two-item lists/tuples are accepted as pairs."""
    with pytest.raises(DomainError):
        Coordinate.from_pair(bad)


@pytest.mark.parametrize(
    ("token", "action"),
    [("N", Action.NORTH), ("S", Action.SOUTH), ("E", Action.EAST), ("W", Action.WEST),
     ("STAY", Action.STAY)],
)
def test_action_parses_exact_tokens(token: str, action: Action) -> None:
    """Each exact token maps to its action."""
    assert Action.parse(token) is action


@pytest.mark.parametrize("bad", ["n", "north", "", "NN", "stay", True, 1, None])
def test_action_rejects_unknown_or_nonstring_tokens(bad: object) -> None:
    """Unknown tokens, wrong case, booleans, and non-strings reject."""
    with pytest.raises(DomainError):
        Action.parse(bad)
