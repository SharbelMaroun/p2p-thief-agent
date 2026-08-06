"""`M7-017`: what a first win is worth, and how the series total is arrived at.

Split from `test_league_ledger.py` because the consequences differ. A wrong game *count*
disqualifies the project under rule 38; a wrong *bonus* costs 10 Fixed points, and a series
total that contradicts its own sub-game lines scores 0 for **both** groups under rule 35.

The failure modes tested here: a diversity bonus paid for a first loss, paid twice to the
same opponent, or spent by a warm-up that never counted; and a total carried forward
instead of recomputed from the lines that justify it.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.reporting.league_ledger import (
    DIVERSITY_REWARD,
    LeagueLedgerError,
    PlayedGame,
    diversity_reward,
    series_total,
)


def played(opponent: str, *, counted: bool = True, won: bool = False) -> PlayedGame:
    return PlayedGame(game_id=f"g-vs-{opponent}", opponent_group_id=opponent,
                      counted=counted, won=won)


# --- M7-017b: the diversity reward -----------------------------------------------------------


def test_a_win_against_a_new_opponent_earns_the_diversity_reward() -> None:
    """Appendix F, Fixed: 10 points for a win against an opponent not played before."""
    assert diversity_reward([played("other")], "rival", won=True) == DIVERSITY_REWARD


def test_a_loss_against_a_new_opponent_earns_nothing() -> None:
    """The row is "reward for a **win** against a new opponent" — novelty alone pays 0."""
    assert diversity_reward([], "rival", won=False) == 0


def test_a_win_against_a_familiar_opponent_earns_nothing() -> None:
    """Rule 52: repeat games against the same opponent do not accumulate score."""
    assert diversity_reward([played("rival")], "rival", won=True) == 0


def test_a_previous_warm_up_does_not_spend_the_novelty() -> None:
    """The subtle one. A warm-up is not a counted game, so the first *counted* meeting is
    still a first meeting — treating it otherwise would forfeit 10 Fixed points."""
    assert diversity_reward([played("rival", counted=False)], "rival",
                            won=True) == DIVERSITY_REWARD


# --- M7-017a: the series total is recomputed ------------------------------------------------


def test_the_series_total_is_recomputed_from_the_stored_sub_games() -> None:
    """Rule 54 wants tokens per game *and* per series; rule 35 scores a contradicting
    report 0 for both groups, so the total must be reproducible from the lines."""
    total = series_total([{"score": 10, "tokens": 100}, {"score": 15, "tokens": 250}])
    assert total == {"sub_games": 2, "total_score": 25, "tokens_total_series": 350}


def test_a_missing_score_or_token_count_reads_as_zero_rather_than_crashing() -> None:
    """A partially written sub-game line should still produce an auditable total; the gap
    shows up as a low number the operator can see, not an exception at report time."""
    assert series_total([{"score": 10}])["tokens_total_series"] == 0


def test_a_series_with_no_sub_games_is_refused_rather_than_reported_as_zero() -> None:
    """A zero total and an empty series are different claims. Reporting the first for the
    second is the contradiction rule 35 punishes."""
    with pytest.raises(LeagueLedgerError, match="no sub-games"):
        series_total([])
