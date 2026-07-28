"""Tests for capture conditions and precedence (M2-05)."""

import pytest

from p2p_thief_agent.domain.barriers import BarrierField
from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.capture import (
    CaptureReason,
    evaluate_capture,
    is_captured,
    is_trapped,
)
from p2p_thief_agent.domain.coordinates import Coordinate, DomainError

BOARD = Board(size=7)


def test_same_cell_capture() -> None:
    """Police and Thief on the same cell is a capture."""
    cell = Coordinate(3, 3)

    assert evaluate_capture(BOARD, cell, cell) is CaptureReason.SAME_CELL
    assert is_captured(BOARD, cell, cell)


def test_barrier_on_thief_capture() -> None:
    """A barrier on the Thief's own cell is a capture."""
    thief = Coordinate(3, 3)
    barriers = BarrierField(frozenset({thief}), quota=1)

    assert evaluate_capture(BOARD, thief, Coordinate(0, 0), barriers) is (
        CaptureReason.BARRIER_ON_THIEF
    )


def test_trapped_by_board_edges_and_barriers() -> None:
    """A corner Thief with both interior neighbors barriered is trapped."""
    thief = Coordinate(0, 0)
    barriers = BarrierField(frozenset({Coordinate(1, 0), Coordinate(0, 1)}), quota=2)

    assert is_trapped(BOARD, thief, barriers)
    assert evaluate_capture(BOARD, thief, Coordinate(6, 6), barriers) is CaptureReason.TRAPPED


def test_stay_does_not_rescue_trapped_thief() -> None:
    """All four cardinal neighbors unavailable is a capture despite STAY existing."""
    thief = Coordinate(3, 3)
    walls = frozenset(
        {Coordinate(2, 3), Coordinate(4, 3), Coordinate(3, 4), Coordinate(3, 2)}
    )
    barriers = BarrierField(walls, quota=4)

    assert is_trapped(BOARD, thief, barriers)
    assert is_captured(BOARD, thief, Coordinate(0, 0), barriers)


def test_open_thief_is_not_captured() -> None:
    """A Thief with a free neighbor and no other condition is uncaptured."""
    assert evaluate_capture(BOARD, Coordinate(3, 3), Coordinate(0, 0)) is None
    assert not is_captured(BOARD, Coordinate(3, 3), Coordinate(0, 0))


def test_one_open_neighbor_prevents_trapping() -> None:
    """A single free cardinal neighbor means the Thief is not trapped."""
    thief = Coordinate(3, 3)
    walls = frozenset({Coordinate(2, 3), Coordinate(4, 3), Coordinate(3, 4)})
    barriers = BarrierField(walls, quota=3)

    assert not is_trapped(BOARD, thief, barriers)


def test_precedence_same_cell_over_barrier_and_trapped() -> None:
    """Same-cell wins when barrier-on-Thief and trapping also hold."""
    thief = Coordinate(0, 0)
    walls = frozenset({Coordinate(0, 0), Coordinate(1, 0), Coordinate(0, 1)})
    barriers = BarrierField(walls, quota=3)

    assert evaluate_capture(BOARD, thief, thief, barriers) is CaptureReason.SAME_CELL


def test_precedence_barrier_over_trapped() -> None:
    """Barrier-on-Thief wins over trapping when both hold."""
    thief = Coordinate(0, 0)
    walls = frozenset({Coordinate(0, 0), Coordinate(1, 0), Coordinate(0, 1)})
    barriers = BarrierField(walls, quota=3)

    assert evaluate_capture(BOARD, thief, Coordinate(6, 6), barriers) is (
        CaptureReason.BARRIER_ON_THIEF
    )


def test_capture_accepts_plain_iterable_barriers() -> None:
    """Barrier inputs may be a plain iterable of coordinates."""
    thief = Coordinate(3, 3)

    assert evaluate_capture(BOARD, thief, Coordinate(0, 0), [thief]) is (
        CaptureReason.BARRIER_ON_THIEF
    )


def test_is_trapped_rejects_off_board_thief() -> None:
    """An off-board Thief cannot be reported as trapped."""
    with pytest.raises(DomainError):
        is_trapped(BOARD, Coordinate(9, 9))


@pytest.mark.parametrize(
    ("thief", "police"),
    [
        (Coordinate(9, 9), Coordinate(0, 0)),
        (Coordinate(0, 0), Coordinate(9, 9)),
    ],
)
def test_evaluate_capture_rejects_off_board_players(
    thief: Coordinate, police: Coordinate
) -> None:
    """Capture evaluation requires both player positions to be on-board."""
    with pytest.raises(DomainError):
        evaluate_capture(BOARD, thief, police)
