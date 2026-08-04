"""Consume and produce the public scent observation on the wire (`M6-002`).

The scent a peer shares is the `smell_grid` field of a `TurnMessage`: a sparse map
`{"r,c": intensity}` (`SIM_WIRE_PROTOCOL.md`). This module is the boundary between that
wire shape and the `(row, col) -> intensity` map the belief layer works with. Emission
physics live in `scent.py`; this module only (de)serialises.

Only occupied cells travel: an unseen cell is **absent, not zero** (`M6-006a`), so an
empty observation is an empty object rather than a zero-filled grid. Parsing is
order-independent and encoding emits keys in a deterministic `(row, col)` order, so the
same field always serialises the same way.

Off-board rejection needs the negotiated grid size and is `M6-006b`; here the checks are
shape and sign only — a key must be `"int,int"` with non-negative coordinates and a
non-negative numeric intensity.
"""

from __future__ import annotations

from collections.abc import Mapping

Cell = tuple[int, int]


class ObservationError(ValueError):
    """Raised when a `smell_grid` is malformed on the wire."""


def parse_smell_grid(smell_grid: object) -> dict[Cell, float]:
    """Parse an inbound `{"r,c": intensity}` map into `(row, col) -> intensity`.

    Order-independent: the same cells parse to the same map whatever order they arrive
    in. A malformed key or a non-numeric/negative intensity is rejected by name.
    """
    if not isinstance(smell_grid, Mapping):
        raise ObservationError('smell_grid must be an object of {"r,c": intensity}')
    return {_parse_key(key): _parse_intensity(value, key) for key, value in smell_grid.items()}


def _parse_key(key: object) -> Cell:
    if not isinstance(key, str):
        raise ObservationError(f'smell_grid key must be a "r,c" string, got {key!r}')
    parts = key.split(",")
    if len(parts) != 2:
        raise ObservationError(f'smell_grid key must be "r,c", got {key!r}')
    try:
        row, col = int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise ObservationError(f"smell_grid key {key!r} is not two integers") from exc
    if row < 0 or col < 0:
        raise ObservationError(f"smell_grid key {key!r} has a negative coordinate")
    return (row, col)


def _parse_intensity(value: object, key: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ObservationError(f"smell_grid[{key!r}] intensity must be a number, got {value!r}")
    if value < 0:
        raise ObservationError(f"smell_grid[{key!r}] intensity must be non-negative, got {value}")
    return float(value)


def encode_smell_grid(observed: Mapping[Cell, float]) -> dict[str, float]:
    """Encode a `(row, col) -> intensity` map to the sparse `{"r,c": intensity}` wire form.

    Only a positive intensity travels; a zero or silent cell is omitted (`M6-006a`). Keys
    are emitted in sorted `(row, col)` order so an identical field always serialises
    identically — the property a canonical hash of the turn would otherwise depend on.
    """
    return {
        f"{row},{col}": float(observed[(row, col)])
        for row, col in sorted(observed)
        if observed[(row, col)] > 0
    }
