"""`M7-002e`: the four artifacts share one identity and derive their names from `game_id`.

Only the book-confirmed naming (`AF-021`) and shared `game_uid` (`AR-001`) are tested; the
artifact field schemas are `U-019` and not built here.
"""

import pytest

from p2p_thief_agent.reporting.naming import (
    ArtifactError,
    MatchIdentity,
    config_filename,
    declaration_filename,
    log_filename,
    match_filenames,
    result_filename,
)

IDENTITY = MatchIdentity(game_id="uoh26-sharNamr-vs-x", game_uid="9f3c-uid")


def test_the_filenames_derive_from_the_game_id() -> None:
    assert declaration_filename("g42") == "declaration_g42.json"
    assert result_filename("g42") == "result_g42.json"
    assert config_filename("g42", 3) == "config_g42_g03.json"
    assert log_filename("g42", 6) == "log_g42_g06.json"


def test_a_match_derives_every_filename_from_one_game_id() -> None:
    names = match_filenames(IDENTITY, [1, 3, 5])
    assert names["declaration"] == "declaration_uoh26-sharNamr-vs-x.json"
    assert names["result"] == "result_uoh26-sharNamr-vs-x.json"
    assert names["configs"] == [
        "config_uoh26-sharNamr-vs-x_g01.json",
        "config_uoh26-sharNamr-vs-x_g03.json",
        "config_uoh26-sharNamr-vs-x_g05.json",
    ]
    assert names["logs"][0] == "log_uoh26-sharNamr-vs-x_g01.json"


def test_an_empty_identity_is_rejected() -> None:
    with pytest.raises(ArtifactError, match="non-empty"):
        MatchIdentity(game_id="", game_uid="u")


@pytest.mark.parametrize("bad", [0, 7])
def test_an_out_of_range_sub_game_number_is_rejected(bad: int) -> None:
    with pytest.raises(ArtifactError, match="sub_game_number"):
        config_filename("g42", bad)


def test_a_match_needs_at_least_one_sub_game() -> None:
    with pytest.raises(ArtifactError, match="at least one"):
        match_filenames(IDENTITY, [])
