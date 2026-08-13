"""Locate the Cop from the *shape* of its scent window, not its values (`M11-001`).

A published `smell_grid` is a fixed-size square window **centred on the emitter**,
clipped to the board, with its zero cells kept. So the set of keys alone pins the Cop
exactly -- and it does so without assuming a single thing about that peer's physics:
not its decay rate, not whether it decays before or after depositing, not its emission
profile, not its rounding, not whether it clamps re-emission at the centre intensity.

Those assumptions are exactly what `emitter_decoder` has to make, and exactly what a
classmate's implementation is free to answer differently. When it does, the residual it
matches against explains nothing, the likelihood comes back flat, and belief stays
uniform. For a Thief that is not a small loss: `choose_evasive_action` runs *away from
the believed Cop*, so a belief that points at the wrong cell does not merely fail to
help, it aims the evasion at the pursuer.

The companion Cop repository found this first and from the other side: through a whole
counted series its belief never localised, and it toured fixed waypoints while its logs
showed the same move sequence in every sub-game. The defect is symmetric, so the fix is.

Recovering the centre is elementary. A window of half-width ``h`` centred on row ``r``
spans ``[r-h, r+h]`` clipped to the board. Unclipped low side: the centre is
``min_row + h``. Unclipped high side: ``max_row - h``. Both clipped at once only when
the window is wider than the board, and that case returns ``None`` rather than a guess.

Every result is *verified*: the reconstructed window must equal the observed key set
exactly. A peer that omits its zeros, or sends something that is not a window, gets
``None`` and the likelihood decoder keeps the turn. A wrong fix would be worse than
none, because this one is trusted absolutely.
"""

from __future__ import annotations

from collections.abc import Iterable

from p2p_thief_agent.domain.board import Board

Cell = tuple[int, int]

# The half-width assumed when neither axis reveals the sender's window size. The agreed
# pheromone field is 5x5, so 2 is the negotiated shape rather than a guess at a stranger.
DEFAULT_HALF = 2


def _contiguous(values: Iterable[int]) -> bool:
    """Return whether the sorted values form an unbroken run of integers."""
    ordered = sorted(values)
    return all(b - a == 1 for a, b in zip(ordered, ordered[1:], strict=False))


def _axis_centre(low: int, high: int, half: int, min_index: int, max_index: int) -> int | None:
    """Return the centre of a clipped span, or ``None`` when both sides are clipped."""
    if low > min_index:
        return low + half
    if high < max_index:
        return high - half
    return None


def _inferred_half(low: int, high: int, min_index: int, max_index: int) -> int | None:
    """Return the half-width an axis reveals, or ``None`` when that axis is clipped."""
    if low > min_index and high < max_index:
        return (high - low) // 2
    return None


def expected_window(row: int, col: int, board: Board, half: int = DEFAULT_HALF) -> set[Cell]:
    """Return the exact key set a window of ``half`` centred on ``(row, col)`` produces."""
    low, high = board.min_index, board.max_index
    return {
        (r, c)
        for r in range(max(low, row - half), min(high, row + half) + 1)
        for c in range(max(low, col - half), min(high, col + half) + 1)
    }


def window_centre(cells: Iterable[Cell], board: Board, half: int | None = None) -> Cell | None:
    """Return the cell an observed window is centred on, or ``None`` if undetermined."""
    observed = set(cells)
    if not observed:
        return None
    rows = {row for row, _ in observed}
    cols = {col for _, col in observed}
    if not (_contiguous(rows) and _contiguous(cols)):
        return None
    if len(observed) != len(rows) * len(cols):
        return None  # ragged: a full window is the complete rectangle of its own span
    low, high = board.min_index, board.max_index
    low_row, high_row, low_col, high_col = min(rows), max(rows), min(cols), max(cols)

    if half is None:
        half = (_inferred_half(low_row, high_row, low, high)
                or _inferred_half(low_col, high_col, low, high)
                or DEFAULT_HALF)
    if half < 0:
        return None
    row = _axis_centre(low_row, high_row, half, low, high)
    col = _axis_centre(low_col, high_col, half, low, high)
    if row is None or col is None:
        return None
    if not (low <= row <= high and low <= col <= high):
        return None
    if expected_window(row, col, board, half) != observed:
        return None
    return row, col


def certainty_belief(cell: Cell, board: Board) -> tuple[tuple[float, ...], ...]:
    """Return a belief grid putting all of its mass on one located cell."""
    low = board.min_index
    return tuple(
        tuple(1.0 if (row + low, col + low) == cell else 0.0 for col in range(board.size))
        for row in range(board.size)
    )
