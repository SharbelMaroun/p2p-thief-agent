"""Immutable coordinates and the five fixed action tokens.

These types encode only Appendix E/F CONFIRMED rules and hold no Cop-private truth.
Coordinates preserve row/column order for JSON round-tripping (`AF-015`, `AF-013`).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DomainError(ValueError):
    """Raised when a value violates the confirmed official domain rules."""


class Action(Enum):
    """The five fixed movement tokens; diagonals are illegal (`AF-015`)."""

    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"
    STAY = "STAY"

    @classmethod
    def parse(cls, token: object) -> Action:
        """Return the action for an exact token, rejecting anything else."""
        if not isinstance(token, str):
            raise DomainError(f"action token must be a string, got {type(token).__name__}")
        try:
            return cls(token)
        except ValueError as exc:
            raise DomainError(f"unknown action token: {token!r}") from exc


def _validate_index(name: str, value: object) -> int:
    """Require a real integer index, rejecting booleans and floats."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise DomainError(f"{name} must be an integer, got {type(value).__name__}")
    return value


@dataclass(frozen=True, slots=True)
class Coordinate:
    """An immutable, hashable (row, column) grid cell."""

    row: int
    col: int

    def __post_init__(self) -> None:
        """Reject booleans, floats, and any non-integer row/column."""
        _validate_index("row", self.row)
        _validate_index("col", self.col)

    @classmethod
    def from_pair(cls, pair: object) -> Coordinate:
        """Build a coordinate from an ordered [row, col] list or tuple."""
        if isinstance(pair, (str, bytes)) or not isinstance(pair, (list, tuple)):
            raise DomainError(f"coordinate pair must be a list or tuple, got {type(pair).__name__}")
        if len(pair) != 2:
            raise DomainError(f"coordinate pair must have exactly two items, got {len(pair)}")
        row, col = pair
        return cls(row, col)

    def to_list(self) -> list[int]:
        """Serialize in confirmed row-then-column JSON order."""
        return [self.row, self.col]
