"""`M6-001`: the confirmed multiplicative scent physics.

The values are the book's, not ours: Appendix F table 16 fixes centre `0.9`, decay `0.10`,
field `5×5`, and Figure 4 (p.44) fixes the radial emission profile. The decay **retains**
90% each turn — the p.43 prose "reduced by 90%" is the arithmetic slip corrected under
`C-014`. The eight unnamed edge cells are `U-025`; they are now a **negotiated** value
carried by the rule-23 lock rather than a private constant, so the tests pin both the
default and the fact that an agreed value replaces it.
"""

import pytest

from p2p_thief_agent.perception.scent import (
    DEFAULT_OUTER_RING_DELTA,
    ScentModelError,
    advance_field,
    emission_delta,
    emission_field,
    require_outer_ring,
    settle,
)

# The eight squared-distance-5 cells, as (row, col) indices into a 5×5 field.
UNNAMED_RING = ((0, 1), (0, 3), (1, 0), (1, 4), (3, 0), (3, 4), (4, 1), (4, 3))


def test_the_field_is_5x5_centred_on_the_agent_at_0_9() -> None:
    """`M6-001a`: a 5×5 emission field with the agent's own cell at the FIXED 0.9."""
    field = emission_field()
    assert len(field) == 5 and all(len(row) == 5 for row in field)
    assert field[2][2] == 0.90


def test_the_radial_profile_matches_book_figure_4() -> None:
    """`M6-001c`: the five book-confirmed distance classes, exactly."""
    field = emission_field()
    cross = {field[1][2], field[3][2], field[2][1], field[2][3]}
    diagonal = {field[1][1], field[1][3], field[3][1], field[3][3]}
    mid_side = {field[0][2], field[4][2], field[2][0], field[2][4]}
    corners = {field[0][0], field[0][4], field[4][0], field[4][4]}
    assert cross == {0.62}
    assert diagonal == {0.20}
    assert mid_side == {0.14}
    assert corners == {0.04}


def test_the_eight_unnamed_edge_cells_carry_the_default_offer() -> None:
    """`U-025`: the squared-distance-5 ring the figure never names."""
    field = emission_field()
    assert {field[r][c] for r, c in UNNAMED_RING} == {DEFAULT_OUTER_RING_DELTA}


def test_an_agreed_ring_value_replaces_the_default_across_all_eight() -> None:
    """The ring is negotiated: whatever the peers lock is what this peer emits."""
    field = emission_field(outer_ring=0.07)
    assert {field[r][c] for r, c in UNNAMED_RING} == {0.07}
    assert field[2][2] == 0.90  # the book-confirmed classes are untouched


def test_every_cell_of_the_window_is_emitted() -> None:
    """The reference emits all 25; an omitted cell is indistinguishable from a zero."""
    field = emission_field()
    assert sum(1 for row in field for value in row if value > 0.0) == 25


@pytest.mark.parametrize("bad", [-0.01, 1.0, "0.04", True, None])
def test_a_ring_value_outside_the_model_is_refused(bad: object) -> None:
    """An opponent supplies this at negotiation, so it is validated like any input."""
    with pytest.raises(ScentModelError):
        require_outer_ring(bad)


def test_the_ring_may_legally_be_zero_or_the_centre_intensity() -> None:
    assert require_outer_ring(0.0) == 0.0
    assert require_outer_ring(0.9) == 0.9


def test_a_cell_beyond_the_window_receives_no_emission() -> None:
    assert emission_delta(3, 0) == 0.0  # squared distance 9 is outside the 5×5


def test_decay_retains_ninety_percent_not_ten() -> None:
    """`M6-001b` / `C-014`: (1-ρ)=0.9, so a silent turn keeps 0.9 → 0.81, not 0.09."""
    assert settle(0.9, 0.0) == pytest.approx(0.81)


def test_a_fresh_emission_lands_on_a_silent_cell() -> None:
    assert settle(0.0, 0.9) == pytest.approx(0.9)


def test_the_update_adds_emission_to_the_decayed_prior() -> None:
    assert settle(0.5, 0.14) == pytest.approx(0.9 * 0.5 + 0.14)


def test_intensity_is_clipped_non_negative() -> None:
    """`M6-001d`: a never-visited cell reads 0, and the update never goes negative."""
    assert settle(0.0, 0.0) == 0.0
    assert settle(-1.0, 0.0) == 0.0


def test_advance_field_applies_the_update_cell_by_cell() -> None:
    field = ((0.9, 0.0), (0.0, 0.5))
    emission = ((0.0, 0.9), (0.0, 0.14))
    assert advance_field(field, emission) == (
        (pytest.approx(0.81), pytest.approx(0.9)),
        (0.0, pytest.approx(0.9 * 0.5 + 0.14)),
    )


def test_advance_field_rejects_a_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="same shape"):
        advance_field(((0.0, 0.0),), ((0.0,),))


def test_the_field_size_must_be_a_positive_odd_number() -> None:
    """An even window has no single centre cell to place the agent on."""
    with pytest.raises(ValueError, match="positive odd number"):
        emission_field(size=4)
