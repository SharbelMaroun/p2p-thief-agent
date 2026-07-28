"""Tests for public barrier declaration rules (M2-04)."""

import pytest

from p2p_thief_agent.domain.barriers import (
    BarrierField,
    validate_barrier_placement,
)
from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate, DomainError

BOARD = Board(size=7)
POLICE = Coordinate(3, 3)


@pytest.mark.parametrize(
    "cell",
    [Coordinate(2, 3), Coordinate(4, 3), Coordinate(3, 4), Coordinate(3, 2)],
)
def test_valid_placement_is_one_orthogonal_step(cell: Coordinate) -> None:
    """A cell one orthogonal step from the Police is a legal placement."""
    assert validate_barrier_placement(BOARD, POLICE, cell) == cell


def test_placement_off_board_rejected() -> None:
    """A barrier past the edge is illegal even if adjacent to the Police."""
    with pytest.raises(DomainError):
        validate_barrier_placement(BOARD, Coordinate(0, 0), Coordinate(-1, 0))


def test_placement_on_police_cell_rejected() -> None:
    """A barrier on the Police's own cell is illegal."""
    with pytest.raises(DomainError):
        validate_barrier_placement(BOARD, POLICE, POLICE)


@pytest.mark.parametrize("cell", [Coordinate(4, 4), Coordinate(3, 5), Coordinate(1, 3)])
def test_non_adjacent_or_diagonal_rejected(cell: Coordinate) -> None:
    """Diagonal and multi-cell placements are illegal."""
    with pytest.raises(DomainError):
        validate_barrier_placement(BOARD, POLICE, cell)


def test_duplicate_placement_rejected() -> None:
    """A barrier already declared cannot be declared again."""
    existing = BarrierField(frozenset({Coordinate(2, 3)}))
    with pytest.raises(DomainError):
        validate_barrier_placement(BOARD, POLICE, Coordinate(2, 3), existing)


def test_quota_exhaustion_rejected() -> None:
    """Placement fails once the quota is reached."""
    existing = BarrierField(frozenset({Coordinate(0, 1)}), quota=1)
    with pytest.raises(DomainError):
        validate_barrier_placement(BOARD, POLICE, Coordinate(2, 3), existing)


def test_place_extends_field_immutably() -> None:
    """place returns a new field and leaves the original unchanged."""
    field = BarrierField(quota=3)
    extended = field.place(BOARD, POLICE, Coordinate(2, 3))

    assert extended.blocks(Coordinate(2, 3))
    assert not field.blocks(Coordinate(2, 3))
    assert len(field.cells) == 0


def test_barrier_field_rejects_overfilled_construction() -> None:
    """A field cannot be built with more barriers than its quota."""
    with pytest.raises(DomainError):
        BarrierField(frozenset({Coordinate(0, 0), Coordinate(0, 1)}), quota=1)


@pytest.mark.parametrize("bad", [True, 1.0, "5"])
def test_barrier_field_rejects_non_integer_quota(bad: object) -> None:
    """Quota must be a real integer."""
    with pytest.raises(DomainError):
        BarrierField(quota=bad)  # type: ignore[arg-type]


def test_barrier_field_rejects_negative_quota() -> None:
    """A negative quota is invalid."""
    with pytest.raises(DomainError):
        BarrierField(quota=-1)


def test_barrier_permanently_blocks_movement() -> None:
    """A placed barrier blocks the Thief's move into that cell."""
    from p2p_thief_agent.domain.coordinates import Action
    from p2p_thief_agent.domain.movement import resolve_move

    field = BarrierField(quota=3).place(BOARD, POLICE, Coordinate(2, 3))
    with pytest.raises(DomainError):
        resolve_move(BOARD, Coordinate(1, 3), Action.SOUTH, field.cells)
