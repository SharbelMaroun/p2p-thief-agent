"""Confirmed multiplicative scent physics (`M6-001`).

The scent model is fixed by the book, not negotiated. Appendix F table 16 pins the three
values as `FIXED` — centre intensity `0.9`, decay `ρ = 0.10`, field `5×5` (`AF-016`) — and
chapter 4.3 (PDF p.43) gives the per-turn update:

    τ(t+1) = max(0, (1 - ρ)·τ(t) + Δτ)

`(1 - ρ) = 0.9` **retains** 90% of the prior scent each turn (it does not remove 90%): the
book's prose "reduced by 90%" on p.43 is an arithmetic slip, corrected under the p.5
contradiction clause (`C-014`). The pinned simulator's subtractive/immediate decay has
lower authority and is not copied (`C-009`, `ADR-0005`).

**Emission shape.** Book Figure 4 (p.44,
`inst/police_thief_p2p_Summary.md:947-955`) names the radial profile of the new emission
Δτ by distance class: centre `0.90`, the orthogonal cross `0.62`, the diagonals `0.20`,
the mid-side edges `0.14`, the corners `0.04`. Those five classes cover 17 of the 25
cells. The **eight** cells at squared-distance 5 — the `(±1,±2)`/`(±2,±1)` ring — are
**not** named by the figure (`U-025`).

**That ring is now negotiated, not privately assumed.** No source yields a value for it,
so a private constant could only ever be this peer's guess, and two peers guessing
differently would emit different fields and discover it at an audit worth zero to both.
The book's own boxed section (PDF p.31,
`inst/police_thief_p2p_Summary.md:1043-1048`) prescribes the alternative: the parties
**agree** the emission and decay model, confirm they read it identically, and lock it
with a SHA-256 hash. So the ring is a parameter with a published default, and
`scent_lock` hashes the whole model at negotiation.

`DEFAULT_OUTER_RING_DELTA` carries **no book authority** and is not written as though it
does. It is our opening offer; the lock is what makes a disagreement visible in time.
"""

from __future__ import annotations

# Appendix F table 16 FIXED values (`AF-016`). Defaults, overridable from the agreed
# match terms so nothing is hard-coded on the play path.
EMISSION_CENTER = 0.9
DECAY_RATE = 0.10
FIELD_SIZE = 5

# Book Figure 4 (p.44): the emission Δτ by squared distance from the centre. These five
# classes are authoritative; every value is book-confirmed.
_CONFIRMED_EMISSION: dict[int, float] = {0: 0.90, 1: 0.62, 2: 0.20, 4: 0.14, 8: 0.04}

# The squared distance of the eight cells Figure 4 leaves unnamed (`U-025`).
OUTER_RING_SQUARED_DISTANCE = 5

# The negotiated default for that ring. NO BOOK AUTHORITY — see the module docstring.
DEFAULT_OUTER_RING_DELTA = 0.04


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
    """Apply one turn of the update τ(t+1) = max(0, (1-ρ)·τ(t) + Δτ) to one cell.

    Non-negative by construction (`M6-001d`): a cell that was silent and receives no
    emission stays `0.0` — an absence of information, never a negative one. The decay
    keeps 90% of the prior scent at the FIXED ρ = 0.10, not 10% (`C-014`).
    """
    return max(0.0, (1.0 - decay_rate) * intensity + emission)


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
