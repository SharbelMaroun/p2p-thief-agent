"""`M7-009`: token counts per game and per series, both defensible (rule 54).

Rule 54 wants both figures and they are different claims. The series total is what the
league compares; the per-game count is what shows the agreed limit was respected in the game
where it mattered. A ledger keeping only the total cannot answer the second question after
the fact; one keeping only per-game figures makes the total somebody's arithmetic.

The tests are weighted towards the two ways this number goes quietly wrong — a per-game
counter reset in the same place a crash interrupts, and a retried sub-game summed into its
first attempt. The agreed limit and provider-usage reading live in `test_token_limits.py`.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.reporting.token_ledger import TokenLedger, TokenLedgerError, TokenUsage

LIMIT = 200_000


def ledger(limit: int = LIMIT) -> TokenLedger:
    return TokenLedger(max_tokens_per_game=limit)


def usage(total: int) -> TokenUsage:
    return TokenUsage(prompt=total // 2, completion=total - total // 2)


# --- rule 54 wants both figures ---------------------------------------------------------------


def test_both_the_per_game_and_series_figures_are_available() -> None:
    book = ledger()
    book.record(1, usage(1000))
    book.record(2, usage(2000))
    assert book.tokens_for(1) == 1000
    assert book.tokens_total_series == 3000


def test_the_series_total_is_derived_rather_than_carried() -> None:
    """Nothing to forget to carry. A stored total can drift from the entries that justify
    it, and rule 35 punishes exactly that contradiction — 0 for both groups."""
    book = ledger()
    for number in range(1, 7):
        book.record(number, usage(100))
    assert book.tokens_total_series == 600
    book.amend(3, usage(400))
    assert book.tokens_total_series == 900, "the total tracked the amendment"


def test_the_ledger_does_not_reset_between_sub_games() -> None:
    """The obvious implementation zeroes a counter at each sub-game start, and that reset
    sits in the same place a crash or a role swap interrupts."""
    book = ledger()
    book.record(1, usage(500))
    book.record(6, usage(500))
    assert book.tokens_total_series == 1000


def test_usage_splits_prompt_from_completion_so_an_over_run_can_be_attributed() -> None:
    assert TokenUsage(prompt=700, completion=300).total == 1000


def test_iterating_yields_sub_games_in_order() -> None:
    book = ledger()
    book.record(3, usage(30))
    book.record(1, usage(10))
    assert [number for number, _ in book] == [1, 3]


# --- the retry that inflates the count ---------------------------------------------------------


def test_recording_a_sub_game_twice_is_refused_rather_than_summed() -> None:
    """**The realistic corruption.** Replaying a sub-game after a disconnection is a real
    scenario, and adding the second attempt to the first inflates a figure rule 54 requires
    to be accurate."""
    book = ledger()
    book.record(1, usage(1000))
    with pytest.raises(TokenLedgerError, match="AE-54"):
        book.record(1, usage(1000))


def test_a_replayed_sub_game_is_amended_deliberately() -> None:
    """The caller has to say which it means. Both readings are legitimate; only one of them
    can be the silent default."""
    book = ledger()
    book.record(1, usage(1000))
    book.amend(1, usage(1500))
    assert book.tokens_total_series == 1500


def test_amending_a_sub_game_that_was_never_recorded_is_refused() -> None:
    """An amend that quietly creates the entry would let a typo'd sub-game number add a
    game that was never played."""
    with pytest.raises(TokenLedgerError, match="no entry to amend"):
        ledger().amend(4, usage(10))


def test_reading_a_sub_game_with_no_recorded_usage_is_refused() -> None:
    with pytest.raises(TokenLedgerError, match="no recorded usage"):
        ledger().tokens_for(2)


def test_a_negative_token_count_is_refused() -> None:
    with pytest.raises(TokenLedgerError, match="cannot be negative"):
        TokenUsage(prompt=-1, completion=0)
