"""Capture evaluation with deterministic precedence (`AE-046`).

Three official capture conditions are recognized. When more than one holds at once,
precedence is fixed: same-cell, then barrier-on-Thief, then trapped. STAY is not a
cardinal escape, so a Thief whose four cardinal neighbors are all unavailable is
captured even though STAY remains a nominal action.
"""

from __future__ import annotations

from collections.abc import Iterable
from enum import Enum

from p2p_thief_agent.domain.barriers import BarrierField
from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate


class CaptureReason(Enum):
    """The recognized capture causes, in precedence order."""

    SAME_CELL = "same_cell"
    BARRIER_ON_THIEF = "barrier_on_thief"
    TRAPPED = "trapped"


def _as_field(barriers: BarrierField | Iterable[Coordinate]) -> BarrierField:
    """Normalize barrier input to a BarrierField."""
    if isinstance(barriers, BarrierField):
        return barriers
    cells = frozenset(barriers)
    return BarrierField(cells, quota=len(cells))


def is_trapped(
    board: Board,
    thief: Coordinate,
    barriers: BarrierField | Iterable[Coordinate] = (),
) -> bool:
    """Return whether every cardinal neighbor is off-board or barriered."""
    board.validate_position(thief)
    field = _as_field(barriers)
    for neighbor in board.orthogonal_neighbors(thief):
        if board.contains(neighbor) and not field.blocks(neighbor):
            return False
    return True


def evaluate_capture(
    board: Board,
    thief: Coordinate,
    police: Coordinate,
    barriers: BarrierField | Iterable[Coordinate] = (),
) -> CaptureReason | None:
    """Return the highest-precedence capture reason, or None if uncaptured."""
    board.validate_position(thief)
    board.validate_position(police)
    field = _as_field(barriers)
    if thief == police:
        return CaptureReason.SAME_CELL
    if field.blocks(thief):
        return CaptureReason.BARRIER_ON_THIEF
    if is_trapped(board, thief, field):
        return CaptureReason.TRAPPED
    return None


def is_captured(
    board: Board,
    thief: Coordinate,
    police: Coordinate,
    barriers: BarrierField | Iterable[Coordinate] = (),
) -> bool:
    """Return whether any capture condition holds."""
    return evaluate_capture(board, thief, police, barriers) is not None
