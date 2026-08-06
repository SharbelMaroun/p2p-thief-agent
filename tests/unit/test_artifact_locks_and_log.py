"""`M7-021` / `M7-022`: the config's locks, and the log an outsider can re-verify.

Split from `test_artifact_contents.py`, which covers the declaration. The seam is real:
that file asks *who is playing*, this asks *under what terms* and *what happened* — and the
two carry different sanctions. A missing declaration field costs a computational bonus; a
missing lock cancels the game (rule 23) and a missing nonce disqualifies for dictionary
attack (rule 18).

**`M7-022b` is the one that cannot be checked after the fact.** Rule 18 requires nonces kept
secret until the end, and a finished log is byte-identical whether the nonces were written
at the end or leaked at step one. Only refusing to *build* the forbidden intermediate state
enforces it, which is what `build_log` does and what is asserted here.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.reporting.config_artifact import build_config
from p2p_thief_agent.reporting.log_artifact import build_log
from p2p_thief_agent.reporting.naming import ArtifactError, MatchIdentity

ID = MatchIdentity(game_id="demo-vs-rival", game_uid="u" * 32)
AGREEMENT = {"confirmed": True, "opponent_group_id": "rival", "sha256": "f" * 64}
QUANTITATIVE = ("board_and_agents", "movement_and_barriers", "scoring", "pheromones",
                "network_and_league", "rate_limiter_gatekeeper")
SECTIONS = {name: {"k": 1} for name in (*QUANTITATIVE, "world")}
SUMMARY = {**dict.fromkeys(
    ("sub_game_number", "group_id", "role", "opponent_group_id", "result", "winner_role",
     "steps", "timezone", "started_at", "duration_seconds", "tokens_total", "audit"), 0),
    "ended_at": "2026-08-07T12:00:00+03:00"}


def config(**overrides):
    kwargs = {"identity": ID, "sub_game_number": 1,
              "agreed_between": ["sharNamr", "rival"], "sections": SECTIONS,
              "links": {}, "config_name": "config_demo-vs-rival_g01.json"}
    return build_config(**{**kwargs, **overrides})


def record(step: int, **extra) -> dict:
    return {"payload": {"step": step, "move": "N", "intent": True},
            "nonce": f"{step:032x}", "commit": f"{step:064x}",
            "hint": "past the market", **extra}


def log(**overrides):
    kwargs = {"identity": ID, "summary": SUMMARY, "links": {},
              "mutual_agreement": AGREEMENT, "records": [record(1), record(2)]}
    return build_log(**{**kwargs, **overrides})


# --- M7-021: the config binds the negotiated match ----------------------------------------


@pytest.mark.parametrize("section", QUANTITATIVE)
def test_every_appendix_f_quantitative_section_is_present(section: str) -> None:
    """`M7-021a`. Named one per section so a failure says which is missing — "the config is
    incomplete" sends someone hunting through seven blocks."""
    assert section in config(), f"{section} is an Appendix F section and must be emitted"


def test_the_config_carries_its_own_hash_lock() -> None:
    """`M7-021b`, first lock. `:111` and rule 11: the configuration must be identical
    bit-for-bit on both sides, sanction "disqualification of the game due to lack of
    symmetry". The lock is what makes that checkable rather than asserted."""
    assert len(config()["config_sha256"]) == 64


def test_the_config_names_who_agreed_it() -> None:
    """A lock over terms nobody is named as agreeing is a hash of an anonymous document."""
    assert config()["agreed_between"] == ["sharNamr", "rival"]


def test_a_config_missing_a_quantitative_section_is_refused_at_build_time() -> None:
    """Refused where it is built. A config already written and shared cannot be recalled,
    and rule 11's sanction lands on the game, not on the file."""
    thin = {name: {"k": 1} for name in QUANTITATIVE[:3]}
    with pytest.raises(ArtifactError):
        config(sections=thin)


# --- M7-022: the log an outsider can re-verify ---------------------------------------------


def test_each_record_carries_its_commitment_and_revealed_payload() -> None:
    """`M7-022a`. Both halves, or the record proves nothing: a commitment with no payload
    cannot be checked, and a payload with no commitment was never bound to anything."""
    for entry in log()["records"]:
        assert entry["commit"] and entry["payload"]


def test_each_record_carries_its_hint_and_intent() -> None:
    """`M7-022c`. A hint without its intent flag cannot be judged — there would be no way
    to tell a bluff from a mistake, and rule 22 punishes only the lie."""
    for entry in log()["records"]:
        assert "hint" in entry
        assert "intent" in entry["payload"]


def test_the_mutual_agreement_rides_in_the_log() -> None:
    """Rule 36: a comprehensive mutual audit is "a mandatory condition before agreement on
    the JSON result", so the log has to carry the confirmation it produced."""
    assert log()["mutual_agreement"]["confirmed"] is True


def test_a_log_with_no_records_is_refused_rather_than_emitted_empty() -> None:
    """An empty log validates against any shape check and audits to nothing."""
    with pytest.raises(ArtifactError):
        log(records=[])


def test_a_log_for_a_game_still_in_play_is_refused_before_it_is_assembled() -> None:
    """**`M7-022b`, and the one guard that cannot be added later.** Every record carries its
    nonce, so building this artifact mid-game publishes them — rule 18's sanction is
    disqualification for enabling a dictionary attack. A finished log is byte-identical
    whether it was written at the end or leaked at step one, so refusing to build is the
    only place the rule is enforceable at all."""
    in_play = {**SUMMARY, "ended_at": ""}
    with pytest.raises(ArtifactError, match="AE-18"):
        log(summary=in_play)


def test_every_record_has_a_distinct_nonce() -> None:
    """`M7-022b`'s neighbour. A reused nonce across two steps collapses two commitments
    into one guess, which is the dictionary attack rule 18's sanction names."""
    nonces = [entry["nonce"] for entry in log()["records"]]
    assert len(set(nonces)) == len(nonces)
