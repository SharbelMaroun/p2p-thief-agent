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

Parsing rejects a malformed key and a non-numeric/negative intensity. An off-board cell —
when the negotiated ``board`` is supplied — is **dropped, not rejected** (`M6-006b`,
corrected 2026-08-09): the reference wire sends a *fixed-size* 5x5 window centred on the
sender, "includes zero cells rather than omitting them" (see `docs/SIM_WIRE_PROTOCOL.md`),
and on a 7x7 board only the central 3x3 of sender positions (9 of 49 cells, 18%) yields a
window with no off-board coordinate. Rejecting the *whole* grid over one such cell, from a
peer standing anywhere in the outer 82% of the board, discarded every real observation and
froze belief for the rest of the match — reproduced 2026-08-09 against the companion Cop
repository's matching defect. Dropping only the off-board cells matches this module's own
stated rule for what it sends: "strict in what we send, generous in what we accept." A
malformed *key* or *intensity* still raises — that is genuine corruption, not a coordinate
system difference, and `parse_smell_grid_dropped_count` keeps the discard rate visible so a
grid that is mostly or entirely off-board stays observable rather than vanishing silently.
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
    in. A malformed key or a non-numeric/negative intensity is rejected by name — that is
    genuine corruption. When the negotiated ``board`` is supplied, a cell outside its
    bounds is **dropped**, not rejected (`M6-006b`): a fixed-size window from a sender near
    an edge or corner necessarily carries such cells, and they are not evidence of a
    hostile or corrupt peer, only of a different (equally valid) encoding convention. Use
    `parse_smell_grid_dropped_count` alongside this to keep the discard rate visible.
    """
    parsed = _parse_all(smell_grid)
    if board is None:
        return parsed
    return {cell: value for cell, value in parsed.items() if _on_board(cell, board)}


def parse_smell_grid_dropped_count(smell_grid: object, board: Board) -> int:
    """Return how many cells `parse_smell_grid` would drop from `smell_grid` for being
    off `board` — diagnostic visibility, so a grid that is mostly or entirely off-board
    (a real encoding mismatch, not just an edge-of-board window) does not vanish silently
    into an empty observation with no trace anywhere.
    """
    parsed = _parse_all(smell_grid)
    return sum(1 for cell in parsed if not _on_board(cell, board))


def _parse_all(smell_grid: object) -> dict[Cell, float]:
    if not isinstance(smell_grid, Mapping):
        raise ObservationError('smell_grid must be an object of {"r,c": intensity}')
    return {_parse_key(key): _parse_intensity(value, key) for key, value in smell_grid.items()}


def _on_board(cell: Cell, board: Board) -> bool:
    row, col = cell
    return board.min_index <= row <= board.max_index and board.min_index <= col <= board.max_index


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
    # A negative coordinate is not malformed data by itself -- it is off-board only
    # relative to a board's axis_start_index, which `parse_smell_grid` decides when a
    # board is supplied. Structural key validity ends here.
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
