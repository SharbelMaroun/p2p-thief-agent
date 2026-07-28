"""Tests for square board geometry and adjacency (M2-02)."""

import pytest

from p2p_thief_agent.domain.board import Board, OriginCorner, is_orthogonal_step
from p2p_thief_agent.domain.coordinates import Coordinate, DomainError


def test_default_board_bounds_are_inclusive() -> None:
    """A size-7 top-left board spans indices 0..6 inclusive."""
    board = Board(size=7)

    assert board.min_index == 0
    assert board.max_index == 6
    assert board.contains(Coordinate(0, 0))
    assert board.contains(Coordinate(6, 6))
    assert not board.contains(Coordinate(7, 0))
    assert not board.contains(Coordinate(-1, 0))


def test_axis_start_index_shifts_bounds() -> None:
    """A one-based board spans indices 1..7 inclusive."""
    board = Board(size=7, axis_start_index=1)

    assert board.min_index == 1
    assert board.max_index == 7
    assert not board.contains(Coordinate(0, 0))
    assert board.contains(Coordinate(7, 7))


@pytest.mark.parametrize("origin", list(OriginCorner))
def test_all_origin_conventions_share_cell_set(origin: OriginCorner) -> None:
    """Origin corner does not change which cells exist on a square board."""
    board = Board(size=3, origin_corner=origin)

    assert board.contains(Coordinate(0, 0))
    assert board.contains(Coordinate(2, 2))
    assert not board.contains(Coordinate(3, 3))


def test_validate_position_rejects_off_board() -> None:
    """validate_position raises for a cell outside the bounds."""
    board = Board(size=5)

    assert board.validate_position(Coordinate(2, 2)) == Coordinate(2, 2)
    with pytest.raises(DomainError):
        board.validate_position(Coordinate(5, 5))


@pytest.mark.parametrize("bad_size", [0, -1])
def test_board_rejects_nonpositive_size(bad_size: int) -> None:
    """Grid size must be at least one."""
    with pytest.raises(DomainError):
        Board(size=bad_size)


@pytest.mark.parametrize("bad", [True, 1.0, "7"])
def test_board_rejects_non_integer_size(bad: object) -> None:
    """Size must be a real integer, not a bool/float/string."""
    with pytest.raises(DomainError):
        Board(size=bad)  # type: ignore[arg-type]


def test_board_rejects_non_origin_corner() -> None:
    """origin_corner must be an OriginCorner value."""
    with pytest.raises(DomainError):
        Board(size=7, origin_corner="top-left")  # type: ignore[arg-type]


def test_orthogonal_neighbors_are_deterministic() -> None:
    """Neighbors are returned N,S,E,W in row/col form regardless of board edges."""
    board = Board(size=7)

    assert board.orthogonal_neighbors(Coordinate(3, 3)) == [
        Coordinate(2, 3), Coordinate(4, 3), Coordinate(3, 4), Coordinate(3, 2),
    ]


def test_is_orthogonal_step() -> None:
    """Exactly one orthogonal cell counts as a step; diagonals and self do not."""
    origin = Coordinate(2, 2)

    assert is_orthogonal_step(origin, Coordinate(2, 3))
    assert is_orthogonal_step(origin, Coordinate(1, 2))
    assert not is_orthogonal_step(origin, Coordinate(3, 3))
    assert not is_orthogonal_step(origin, Coordinate(2, 2))
    assert not is_orthogonal_step(origin, Coordinate(2, 4))
