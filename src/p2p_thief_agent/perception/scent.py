"""Confirmed multiplicative scent physics (`M6-001`).

The scent model is fixed by the book, not negotiated. Appendix F table 16 pins the three
values as `FIXED` — centre intensity `0.9`, decay `ρ = 0.10`, field `5×5` (`AF-016`) — and
chapter 4.3 (PDF p.43) gives the per-turn update:

    τ(t+1) = max(0, (1 - ρ)·τ(t) + Δτ)

`(1 - ρ) = 0.9` **retains** 90% of the prior scent each turn (it does not remove 90%): the
book's prose "reduced by 90%" on p.43 is an arithmetic slip, corrected under the p.5
contradiction clause (`C-014`). The pinned simulator's subtractive/immediate decay has
lower authority and is not copied (`C-009`, `ADR-0005`).

**Emission shape.** Book Figure 4 (p.44) names the radial profile of the new emission Δτ
by distance class: centre `0.90`, the orthogonal cross `0.62`, the diagonals `0.20`, the
mid-side edges `0.14`, the corners `0.04`. Those five classes cover 17 of the 25 cells.
The **eight** cells at squared-distance 5 — the `(±1,±2)`/`(±2,±1)` ring — are **not**
named by the figure, so their value is an open unknown (`U-025`); `_PROVISIONAL_D2_5`
holds a documented residual pending a ruling rather than a silent guess.
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

# `U-025`: the eight cells at squared-distance 5 are unnamed by the figure. This residual
# is provisional and flagged, not confirmed — change it here if the coordinator rules.
_PROVISIONAL_D2_5 = 0.04


def emission_delta(row_offset: int, col_offset: int) -> float:
    """Return the new emission Δτ for a cell at an offset from the agent's cell.

    The offset is measured in cells from the emission centre; anything outside the 5×5
    window contributes nothing, matching "if the agent is far, Δτ = 0" (book p.43).
    """
    squared_distance = row_offset * row_offset + col_offset * col_offset
    if squared_distance in _CONFIRMED_EMISSION:
        return _CONFIRMED_EMISSION[squared_distance]
    if squared_distance == 5:  # the eight unnamed cells — U-025, provisional
        return _PROVISIONAL_D2_5
    return 0.0


def emission_field(size: int = FIELD_SIZE) -> tuple[tuple[float, ...], ...]:
    """Return the `size×size` emission field centred on the agent (`M6-001a`).

    The centre carries `EMISSION_CENTER` and intensity falls off radially per the book's
    Figure 4 profile. `size` is the Appendix F FIXED `smell_grid_size` (5); it is a
    parameter only so a caller can pass the agreed value rather than assume it.
    """
    if size < 1 or size % 2 == 0:
        raise ValueError(f"scent field size must be a positive odd number, got {size}")
    half = size // 2
    return tuple(
        tuple(emission_delta(row - half, col - half) for col in range(size))
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
