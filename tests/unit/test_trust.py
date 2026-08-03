"""`M6-003b`/`M6-003f`: temper a hint by trust, and move trust by scent agreement."""

import pytest

from p2p_thief_agent.perception.belief import BeliefError, uniform_belief
from p2p_thief_agent.perception.trust import (
    NEUTRAL_TRUST,
    trust_weighted,
    update_trust,
)

PEAK_00 = [[1.0, 0.0], [0.0, 0.0]]
PEAK_11 = [[0.0, 0.0], [0.0, 1.0]]


def test_full_trust_applies_the_hint_as_is() -> None:
    assert trust_weighted(PEAK_00, 1.0) == (pytest.approx((1.0, 0.0)), pytest.approx((0.0, 0.0)))


def test_zero_trust_collapses_the_hint_to_uniform() -> None:
    """A hint from a peer earned no belief moves nothing."""
    assert trust_weighted(PEAK_00, 0.0) == uniform_belief(2, 2)


def test_half_trust_blends_toward_uniform() -> None:
    weighted = trust_weighted(PEAK_00, 0.5)
    assert weighted[0][0] == pytest.approx(0.625)  # 0.5*1 + 0.5*0.25
    assert weighted[1][1] == pytest.approx(0.125)  # 0.5*0 + 0.5*0.25


def test_trust_out_of_range_is_rejected() -> None:
    with pytest.raises(BeliefError, match="trust must be in"):
        trust_weighted(PEAK_00, 1.5)


def test_a_hint_confirmed_by_scent_earns_trust() -> None:
    """`M6-003f`: the hint concentrates where the Cop's scent does."""
    assert update_trust(NEUTRAL_TRUST, PEAK_00, PEAK_00) > NEUTRAL_TRUST


def test_a_hint_contradicted_by_scent_loses_trust() -> None:
    """A claimed direction with no scent residue behind it is evidence of a lie."""
    assert update_trust(NEUTRAL_TRUST, PEAK_11, PEAK_00) < NEUTRAL_TRUST


def test_an_uninformative_hint_leaves_trust_unchanged() -> None:
    flat = uniform_belief(2, 2)
    assert update_trust(NEUTRAL_TRUST, flat, PEAK_00) == pytest.approx(NEUTRAL_TRUST)


def test_trust_is_clipped_to_the_unit_interval() -> None:
    assert update_trust(0.95, PEAK_00, PEAK_00) == 1.0
    assert update_trust(0.10, PEAK_11, PEAK_00) == 0.0


def test_a_shape_mismatch_is_rejected() -> None:
    with pytest.raises(BeliefError, match="same shape"):
        update_trust(NEUTRAL_TRUST, [[1.0, 0.0]], PEAK_00)


def test_the_trust_rate_must_be_a_unit_value() -> None:
    with pytest.raises(BeliefError, match="rate must be in"):
        update_trust(NEUTRAL_TRUST, PEAK_00, PEAK_00, rate=2.0)
