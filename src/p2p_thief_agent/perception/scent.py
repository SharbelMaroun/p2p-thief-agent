"""Confirmed multiplicative scent physics (`M6-001`).

The scent model is fixed by the book, not negotiated. Appendix F table 16 pins the three
values as `FIXED` — centre intensity `0.9`, decay `ρ = 0.10`, field `5×5` (`AF-016`) — and
chapter 4.3 (PDF p.43) gives the per-turn update:

    τ(t+1) = max(0, (1 - ρ)·τ(t) + Δτ)

`(1 - ρ) = 0.9` **retains** 90% of the prior scent each turn (it does not remove 90%): the
book's prose "reduced by 90%" on p.43 is an arithmetic slip, corrected under the p.5
contradiction clause (`C-014`). The pinned simulator's subtractive/immediate decay has
lower authority and is not copied (`C-009`, `ADR-0005`).

**Emission shape — corrected 2026-08-08 (`U-025`, reopened and re-closed).** Book
Figure 4 names the radial profile of the emission Δτ by squared distance from the centre:
centre `0.90`, orthogonal cross `0.62`, diagonals **`0.42`**, mid-side edges **`0.20`**,
the eight `(±1,±2)`/`(±2,±1)` cells **`0.14`**, corners `0.04` — **25 of 25 cells**,
none unnamed.

**How the old table went wrong, because the shape of the error is the lesson.** The
translation at `inst/police_thief_p2p_Summary.md:947-955` lists five classes and gives
the diagonals `0.20` and the mid-side `0.14` — the true values of the *next two rings
out*. The table was the right curve **shifted inward by one radial class**, which is why
its endpoints (`0.90`, `0.62`, `0.04`) matched perfectly while the middle did not, and
why eight cells looked unnamed: the shift had consumed the class that owns `0.14`.

**What settles it.** Fit `τ = 0.9·exp(−k·d²)` using only the two values every reading
agrees on — centre `0.90` and cross `0.62` — and the rest follow with no free parameter:
`0.427`, `0.203`, `0.140`, `0.046`. That is the corrected table to two decimals, four for
four, and it is exactly what the figure's caption describes: a hill that decays radially.
The book PDF confirms it directly, and a classmate team reproduced the same kernel.

This repository defended the old reading on 2026-08-05 against these very values, on the
grounds that "a notebook answer is not a source" — but the notebook holds the **PDF**, and
the file it was checked against is a *translation*. A restatement is not the source
either; the rule was applied backwards, and it cost a wrong emission table in both peers.

`DEFAULT_OUTER_RING_DELTA` now carries book authority. The parameter survives only so a
peer insisting on a different ring can still be met and locked.
"""

from __future__ import annotations

# Appendix F table 16 FIXED values (`AF-016`). Defaults, overridable from the agreed
# match terms so nothing is hard-coded on the play path.
EMISSION_CENTER = 0.9
DECAY_RATE = 0.10
FIELD_SIZE = 5

# Book Figure 4: the emission Δτ by squared distance from the centre. Corrected
# 2026-08-08 — the diagonals are 0.42 and the mid-side 0.20; the previous 0.20/0.14 were
# this same curve shifted inward by one radial class.
_CONFIRMED_EMISSION: dict[int, float] = {0: 0.90, 1: 0.62, 2: 0.42, 4: 0.20, 8: 0.04}

# The squared distance of the eight cells that looked unnamed until the shift was found.
OUTER_RING_SQUARED_DISTANCE = 5

# Figure 4's value for that ring, book-authoritative since the 2026-08-08 correction.
DEFAULT_OUTER_RING_DELTA = 0.14


class ScentModelError(ValueError):
    """Raised when a negotiated scent parameter falls outside the model's range."""


def require_outer_ring(value: object) -> float:
    """Return a validated outer-ring Δτ, refusing anything outside `[0, 0.9]`.

    An opponent supplies this value at negotiation, so it is validated like any other
    peer input: above the centre intensity the field would stop decreasing with distance
    and would not be a radial emission at all, and a negative Δτ contradicts the book's
    "absence of information, never negative" reading of `max(0, ...)`.
    """
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ScentModelError(f"outer-ring emission must be a number, got {value!r}")
    if not 0.0 <= float(value) <= EMISSION_CENTER:
        raise ScentModelError(
            f"outer-ring emission must lie in [0, {EMISSION_CENTER}], got {value!r}"
        )
    return float(value)


