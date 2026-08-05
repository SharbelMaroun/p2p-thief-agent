"""Orchestrate the accepted six-sub-game series for the Thief role (`M7-001`).

A *meeting* between two teams is six sub-games under one series identity (`AF-t18`). The
teams alternate roles across them: `U-021` fixes the schedule as sub-games 1, 3, 5 in the
natural role and 2, 4, 6 swapped, with the Thief moving first. This repository runs the Thief
role, so it plays whichever sub-games its team is the Thief in — an **injected** schedule, so
a later correction to `U-021` is a one-line change rather than a code edit (`C-012`).

Each sub-game carries its `sub_game_number` into the result, and the per-sub-game Thief scores
(Appendix F table 17) sum to the cumulative series score. A *cumulative* tie between the two
teams' totals is settled at reporting time (`M7-017`); the tie **award** itself is the table's
`TIE_SCORE`, already what `thief_score(Outcome.TIE)` pays.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from p2p_thief_agent.state.scoring import Outcome, thief_score

NUM_SUB_GAMES = 6  # Appendix F table 18: games in a series against one opponent
# `U-021` role schedule — the sub-games this team plays as Thief. Injected/overridable.
THIEF_SUBGAMES_NATURAL = (1, 3, 5)
THIEF_SUBGAMES_SWAPPED = (2, 4, 6)

# Play one Thief sub-game identified by its number, returning its terminal outcome.
PlaySubGame = Callable[[int], Outcome]


class SeriesError(ValueError):
    """Raised when a series is misconfigured."""


@dataclass(frozen=True, slots=True)
class SubGameResult:
    """One sub-game's place in the series: its number, its outcome, and its Thief points."""

    sub_game_number: int
    outcome: Outcome
    score: int


@dataclass(frozen=True, slots=True)
class SeriesResult:
    """A series under one identity: the per-sub-game lines and their cumulative Thief score."""

    series_id: str
    sub_games: tuple[SubGameResult, ...]
    cumulative_score: int


def run_thief_series(
    series_id: str, thief_subgames: Sequence[int], play: PlaySubGame
) -> SeriesResult:
    """Run this team's Thief sub-games under one identity and aggregate the score (`M7-001`)."""
    if not series_id:
        raise SeriesError("series_id must be non-empty")
    if not thief_subgames:
        raise SeriesError("a series must contain at least one Thief sub-game")
    if any(not 1 <= number <= NUM_SUB_GAMES for number in thief_subgames):
        raise SeriesError(f"sub-game numbers must be in 1..{NUM_SUB_GAMES}")
    if len(set(thief_subgames)) != len(thief_subgames):
        raise SeriesError("sub-game numbers must be distinct")
    results = tuple(
        SubGameResult(number, outcome := play(number), thief_score(outcome))
        for number in thief_subgames
    )
    return SeriesResult(series_id, results, sum(result.score for result in results))


def is_cumulative_tie(our_total: int, their_total: int) -> bool:
    """Return whether the two teams' series totals are level — a cumulative tie (`M7-001d`)."""
    return our_total == their_total
