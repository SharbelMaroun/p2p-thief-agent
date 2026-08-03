"""`M6-003` foundation: the Thief-local belief distribution and its Bayes update.

Covers the board-sized matrix (`M6-003a`), zero-safe normalisation (`M6-003c`), the
Bayes mechanism (`M6-003b`), and the privacy guarantee that no objective Cop truth can
enter the update (`M6-003d`). The trust factor and hint decoding (`M6-003b` trust,
`M6-003e/f`) build on this and are separate.
"""

import inspect

import pytest

from p2p_thief_agent.perception.belief import (
    BeliefError,
    apply_evidence,
    normalize,
    uniform_belief,
)


def total(grid) -> float:
    return sum(value for row in grid for value in row)


def test_a_uniform_belief_is_sized_to_the_grid_and_sums_to_one() -> None:
    """`M6-003a`: sized to the negotiated grid, not the book's 10x10 illustration."""
    belief = uniform_belief(3, 4)
    assert len(belief) == 3 and all(len(row) == 4 for row in belief)
    assert belief[0][0] == pytest.approx(1 / 12)
    assert total(belief) == pytest.approx(1.0)


def test_a_degenerate_grid_size_is_rejected() -> None:
    with pytest.raises(BeliefError, match="at least 1x1"):
        uniform_belief(0, 5)


def test_normalize_scales_to_a_distribution() -> None:
    assert normalize([[1.0, 3.0]]) == (pytest.approx((0.25, 0.75)),)
    assert total(normalize([[2.0, 2.0], [2.0, 2.0]])) == pytest.approx(1.0)


def test_a_zero_total_falls_back_to_uniform_not_a_division_by_zero() -> None:
    """`M6-003c`: contradictory evidence leaves a valid max-entropy distribution."""
    assert normalize([[0.0, 0.0], [0.0, 0.0]]) == uniform_belief(2, 2)


def test_negative_values_are_rejected() -> None:
    with pytest.raises(BeliefError, match="non-negative"):
        normalize([[0.5, -0.1]])


def test_a_ragged_matrix_is_rejected() -> None:
    with pytest.raises(BeliefError, match="same length"):
        normalize([[0.5, 0.5], [1.0]])


@pytest.mark.parametrize("empty", [[], [[]]])
def test_an_empty_matrix_is_rejected(empty: list) -> None:
    with pytest.raises(BeliefError, match="non-empty rectangular"):
        normalize(empty)


def test_evidence_concentrates_belief_where_the_observation_is_likely() -> None:
    """`M6-003b`: posterior ∝ prior × likelihood, renormalised."""
    prior = uniform_belief(1, 3)
    posterior = apply_evidence(prior, [[0.0, 1.0, 0.0]])
    assert posterior == (pytest.approx((0.0, 1.0, 0.0)),)
    assert total(posterior) == pytest.approx(1.0)


def test_a_uniform_likelihood_leaves_the_prior_unchanged() -> None:
    prior = apply_evidence(uniform_belief(2, 2), [[1.0, 3.0], [2.0, 4.0]])
    assert apply_evidence(prior, [[0.5, 0.5], [0.5, 0.5]]) == prior


def test_a_likelihood_that_is_zero_everywhere_resets_to_uniform() -> None:
    """`M6-003c`: no posterior cell survives, so belief returns to max entropy."""
    prior = apply_evidence(uniform_belief(2, 2), [[0.1, 0.9], [0.4, 0.6]])
    assert apply_evidence(prior, [[0.0, 0.0], [0.0, 0.0]]) == uniform_belief(2, 2)


def test_evidence_of_a_different_shape_is_rejected() -> None:
    with pytest.raises(BeliefError, match="same shape"):
        apply_evidence(uniform_belief(2, 2), [[1.0, 1.0]])


def test_the_belief_update_takes_no_objective_cop_truth() -> None:
    """`M6-003d`: the update's only inputs are a prior and a public likelihood.

    There is no parameter for the Cop's real cell, so objective truth cannot enter by
    construction, and the result is always a distribution, never a stored certainty
    `[AE-8]` `[AE-9]`.
    """
    assert set(inspect.signature(apply_evidence).parameters) == {"belief", "likelihood"}
    posterior = apply_evidence(uniform_belief(2, 2), [[0.0, 9.0], [0.0, 1.0]])
    assert total(posterior) == pytest.approx(1.0)
