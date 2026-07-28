"""Public barrier declarations and their official placement rules (`AE-015`).

The Thief validates disclosed barrier placements with the same official rules the
Police must follow. Per the project book Chapter 3.4 (PDF p.37 / printed p.21), the
Police may give up movement to place a barrier either on the Police's current cell or
on one orthogonally adjacent cell. Validation is pure and takes the Police's auditable
position explicitly; it holds no Cop-private truth. A placed barrier permanently
blocks movement for both players. This pure API validates a disclosed placement only;
the barrier-replaces-movement turn rule is enforced later by the turn state machine.
Barrier-on-Thief capture is evaluated in `capture`.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field, replace

from p2p_thief_agent.domain.board import Board, is_orthogonal_step
from p2p_thief_agent.domain.coordinates import Coordinate, DomainError

# Appendix F Table 15 barrier quota (MINIMUM status, `AF-015`).
DEFAULT_BARRIER_QUOTA = 14


@dataclass(frozen=True, slots=True)
class BarrierField:
    """An immutable set of disclosed barriers with a placement quota."""

    cells: frozenset[Coordinate] = field(default_factory=frozenset)
    quota: int = DEFAULT_BARRIER_QUOTA

    def __post_init__(self) -> None:
        """Validate the quota and normalize the barrier set."""
        if isinstance(self.quota, bool) or not isinstance(self.quota, int):
            raise DomainError(f"quota must be an integer, got {type(self.quota).__name__}")
        if self.quota < 0:
            raise DomainError(f"quota must be nonnegative, got {self.quota}")
        object.__setattr__(self, "cells", frozenset(self.cells))
        if len(self.cells) > self.quota:
            raise DomainError("barrier count exceeds quota")

    def blocks(self, cell: Coordinate) -> bool:
        """Return whether a cell is permanently barriered."""
        return cell in self.cells

    def place(self, board: Board, police_position: Coordinate, cell: Coordinate) -> BarrierField:
        """Validate one disclosed placement and return the extended field."""
        validate_barrier_placement(board, police_position, cell, self)
        return replace(self, cells=self.cells | {cell})


def validate_barrier_placement(
    board: Board,
    police_position: Coordinate,
    cell: Coordinate,
    existing: BarrierField | Iterable[Coordinate] = (),
    quota: int = DEFAULT_BARRIER_QUOTA,
) -> Coordinate:
    """Return the cell if the disclosed placement is legal, else raise."""
    if isinstance(existing, BarrierField):
        placed, quota = existing.cells, existing.quota
    else:
        placed = frozenset(existing)
    board.validate_position(cell)
    board.validate_position(police_position)
    if cell != police_position and not is_orthogonal_step(police_position, cell):
        raise DomainError(
            "barrier must be on the Police's own cell or one orthogonal step away"
        )
    if cell in placed:
        raise DomainError(f"barrier already declared at {cell.to_list()}")
    if len(placed) >= quota:
        raise DomainError(f"barrier quota {quota} is exhausted")
    return cell
