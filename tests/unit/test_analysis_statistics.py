"""`M9-006c`: summaries that carry their run count, and a paired test that cannot be faked.

"Experiment tables with **run counts**, not anecdotes" is the row's condition, and the book
sets the standard: research "based on numbers and not on guesses" (p.142/266). These tests
pin the arithmetic the research report quotes, so a figure in that report is wrong only if a
test here is wrong too.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.analysis import paired_compare, quantile, summarise


def test_a_summary_reports_the_run_count_alongside_every_figure() -> None:
    """The whole point of the row. A mean with no `n` is an anecdote with a decimal point."""
    summary = summarise([1.0, 2.0, 3.0, 4.0])
    assert summary.runs == 4
    assert summary.as_dict()["runs"] == 4
    assert summary.mean == 2.5


def test_a_summary_of_nothing_is_refused_rather_than_returning_zeros() -> None:
    """Zeros would flow into the report looking like a measurement of zero."""
    with pytest.raises(ValueError, match="anecdote"):
        summarise([])


def test_the_standard_deviation_is_the_sample_one() -> None:
    """These are runs drawn from a process, not a whole population, so `n-1` is the honest
    denominator. Population stdev would understate the spread and make every configuration
    look more reliable than it is."""
    assert summarise([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]).stdev == pytest.approx(2.13809, abs=1e-5)


def test_a_single_run_reports_no_spread_rather_than_dividing_by_zero() -> None:
    summary = summarise([7.0])
    assert summary.runs == 1 and summary.stdev == 0.0
    assert summary.five_number == (7.0, 7.0, 7.0, 7.0, 7.0)


def test_quantiles_interpolate_rather_than_snapping_to_a_sample() -> None:
    """At a few dozen scenarios a nearest-rank Q1 moves in steps of several percentage points, which
    would make two genuinely different configurations report identical boxes."""
    assert quantile([1.0, 2.0, 3.0, 4.0], 0.5) == 2.5
    assert quantile([1.0, 2.0, 3.0, 4.0], 0.25) == 1.75


def test_a_quantile_of_nothing_is_refused_rather_than_returning_zero() -> None:
    """Reached directly rather than through `summarise`, which guards earlier. A silent
    0.0 would land in a box plot as a real lower whisker."""
    with pytest.raises(ValueError, match="quantile of no values"):
        quantile([], 0.5)


def test_the_five_number_summary_is_ordered_as_a_box_plot_draws_it() -> None:
    summary = summarise([5.0, 1.0, 9.0, 3.0, 7.0])
    low, q1, median, q3, high = summary.five_number
    assert low <= q1 <= median <= q3 <= high
    assert (low, median, high) == (1.0, 5.0, 9.0)


# --- the paired comparison ---------------------------------------------------------------


def test_a_paired_comparison_counts_wins_losses_and_ties_per_seed() -> None:
    """Seed *i* gives both arms the identical opponent, so this is a paired design and the
    per-seed verdict is meaningful in a way two averages are not."""
    result = paired_compare([20.0, 20.0, 5.0, 20.0], [5.0, 20.0, 20.0, 5.0])
    assert (result.wins, result.losses, result.ties, result.pairs) == (2, 1, 1, 4)
    assert result.win_share == pytest.approx(2 / 3), "ties carry no information either way"


def test_unequal_arms_are_refused_rather_than_zipped_short() -> None:
    """**The guard that matters.** Truncating would pair unrelated matches and produce a
    number that reads exactly like evidence."""
    with pytest.raises(ValueError, match="same scenarios on both sides"):
        paired_compare([1.0, 2.0, 3.0], [1.0, 2.0])


def test_an_all_tied_comparison_reports_zero_share_rather_than_dividing_by_zero() -> None:
    result = paired_compare([1.0, 1.0], [1.0, 1.0])
    assert result.decisive == 0 and result.win_share == 0.0


def test_the_dict_form_keeps_the_pair_count_visible() -> None:
    """A win count without its denominator is the same failure as a mean without its `n`."""
    assert set(paired_compare([1.0], [0.0]).as_dict()) == {
        "pairs", "wins", "losses", "ties", "win_share_of_decisive"
    }
