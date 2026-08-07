"""`M7-009`: the agreed per-game limit, and where the numbers come from.

Split from `test_token_ledger.py`, which covers the accounting. This covers the two places a
correct ledger still reports a wrong figure: clamping an over-run so the report looks
compliant, and reading a missing provider usage block as zero.

Both produce a number that looks fine, which is what makes them worse than a refusal. Rule
35 scores a report that contradicts the opponent's 0 for **both** groups, so a plausible
wrong figure costs more here than an error at report time.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.reporting.token_ledger import (
    TokenLedger,
    TokenLedgerError,
    TokenUsage,
    usage_from_response,
)


def ledger(limit: int) -> TokenLedger:
    return TokenLedger(max_tokens_per_game=limit)


def usage(total: int) -> TokenUsage:
    return TokenUsage(prompt=total // 2, completion=total - total // 2)


# --- the agreed limit ---------------------------------------------------------------------------


def test_an_over_run_is_reported_rather_than_clamped() -> None:
    """A ledger that caps its own number reports a compliant figure for a game that was
    not, which is the contradiction rule 35 scores 0 for both groups."""
    book = ledger(1000)
    book.record(1, usage(1200))
    assert book.over_limit() == (1,)
    assert book.tokens_total_series == 1200, "the real number survives the finding"


def test_every_over_run_is_listed_rather_than_the_first() -> None:
    """Asked before a submission, where the useful answer is the full list — stopping at
    the earliest turns one review into six."""
    book = ledger(100)
    for number, spent in ((1, 500), (2, 50), (3, 500)):
        book.record(number, usage(spent))
    assert book.over_limit() == (1, 3)


def test_a_series_within_the_limit_reports_no_over_runs() -> None:
    book = ledger(200_000)
    book.record(1, usage(10))
    assert book.over_limit() == ()


def test_usage_exactly_at_the_limit_is_not_an_over_run() -> None:
    """The agreed figure is a ceiling that may be reached. An off-by-one here reports a
    compliant game as a breach, which is a false statement in the direction that costs the
    opponent's trust in every other number we send."""
    book = ledger(1000)
    book.record(1, usage(1000))
    assert book.over_limit() == ()


def test_a_non_positive_agreed_limit_is_refused() -> None:
    with pytest.raises(TokenLedgerError, match="must be positive"):
        TokenLedger(max_tokens_per_game=0)


# --- the report ---------------------------------------------------------------------------------


def test_the_report_carries_both_figures_and_the_evidence_behind_them() -> None:
    book = ledger(1000)
    book.record(1, usage(400))
    book.record(2, usage(1200))
    assert book.report() == {"max_tokens_per_game": 1000,
                             "per_sub_game": {1: 400, 2: 1200},
                             "tokens_total_series": 1600,
                             "sub_games_over_limit": [2]}


def test_a_series_with_no_recorded_usage_is_refused_rather_than_reported_as_zero() -> None:
    """Zero tokens and no measurement are different claims, and only one is reportable."""
    with pytest.raises(TokenLedgerError, match="AE-54"):
        ledger(1000).report()


# --- reading usage off a provider response ----------------------------------------------------


@pytest.mark.parametrize(("prompt_key", "completion_key"),
                         [("prompt_tokens", "completion_tokens"),
                          ("input_tokens", "output_tokens")])
def test_usage_is_read_from_either_provider_naming(prompt_key, completion_key) -> None:
    """Two providers, two names for the same number. Supporting one silently reports zero
    for the other."""
    assert usage_from_response({"usage": {prompt_key: 10, completion_key: 5}}).total == 15


def test_a_response_with_no_usage_block_is_refused_rather_than_counted_as_zero() -> None:
    """**A provider that stopped returning usage looks exactly like a game that used no
    tokens**, and the second is a figure we would report to the league as fact."""
    with pytest.raises(TokenLedgerError, match="AE-54"):
        usage_from_response({"choices": []})


@pytest.mark.parametrize("broken", [{"prompt_tokens": "many", "completion_tokens": 5},
                                    {"prompt_tokens": 5}, {}])
def test_a_usage_block_without_integer_counts_is_refused(broken: dict) -> None:
    """A partial block is the shape a provider change actually takes — one field renamed,
    the other left alone — and reading the survivor alone halves the reported figure."""
    with pytest.raises(TokenLedgerError, match="no integer token counts"):
        usage_from_response({"usage": broken})
