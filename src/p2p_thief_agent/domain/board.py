"""Configured square board geometry and origin-independent adjacency.

Bounds and start positions follow the configured grid size, origin corner, and axis
start index (`AF-013`). Orthogonal adjacency does not depend on the origin corner.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from p2p_thief_agent.domain.coordinates import Coordinate, DomainError, _validate_index

# Origin-independent orthogonal steps in (row, col) form.
_ORTHOGONAL_STEPS = ((-1, 0), (1, 0), (0, 1), (0, -1))


class OriginCorner(Enum):
    """Supported axis-origin conventions (`AF-013` negotiated default is top-left)."""

    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"


@dataclass(frozen=True, slots=True)
class Board:
    """An immutable square grid with configurable origin and start index."""

    size: int
    origin_corner: OriginCorner = OriginCorner.TOP_LEFT
    axis_start_index: int = 0

    def __post_init__(self) -> None:
        """Validate the configured size and start index."""
        _validate_index("size", self.size)
        _validate_index("axis_start_index", self.axis_start_index)
        if self.size < 1:
            raise DomainError(f"grid size must be at least 1, got {self.size}")
        if not isinstance(self.origin_corner, OriginCorner):
            raise DomainError("origin_corner must be an OriginCorner")

    @property
    def min_index(self) -> int:
        """Inclusive lowest valid row/column index."""
        return self.axis_start_index

    @property
    def max_index(self) -> int:
        """Inclusive highest valid row/column index."""
        return self.axis_start_index + self.size - 1

    def contains(self, cell: Coordinate) -> bool:
        """Return whether a cell lies within the inclusive board bounds."""
        return (
            self.min_index <= cell.row <= self.max_index
            and self.min_index <= cell.col <= self.max_index
        )

    def validate_position(self, cell: Coordinate) -> Coordinate:
        """Return the cell if on-board, else raise a domain error."""
        if not self.contains(cell):
            raise DomainError(f"position {cell.to_list()} is outside the board")
        return cell

    def orthogonal_neighbors(self, cell: Coordinate) -> list[Coordinate]:
        """Return the four orthogonal cells in deterministic order (may be off-board)."""
        return [Coordinate(cell.row + dr, cell.col + dc) for dr, dc in _ORTHOGONAL_STEPS]


def is_orthogonal_step(source: Coordinate, target: Coordinate) -> bool:
    """Return whether target is exactly one orthogonal cell from source."""
    return abs(source.row - target.row) + abs(source.col - target.col) == 1