def emission_delta(
    row_offset: int,
    col_offset: int,
    *,
    outer_ring: float = DEFAULT_OUTER_RING_DELTA,
) -> float:
    """Return the new emission Δτ for a cell at an offset from the agent's cell.

    The offset is measured in cells from the emission centre; anything outside the 5×5
    window contributes nothing, matching "if the agent is far, Δτ = 0" (book p.43).
    `outer_ring` is the agreed value for the eight cells the book does not name.
    """
    squared_distance = row_offset * row_offset + col_offset * col_offset
    if squared_distance in _CONFIRMED_EMISSION:
        return _CONFIRMED_EMISSION[squared_distance]
    if squared_distance == OUTER_RING_SQUARED_DISTANCE:
        return require_outer_ring(outer_ring)
    return 0.0


def emission_field(
    size: int = FIELD_SIZE,
    *,
    outer_ring: float = DEFAULT_OUTER_RING_DELTA,
) -> tuple[tuple[float, ...], ...]:
    """Return the `size×size` emission field centred on the agent (`M6-001a`).

    The centre carries `EMISSION_CENTER` and intensity falls off radially per the book's
    Figure 4 profile. `size` is the Appendix F FIXED `smell_grid_size` (5); it is a
    parameter only so a caller can pass the agreed value rather than assume it.
    """
    if size < 1 or size % 2 == 0:
        raise ValueError(f"scent field size must be a positive odd number, got {size}")
    half = size // 2
    return tuple(
        tuple(
            emission_delta(row - half, col - half, outer_ring=outer_ring)
            for col in range(size)
        )
        for row in range(size)
    )


def settle(intensity: float, emission: float, *, decay_rate: float = DECAY_RATE) -> float:
    """One turn of τ(t+1) = clamp((1-ρ)·τ(t) + Δτ, 0, EMISSION_CENTER) for one cell.

    Non-negative by construction (`M6-001d`): a cell that was silent and receives no
    emission stays `0.0` — an absence of information, never a negative one. The decay
    keeps 90% of the prior scent at the FIXED ρ = 0.10, not 10% (`C-014`).

    **The UPPER clamp closes `U-031`, added after the open question cost a live sub-game
    (companion `C-048`).** The book prints only `max(0, ...)`, so this repository applied
    no cap and a cell already scented and emitted on again rose above the centre
    intensity. Against group `yanell11` on 2026-08-15 the companion's Police reached
    `≈1.46` at one cell; their verifier read the published `smell_grid`, called it a
    deviation from the locked model and declared a technical loss — which Appendix E rule
    23 supports, its sanction for deviating from the agreed emission formula being that
    the game is cancelled. This agent emits the same trail and lost sub-game 2 to it.

    The clamp comes from the book, not from the peer: chapter 4 declares τ continuous in
    `[0, 0.9]`, and a value above `EMISSION_CENTER` contradicts that declaration while the
    printed `max(0, ...)` merely omits it. Where a formula and a stated range disagree the
    range is the tighter and safer claim — a field that never exceeds the centre cannot be
    refused by a peer that would permit more, and the converse is what actually happened.
    """
    return min(max(0.0, (1.0 - decay_rate) * intensity + emission), EMISSION_CENTER)


def advance_field(
    field: tuple[tuple[float, ...], ...],
    emission: tuple[tuple[float, ...], ...],
    *,
    decay_rate: float = DECAY_RATE,
) -> tuple[tuple[float, ...], ...]:
    """Advance a whole scent field one full turn, cell by cell (`M6-001b`).

    Decay is a single per-turn step applied after both peers have acted, so this is
    called once per turn, not once per move. ``field`` and ``emission`` must share shape.
    """
    if [len(row) for row in field] != [len(row) for row in emission]:
        raise ValueError("scent field and emission must share the same shape")
    return tuple(
        tuple(
            settle(now, add, decay_rate=decay_rate)
            for now, add in zip(field_row, emit_row, strict=True)
        )
        for field_row, emit_row in zip(field, emission, strict=True)
    )
