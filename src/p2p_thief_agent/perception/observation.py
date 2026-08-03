"""Consume and produce the public scent observation on the wire (`M6-002`).

The scent a peer shares is the `smell_grid` field of a `TurnMessage`: a sparse map
`{"r,c": intensity}` (`SIM_WIRE_PROTOCOL.md`). This module is the boundary between that
wire shape and the `(row, col) -> intensity` map the belief layer works with. Emission
physics live in `scent.py`; this module only (de)serialises.

Only occupied cells travel: an unseen cell is **absent, not zero** (`M6-006a`), so an
empty observation is an empty object rather than a zero-filled grid. Parsing is
order-independent and encoding emits keys in a deterministic `(row, col)` order and rounds
every intensity to a **pinned precision** (`M6-006c`), so an identical field serialises to
byte-identical bytes on both peers — without which the locked scent-model hash would mean
nothing, two conforming peers still disagreeing on the field.

Parsing rejects a malformed key, a non-numeric/negative intensity, and — when the
negotiated board is supplied — any **off-board** cell (`M6-006b`).
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_thief_agent.domain.board import Board

Cell = tuple[int, int]

# Decimal places kept on the wire. Both peers round identically, so the same field always
# serialises to the same bytes (`M6-006c`). Six places comfortably resolve the emission
# profile (0.90…0.04) and its multiplicative decay without carrying float noise across.
SCENT_PRECISION = 6


class ObservationError(ValueError):
    """Raised when a `smell_grid` is malformed on the wire."""


def parse_smell_grid(smell_grid: object, board: Board | None = None) -> dict[Cell, float]:
    """Parse an inbound `{"r,c": intensity}` map into `(row, col) -> intensity`.

    Order-independent: the same cells parse to the same map whatever order they arrive
    in. A malformed key or a non-numeric/negative intensity is rejected by name. When the
    negotiated ``board`` is supplied, a cell outside its bounds is rejected too (`M6-006b`):
    an opponent's field is untrusted input and must not carry a cell that cannot exist.
    """
    if not isinstance(smell_grid, Mapping):
        raise ObservationError('smell_grid must be an object of {"r,c": intensity}')
    parsed = {_parse_key(key): _parse_intensity(value, key) for key, value in smell_grid.items()}
    if board is not None:
        for row, col in parsed:
            if not (board.min_index <= row <= board.max_index
                    and board.min_index <= col <= board.max_index):
                raise ObservationError(
                    f"smell_grid cell ({row},{col}) is off the {board.size}x{board.size} board"
                )
    return parsed


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

    Each intensity is rounded to `SCENT_PRECISION` decimals (`M6-006c`), then only a
    positive result travels — a zero, silent, or below-precision cell is omitted
    (`M6-006a`). Keys are emitted in sorted `(row, col)` order, so an identical field
    always serialises to identical bytes on both peers.
    """
    encoded: dict[str, float] = {}
    for row, col in sorted(observed):
        intensity = round(float(observed[(row, col)]), SCENT_PRECISION)
        if intensity > 0:
            encoded[f"{row},{col}"] = intensity
    return encoded
