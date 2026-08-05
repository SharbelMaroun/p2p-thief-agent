"""`M7-001`: orchestrate the six-sub-game series lifecycle for the Thief role."""

import pytest

from p2p_thief_agent.orchestration.series import (
    THIEF_SUBGAMES_NATURAL,
    THIEF_SUBGAMES_SWAPPED,
    SeriesError,
    is_cumulative_tie,
    run_thief_series,
)
from p2p_thief_agent.state.scoring import Outcome

OUTCOMES = {1: Outcome.SURVIVAL, 2: Outcome.CAPTURE, 3: Outcome.SURVIVAL,
            4: Outcome.TIE, 5: Outcome.CAPTURE, 6: Outcome.TECHNICAL_LOSS}


def play(number: int) -> Outcome:
    return OUTCOMES[number]


def test_a_natural_series_runs_its_thief_sub_games_under_one_identity() -> None:
    """`M7-001a`/`M7-001c`: sub-games 1, 3, 5 carried and their Thief scores summed (10+10+5)."""
    result = run_thief_series("game-42", THIEF_SUBGAMES_NATURAL, play)
    assert result.series_id == "game-42"
    assert [s.sub_game_number for s in result.sub_games] == [1, 3, 5]
    assert [s.score for s in result.sub_games] == [10, 10, 5]
    assert result.cumulative_score == 25


def test_the_swapped_schedule_is_injected_not_hard_coded() -> None:
    """`M7-001b`: the same orchestrator runs the 2, 4, 6 schedule when injected."""
    result = run_thief_series("game-42", THIEF_SUBGAMES_SWAPPED, play)
    assert [s.sub_game_number for s in result.sub_games] == [2, 4, 6]
    assert result.cumulative_score == 5 + 2 + 0  # capture 5, tie 2, technical loss 0


@pytest.mark.parametrize("bad", ["", None])
def test_an_empty_series_id_is_rejected(bad: object) -> None:
    with pytest.raises(SeriesError, match="series_id"):
        run_thief_series(bad, THIEF_SUBGAMES_NATURAL, play)


@pytest.mark.parametrize("bad", [(), (0, 1), (1, 7), (1, 1, 3)])
def test_a_malformed_schedule_is_rejected(bad: tuple) -> None:
    with pytest.raises(SeriesError):
        run_thief_series("game-42", bad, play)


def test_a_cumulative_tie_is_detected() -> None:
    """`M7-001d`: two level series totals are a cumulative tie."""
    assert is_cumulative_tie(25, 25) is True
    assert is_cumulative_tie(25, 20) is False
