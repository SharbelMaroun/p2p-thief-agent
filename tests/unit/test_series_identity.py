"""The identifier every artifact in a series is named from (`AF-021`, Appendix F t20).

The defect these pin cost a counted game. This side derived `game_id` as
`game-<config sha[:12]>` and `game_uid` as `sha[:32]`, while the companion Cop -- fixed
earlier the same day -- used the agreed `G00N` label and the shared UUID. `G009` therefore
produced `log_game-5a7b4a6e58be_g01.json` here and `config_G009_g02.json` there: one
series, two naming schemes, and a result report that would have linked six files of which
three existed. Both halves are written by repositories that cannot see each other, so the
agreement has to be asserted rather than assumed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p2p_thief_agent.protocol.terms_projection import terms_from_shared_config
from p2p_thief_agent.reporting.naming import (
    config_filename,
    declaration_filename,
    log_filename,
)
from p2p_thief_agent.shared.series_identity import derive_game_uid, series_game_id

MATCH = Path(__file__).resolve().parents[2] / "config" / "match_friendly_uohay26.json"


def test_series_game_id_is_the_agreed_label() -> None:
    assert series_game_id({"game": {"series_game_id": "G009"}}) == "G009"
    assert series_game_id({"game": {"series_game_id": "  G009  "}}) == "G009"


@pytest.mark.parametrize("config", [
    {}, {"game": {}}, {"game": {"series_game_id": ""}}, {"game": {"series_game_id": "   "}},
])
def test_series_game_id_refuses_rather_than_defaulting(config: dict) -> None:
    """A missing label must fail at launch, not produce a digest-named set at grading."""
    with pytest.raises(ValueError, match="series_game_id"):
        series_game_id(config)


def test_every_artifact_in_the_set_is_named_from_the_one_label() -> None:
    """The whole point: four filenames, one identifier, no digest anywhere."""
    game_id = "G009"
    names = [declaration_filename(game_id), config_filename(game_id, 1),
             log_filename(game_id, 1), log_filename(game_id, 6)]
    assert names == ["declaration_G009.json", "config_G009_g01.json",
                     "log_G009_g01.json", "log_G009_g06.json"]
    assert not any("game-" in name for name in names)


def test_game_uid_matches_the_value_the_other_two_implementations_derive() -> None:
    """Pinned to the UUID the companion Cop and `uoh-ay26` both computed independently.

    Not a golden-value test for its own sake: this constant is the evidence that three
    separate implementations agree, which is the only thing that makes `game_uid` usable as
    the shared identifier the four artifacts are meant to carry. If this fails, our uid has
    drifted from the league's and the artifacts stop being cross-checkable.
    """
    terms = terms_from_shared_config(json.loads(MATCH.read_text(encoding="utf-8")))
    assert derive_game_uid(terms, ["sharNamr", "uoh-ay26"]) == (
        "7b1d942e-5a9c-6e0c-312a-761dd7dec131")


def test_game_uid_is_order_independent_across_the_group_pair() -> None:
    """Both peers must reach it without agreeing who is 'first' -- the pair is sorted."""
    terms = terms_from_shared_config(json.loads(MATCH.read_text(encoding="utf-8")))
    assert derive_game_uid(terms, ["sharNamr", "uoh-ay26"]) == derive_game_uid(
        terms, ["uoh-ay26", "sharNamr"])
