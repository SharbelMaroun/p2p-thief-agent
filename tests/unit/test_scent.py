"""`M6-001`: the confirmed multiplicative scent physics.

The values are the book's, not ours: Appendix F table 16 fixes centre `0.9`, decay `0.10`,
field `5×5`, and Figure 4 (p.44) fixes the radial emission profile. The decay **retains**
90% each turn — the p.43 prose "reduced by 90%" is the arithmetic slip corrected under
`C-014`. The eight unnamed edge cells are `U-025`, pinned here against the flagged
provisional so a later ruling moves the test and the code together.
"""

import pytest

from p2p_thief_agent.perception.scent import (
    _PROVISIONAL_D2_5,
    advance_field,
    emission_delta,
    emission_field,
    settle,
)


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


def test_the_eight_unnamed_edge_cells_are_the_flagged_provisional() -> None:
    """`U-025`: the squared-distance-5 ring the figure never names."""
    field = emission_field()
    unnamed = {field[0][1], field[0][3], field[1][0], field[1][4],
               field[3][0], field[3][4], field[4][1], field[4][3]}
    assert unnamed == {_PROVISIONAL_D2_5}


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
