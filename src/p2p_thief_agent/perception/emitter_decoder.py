"""Model-matched emitter decoding: invert the locked scent physics (`M6-031`).

The sixth evasion attempt localised the whole six-attempt graveyard to one number:
truth-fed, the exact planner escapes 24/24 against every committed archetype;
argmax-fed it collapses to 4/24. The argmax comes from `scent_likelihood`, which
weights cells by **raw observed intensity** — it discards everything the agreed model
says about how a trail decays and stacks, so a twice-visited old cell outshines a
fresh stamp and the estimate lags the emitter by the cell that loses the game.

But the physics is a shared, hash-locked contract (`scent_lock`), and it is exactly
invertible. The field obeys `τ' = max(0, (1-ρ)·τ + Δτ)` with both terms non-negative,
so the clip never bites and consecutive observations satisfy, cell for cell:

    now(x) − (1−ρ)·before(x)  =  Δτ(x − emitter)

The left side is computable from two public observations; the right side is the
agreed 5×5 stamp. Decoding the emitter is therefore **profile matching on the
residual**: score every candidate cell by how badly the residual mismatches the stamp
centred there, and the true emitter scores zero. The worst wrong candidate is right
next door, and even it carries at least the centre-versus-cross gap `(0.9 − 0.62)²`,
so a sharply decaying score separates truth from neighbour by orders of magnitude.

Authority: the book fixes the physics and frees the inference — "how an agent
analyses the deviation between the physics and its observations is a free strategic
component expected of every team" (pp. 48/121, 94/211) — and the reference itself
ships a model-matched observation step (`BeliefGrid.observe_smell`), so this is the
book's own path taken seriously, not a loophole. Zero-Trust holds: inputs are the
opponent's published `smell_grid` observations and the agreed constants, never a true
position (`M6-003d`).

Degraded modes are explicit rather than accidental: with no previous observation
(first turn, or a gap after a silent turn) the residual *is* the current field, which
is exact on turn one and approximate after a gap; with a partial window (the live
wire sends 5×5, not the board) the caller restricts scoring to the cells both
observations actually covered, because "unobserved" is not "zero".
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.perception.belief import Grid
from p2p_thief_agent.perception.scent import DECAY_RATE, DEFAULT_OUTER_RING_DELTA, emission_delta

Cell = tuple[int, int]

# The 5×5 stamp reaches two cells from its centre.
_RADIUS = 2

# e^(−error/SHARPNESS) turns a match error into a likelihood. The nearest wrong
# centre carries at least (0.9−0.62)² ≈ 0.078 of error, so 0.01 gives the true cell
# more than a thousand times the mass of its best rival while never zeroing anyone —
# a wrong model (a rule-23 deviator) degrades smoothly toward uniform instead of
# crashing the belief (`M6-003c`).
SHARPNESS = 0.01


def residual(
    now: Mapping[Cell, float],
    before: Mapping[Cell, float] | None,
    *,
    decay_rate: float = DECAY_RATE,
) -> dict[Cell, float]:
    """Return `now − (1−ρ)·before` per cell: the newest stamp, by the locked contract."""
    keep = 1.0 - decay_rate
    cells = set(now) | set(before or ())
    return {cell: now.get(cell, 0.0) - keep * (before or {}).get(cell, 0.0)
            for cell in cells}


def match_error(
    board: Board,
    observed_residual: Mapping[Cell, float],
    centre: Cell,
    trusted: Iterable[Cell] | None = None,
    *,
    outer_ring: float = DEFAULT_OUTER_RING_DELTA,
) -> float:
    """Return the squared mismatch between the residual and the stamp at ``centre``.

    Scored over the stamp's on-board support plus the residual's support, so both a
    missing stamp cell and an unexplained residual cell count against a candidate.
    ``trusted`` restricts scoring to cells whose residual is actually computable —
    the partial-window case; ``None`` trusts everything (full-field observations).
    """
    centre_row, centre_col = centre
    cells = {
        (centre_row + dr, centre_col + dc)
        for dr in range(-_RADIUS, _RADIUS + 1) for dc in range(-_RADIUS, _RADIUS + 1)
        if board.min_index <= centre_row + dr <= board.max_index
        and board.min_index <= centre_col + dc <= board.max_index
    }
    cells |= set(observed_residual)
    if trusted is not None:
        cells &= set(trusted)
    error = 0.0
    for cell in sorted(cells):
        expected = emission_delta(cell[0] - centre_row, cell[1] - centre_col,
                                  outer_ring=outer_ring)
        gap = observed_residual.get(cell, 0.0) - expected
        error += gap * gap
    return error


def emitter_likelihood(
    board: Board,
    now: Mapping[Cell, float],
    before: Mapping[Cell, float] | None = None,
    trusted: Iterable[Cell] | None = None,
    *,
    sharpness: float = SHARPNESS,
) -> Grid:
    """Return a likelihood grid over emitter cells for the belief's Bayes update.

    Plugs into `apply_evidence` exactly where `scent_likelihood` does; the difference
    is what a cell's weight *means* — not "how much scent sits here" but "how well
    the whole observed change is explained by the emitter standing here". An empty
    observation carries no information and yields the uniform-safe all-equal grid.
    """
    from math import exp  # noqa: PLC0415

    if not now:
        return tuple(tuple(1.0 for _ in range(board.size)) for _ in range(board.size))
    delta = residual(now, before)
    trusted_cells = None if trusted is None else set(trusted)
    grid = tuple(
        tuple(
            exp(-match_error(board, delta,
                             (board.min_index + r, board.min_index + c),
                             trusted_cells) / sharpness)
            for c in range(board.size)
        )
        for r in range(board.size)
    )
    if not any(value > 0.0 for row in grid for value in row):
        # A field the model cannot explain anywhere (a rule-23 deviator, or numeric
        # underflow on one): explicitly no information, never a hard zero belief.
        return tuple(tuple(1.0 for _ in range(board.size)) for _ in range(board.size))
    return grid
