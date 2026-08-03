"""Thief-local belief over the Cop's position (`M6-003`).

Partial observability is the whole game: the Thief never sees the Cop's cell (`AE-8`,
`AE-9`). It keeps only a probability distribution over where the Cop *might* be, updated
from **public** evidence — the Cop's shared scent and its natural-language hints — and
never from objective truth. This module holds that distribution and the Bayes mechanics.

Turning a specific observation into a likelihood is the caller's job (the scent and hint
adapters), so no Cop-truth source can enter here: `apply_evidence` takes a prior and a
likelihood, nothing that names a real cell. The matrix is sized to the **negotiated**
grid, not the book's 10×10 illustration, always sums to 1, and a zero-evidence update
falls back to the max-entropy distribution rather than dividing by zero (`M6-003c`).
"""

from __future__ import annotations

from collections.abc import Sequence

Grid = tuple[tuple[float, ...], ...]


class BeliefError(ValueError):
    """Raised when a belief grid or an evidence update is malformed."""


def _dimensions(matrix: Sequence[Sequence[float]]) -> tuple[int, int]:
    if len(matrix) == 0 or len(matrix[0]) == 0:
        raise BeliefError("belief grid must be a non-empty rectangular matrix")
    if any(len(row) != len(matrix[0]) for row in matrix):
        raise BeliefError("belief grid rows must all be the same length")
    return len(matrix), len(matrix[0])


def uniform_belief(rows: int, cols: int) -> Grid:
    """Return the max-entropy belief: every cell equally likely to hold the Cop.

    The first turn has no prior beyond the public start positions, so a uniform grid is
    the honest starting point — the Thief asserts nothing it has not observed (`M6-003a`).
    """
    if rows < 1 or cols < 1:
        raise BeliefError(f"belief grid must be at least 1x1, got {rows}x{cols}")
    share = 1.0 / (rows * cols)
    return tuple(tuple(share for _ in range(cols)) for _ in range(rows))


def normalize(matrix: Sequence[Sequence[float]]) -> Grid:
    """Scale a non-negative matrix to sum to 1; a zero total falls back to uniform.

    Dividing by a zero total is the failure `M6-003c` guards: evidence that zeroes every
    cell leaves not a crash and not an invalid grid, but the max-entropy distribution —
    "I have no information", which is itself a valid belief.
    """
    rows, cols = _dimensions(matrix)
    total = 0.0
    for row in matrix:
        for value in row:
            if value < 0:
                raise BeliefError(f"belief values must be non-negative, got {value}")
            total += value
    if total == 0.0:
        return uniform_belief(rows, cols)
    return tuple(tuple(value / total for value in row) for row in matrix)


def apply_evidence(belief: Grid, likelihood: Sequence[Sequence[float]]) -> Grid:
    """Bayes update: posterior ∝ prior × likelihood, renormalised (`M6-003b` mechanism).

    ``likelihood[r][c]`` is P(observation | Cop at (r, c)), computed by the caller from a
    public observation — scent or a hint — never from the Cop's true cell (`M6-003d`). A
    uniform likelihood leaves the prior unchanged; a likelihood that is zero everywhere is
    contradictory evidence and resets to uniform rather than dividing by zero.
    """
    if _dimensions(belief) != _dimensions(likelihood):
        raise BeliefError("belief and likelihood must share the same shape")
    product = tuple(
        tuple(prior * odds for prior, odds in zip(prior_row, like_row, strict=True))
        for prior_row, like_row in zip(belief, likelihood, strict=True)
    )
    return normalize(product)
