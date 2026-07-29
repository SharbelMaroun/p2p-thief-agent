"""Thief-local record of publicly disclosed barriers with provenance.

A barrier becomes known only when it is disclosed in public protocol traffic. This
record stores each known barrier cell together with the step at which the Thief learned
it, so local reasoning and later audit can explain provenance. It holds no Cop-private
truth: it never stores the Police position or an unobserved barrier, only cells the
Thief has been told about. It is immutable -- recording a disclosure returns a new
record -- every cell is validated on-board, and the earliest disclosure step is kept.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate, DomainError, _validate_index


def _entry_key(entry: tuple[Coordinate, int]) -> tuple[int, int]:
    """Order entries by cell row then column for stable, hashable state."""
    cell, _ = entry
    return (cell.row, cell.col)


@dataclass(frozen=True, slots=True)
class KnownBarriers:
    """An immutable map of known barrier cells to their disclosure step."""

    items: tuple[tuple[Coordinate, int], ...] = ()

    def __post_init__(self) -> None:
        """Deduplicate by cell keeping the earliest step, then order deterministically."""
        earliest: dict[Coordinate, int] = {}
        for cell, step in self.items:
            if not isinstance(cell, Coordinate):
                raise DomainError(f"barrier cell must be a Coordinate, got {type(cell).__name__}")
            _validate_index("step", step)
            if step < 0:
                raise DomainError(f"disclosure step must be nonnegative, got {step}")
            if cell not in earliest or step < earliest[cell]:
                earliest[cell] = step
        ordered = tuple(sorted(earliest.items(), key=_entry_key))
        object.__setattr__(self, "items", ordered)

    @property
    def cells(self) -> frozenset[Coordinate]:
        """Return the set of known barrier cells."""
        return frozenset(cell for cell, _ in self.items)

    def blocks(self, cell: Coordinate) -> bool:
        """Return whether a cell is a known barrier."""
        return any(known == cell for known, _ in self.items)

    def disclosed_at(self, cell: Coordinate) -> int | None:
        """Return the step a cell was first disclosed, or None if unknown."""
        for known, step in self.items:
            if known == cell:
                return step
        return None

    def record(self, board: Board, cell: Coordinate, *, step: int) -> KnownBarriers:
        """Return a new record including a disclosed on-board barrier.

        A cell already known keeps its earliest disclosure step; re-recording it is a
        no-op that returns an equal record.
        """
        board.validate_position(cell)
        _validate_index("step", step)
        return KnownBarriers(self.items + ((cell, step),))

    def record_all(
        self, board: Board, cells: Iterable[Coordinate], *, step: int
    ) -> KnownBarriers:
        """Return a new record including several barriers disclosed at one step."""
        additions = tuple((board.validate_position(cell), step) for cell in cells)
        return KnownBarriers(self.items + additions)
