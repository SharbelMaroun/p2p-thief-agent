"""`M7-007` / `M7-010`: the number of games we declare having played.

Rule 38's sanction is **absolute disqualification of the project** for a false declaration
of games played, and it does not distinguish a lie from an arithmetic mistake. That makes
this the highest-consequence arithmetic in the repository, so the tests below are written
against the failure modes rather than the happy path: a warm-up counted as a real game
(over-declares), and a real game filed as a warm-up after seeing the score (under-declares
— the shape rule 38 actually describes).

Scoring lives next door in `test_league_scoring.py`; the seam is that a wrong count
disqualifies the project while a wrong bonus costs points.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.reporting.league_ledger import (
    LeagueLedgerError,
    PlayedGame,
    check_declared_count,
    declare_games_played,
    games_against,
)


def played(opponent: str, *, counted: bool = True, won: bool = False) -> PlayedGame:
    return PlayedGame(game_id=f"g-vs-{opponent}", opponent_group_id=opponent,
                      counted=counted, won=won)


def result(opponent: str, *, winner: str | None = None, **extra) -> dict:
    return {"game_id": f"g-vs-{opponent}", "our_group_id": "sharNamr",
            "mutual_agreement": {"opponent_group_id": opponent},
            "final_result": {"winner_group": winner}, **extra}


# --- M7-007: the count comes from the artifacts, not from a tally ---------------------------


def test_the_count_is_read_from_a_result_artifact() -> None:
    """Rule 38 does not distinguish a lie from a mistake, so the number we declare is
    derived from the files the lecturer will also receive."""
    game = PlayedGame.from_result(result("rival"))
    assert game.opponent_group_id == "rival"
    assert game.counted is True


def test_a_result_naming_no_opponent_is_refused_rather_than_counted_as_zero() -> None:
    """An unattributed game cannot be counted against anyone, and silently dropping it
    under-declares — which is the direction rule 38 disqualifies for."""
    orphan = {"game_id": "g-1", "final_result": {}}
    with pytest.raises(LeagueLedgerError, match="names no opponent"):
        PlayedGame.from_result(orphan)


def test_a_result_with_no_counted_flag_is_treated_as_a_counted_game() -> None:
    """**Deliberately asymmetric.** Over-declaring is safe; under-declaring is the false
    declaration. A missing flag is far more likely a counted game than an unlabelled
    warm-up, so the unsafe direction needs the explicit statement."""
    assert PlayedGame.from_result(result("rival")).counted is True


def test_a_win_is_recognised_only_when_we_are_the_named_winner() -> None:
    assert PlayedGame.from_result(result("rival", winner="sharNamr")).won is True
    assert PlayedGame.from_result(result("rival", winner="rival")).won is False
    assert PlayedGame.from_result(result("rival")).won is False


# --- M7-007a / M7-007b / M7-010: warm-ups do not count ---------------------------------------


def test_warm_up_games_are_excluded_from_the_count() -> None:
    """Rule 52 / `:2028`: "warm-up games that do not count are permitted"."""
    history = [played("rival"), played("rival", counted=False), played("other")]
    assert games_against(history, "rival") == 1


def test_the_declaration_reports_the_count_including_the_game_about_to_be_played() -> None:
    """Rule 37 is "at the start of each game", so the number an opponent hears has to
    include the one we are opening — otherwise both sides declare different totals for the
    same match."""
    block = declare_games_played([played("rival"), played("other")], "rival")
    assert block["games_played_including_this"] == 2
    assert block["counted_games_before_this"] == 1
    assert block["first_meeting_between_groups"] is False


def test_a_first_meeting_is_declared_as_such() -> None:
    block = declare_games_played([played("other")], "rival")
    assert block["games_played_including_this"] == 1
    assert block["first_meeting_between_groups"] is True


def test_the_declaration_shows_how_many_warm_ups_were_excluded() -> None:
    """Shown rather than hidden. A count that silently drops games is indistinguishable
    from a count that is simply wrong, and the opponent cannot audit what it cannot see."""
    block = declare_games_played([played("rival", counted=False)] * 2, "rival")
    assert block["warm_ups_excluded"] == 2
    assert block["games_played_including_this"] == 1


def test_a_declared_count_that_disagrees_with_the_artifacts_is_refused() -> None:
    """`M7-010`. The check exists here because rule 38's sanction lands on the **project**,
    not the game — there is no recovering from it after the fact."""
    with pytest.raises(LeagueLedgerError, match="AE-38"):
        check_declared_count(5, [played("rival")], "rival")


def test_a_declared_count_matching_the_artifacts_passes_quietly() -> None:
    check_declared_count(2, [played("rival"), played("rival", counted=False)], "rival")
