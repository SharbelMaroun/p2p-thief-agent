"""`M7-008b`: any past game's config can be retrieved from what is committed.

The retrieval half is what makes retention checkable. A store with no reader is a claim that
files exist somewhere; this is the operation an auditor actually performs when asked to
reproduce a game, so it is the one worth testing.

`missing_configs` answers the question asked *before* a submission rather than after, and it
returns rather than raises — the useful answer there is the full list of gaps to fill, since
stopping at the first turns one review into six.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.reporting.naming import MatchIdentity
from p2p_thief_agent.reporting.retention import (
    RetentionError,
    missing_configs,
    retrieve_config,
    store_config,
    stored_games,
)

IDENTITY = MatchIdentity(game_id="demo-vs-rival", game_uid="u" * 32)
SERIES = (1, 2, 3, 4, 5, 6)
CONFIG = {"_schema": "config", "scoring": {"capture": -10}, "config_sha256": "a" * 64,
          "pheromones": {"decay": 0.9, "deposit": 0.62}}


def test_a_stored_config_round_trips(tmp_path) -> None:
    """Byte-for-byte through JSON, because the point of committing it is that somebody can
    replay the game from exactly these parameters."""
    store_config(tmp_path, IDENTITY, 2, CONFIG)
    assert retrieve_config(tmp_path, IDENTITY.game_id, 2) == CONFIG


def test_each_sub_game_retrieves_its_own_terms(tmp_path) -> None:
    """The failure a single-file-per-match layout produces: a later sub-game's negotiated
    terms silently answering for an earlier one."""
    for number in SERIES:
        store_config(tmp_path, IDENTITY, number, {**CONFIG, "sub_game_number": number})
    for number in SERIES:
        assert retrieve_config(tmp_path, IDENTITY.game_id, number)["sub_game_number"] == number


def test_retrieving_a_config_that_was_never_committed_says_which_game(tmp_path) -> None:
    """Named in the error, because "not found" against six sub-games and several matches is
    the start of a search rather than an answer."""
    with pytest.raises(RetentionError, match="sub-game 4"):
        retrieve_config(tmp_path, "demo-vs-rival", 4)


def test_stored_games_lists_every_match_with_a_committed_config(tmp_path) -> None:
    store_config(tmp_path, IDENTITY, 1, CONFIG)
    store_config(tmp_path, MatchIdentity("older-match", "z" * 32), 1, CONFIG)
    assert stored_games(tmp_path) == ("demo-vs-rival", "older-match")


def test_stored_games_on_a_repository_with_no_games_yet_is_empty(tmp_path) -> None:
    """Empty, not an error. A fresh clone before the first game is a normal state, and a
    raise here would make the pre-submission check fail loudest when it has least to say."""
    assert stored_games(tmp_path) == ()


def test_missing_configs_reports_every_gap_rather_than_the_first(tmp_path) -> None:
    store_config(tmp_path, IDENTITY, 1, CONFIG)
    store_config(tmp_path, IDENTITY, 4, CONFIG)
    assert missing_configs(tmp_path, IDENTITY.game_id, SERIES) == (2, 3, 5, 6)


def test_a_complete_series_reports_no_gaps(tmp_path) -> None:
    for number in SERIES:
        store_config(tmp_path, IDENTITY, number, CONFIG)
    assert missing_configs(tmp_path, IDENTITY.game_id, SERIES) == ()


def test_a_match_with_nothing_committed_reports_every_sub_game_missing(tmp_path) -> None:
    """The state after a series that ran and never stored anything — which is what the
    repository looked like before this module existed."""
    assert missing_configs(tmp_path, "never-stored", SERIES) == SERIES
