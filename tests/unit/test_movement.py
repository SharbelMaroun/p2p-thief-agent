"""Tests for legal movement, barriers, and enumeration (M2-03)."""

import pytest

from p2p_thief_agent.domain.board import Board, OriginCorner
from p2p_thief_agent.domain.coordinates import Action, Coordinate, DomainError
from p2p_thief_agent.domain.movement import cardinal_moves, legal_actions, resolve_move


def test_single_orthogonal_steps_top_left() -> None:
    """Top-left origin: north decreases row, east increases column."""
    board = Board(size=7)
    start = Coordinate(3, 3)

    assert resolve_move(board, start, Action.NORTH) == Coordinate(2, 3)
    assert resolve_move(board, start, Action.SOUTH) == Coordinate(4, 3)
    assert resolve_move(board, start, Action.EAST) == Coordinate(3, 4)
    assert resolve_move(board, start, Action.WEST) == Coordinate(3, 2)


def test_stay_returns_same_cell() -> None:
    """STAY is always legal and yields the same cell."""
    board = Board(size=7)

    assert resolve_move(board, Coordinate(0, 0), Action.STAY) == Coordinate(0, 0)


@pytest.mark.parametrize(
    ("origin", "north", "east"),
    [
        (OriginCorner.TOP_LEFT, Coordinate(2, 3), Coordinate(3, 4)),
        (OriginCorner.BOTTOM_LEFT, Coordinate(4, 3), Coordinate(3, 4)),
        (OriginCorner.TOP_RIGHT, Coordinate(2, 3), Coordinate(3, 2)),
        (OriginCorner.BOTTOM_RIGHT, Coordinate(4, 3), Coordinate(3, 2)),
    ],
)
def test_origin_conventions_change_direction(
    origin: OriginCorner, north: Coordinate, east: Coordinate
) -> None:
    """Direction deltas follow the configured origin corner."""
    board = Board(size=7, origin_corner=origin)
    start = Coordinate(3, 3)

    assert resolve_move(board, start, Action.NORTH) == north
    assert resolve_move(board, start, Action.EAST) == east


def test_off_board_move_rejected() -> None:
    """A step past the edge is illegal."""
    board = Board(size=7)

    with pytest.raises(DomainError):
        resolve_move(board, Coordinate(0, 0), Action.NORTH)


def test_barrier_cell_is_impassable() -> None:
    """A barriered target rejects the move."""
    board = Board(size=7)
    barriers = [Coordinate(2, 3)]

    with pytest.raises(DomainError):
        resolve_move(board, Coordinate(3, 3), Action.NORTH, barriers)


def test_position_off_board_rejected() -> None:
    """Moving from an off-board position is rejected."""
    board = Board(size=5)

    with pytest.raises(DomainError):
        resolve_move(board, Coordinate(9, 9), Action.STAY)


def test_legal_actions_are_deterministic_and_ordered() -> None:
    """Enumeration follows fixed Action order and includes STAY."""
    board = Board(size=7)

    assert legal_actions(board, Coordinate(3, 3)) == [
        Action.NORTH, Action.SOUTH, Action.EAST, Action.WEST, Action.STAY,
    ]


def test_legal_actions_at_corner_drops_off_board_steps() -> None:
    """A top-left corner keeps only south, east, and stay."""
    board = Board(size=7)

    assert legal_actions(board, Coordinate(0, 0)) == [
        Action.SOUTH, Action.EAST, Action.STAY,
    ]


def test_cardinal_moves_exclude_stay() -> None:
    """Cardinal-move enumeration omits STAY for trapping checks."""
    board = Board(size=7)

    assert Action.STAY not in cardinal_moves(board, Coordinate(0, 0))
    assert cardinal_moves(board, Coordinate(0, 0)) == [Action.SOUTH, Action.EAST]
