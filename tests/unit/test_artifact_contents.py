"""`M7-012a-e`: every real builder produces an artifact that validates, as one match.

`test_artifact_schema.py` proves the *table* is honest — every required key cites a rule.
This proves the **builders satisfy it**, which is the different and more useful claim: a
schema nothing is checked against is a document, not a guard.

The per-artifact content requirements live next door, split by the sanction each carries:
`test_declaration_content.py` (`M7-020`, computational bonus) and
`test_artifact_locks_and_log.py` (`M7-021`/`M7-022`, game cancellation and rule 18).

The test worth reading here is the last one. Four artifacts can each validate perfectly and
still describe, between them, a match that never happened — the shape a rushed re-run
produces when one file is left over from the previous game (`AR-001`).
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.reporting.artifact_schema import (
    ArtifactSchemaError,
    check_shared_game_uid,
    validate_artifact,
)
from p2p_thief_agent.reporting.config_artifact import build_config
from p2p_thief_agent.reporting.declaration import build_declaration
from p2p_thief_agent.reporting.log_artifact import build_log
from p2p_thief_agent.reporting.naming import MatchIdentity
from p2p_thief_agent.reporting.result_artifact import build_result

ID = MatchIdentity(game_id="demo-vs-rival", game_uid="u" * 32)
COMMIT = "a" * 40
HARDWARE = {"os": "Windows 11", "cpu_type": "x86_64", "cpu_freq_mhz": 3000, "cpu_cores": 8,
            "ram_gb": 16, "gpu_model": "none", "vram_gb": 0}
AGREEMENT = {"confirmed": True, "opponent_group_id": "rival", "sha256": "f" * 64}
SECTIONS = {name: {"k": 1} for name in
            ("board_and_agents", "world", "movement_and_barriers", "scoring", "pheromones",
             "network_and_league", "rate_limiter_gatekeeper")}
SUMMARY = {**dict.fromkeys(
    ("sub_game_number", "group_id", "role", "opponent_group_id", "result", "winner_role",
     "steps", "timezone", "started_at", "duration_seconds", "tokens_total", "audit"), 0),
    "ended_at": "2026-08-07T12:00:00+03:00"}  # `M7-022b`: a log with no end time is refused
SUB_GAME = {"sub_game_number": 1, "roles": {}, "started_at": "t0", "ended_at": "t1",
            "result": "survival", "winner_group": "sharNamr", "tie": False,
            "github_commit": COMMIT, "tokens": 120, "score": 10, "log_files": [], "audit": {}}
FINAL = {"total_score": 25, "sub_games_won": 3, "ties": 0, "winner_group": "sharNamr",
         "series_tie": False, "tokens_total_series": 720}
RECORD = {"payload": {"step": 1, "move": "N", "intent": True}, "nonce": "n" * 32,
          "commit": "c" * 64, "hint": "past the market"}


def group(gid: str) -> dict:
    return {"group_id": gid, "group_name": gid, "members": ["student-1", "student-2"],
            "repos": {"cop": f"https://github.com/{gid}/cop",
                      "thief": f"https://github.com/{gid}/thief"},
            "mcp_servers": {"peer": f"https://{gid}.example.com/mcp"},
            "llm_model": "template-free", "hardware_spec": HARDWARE, "signature": "sig"}


GROUPS = [group("sharNamr"), group("rival")]


def artifacts() -> dict[str, dict]:
    return {
        "declaration": build_declaration(
            identity=ID, groups=GROUPS, num_sub_games=6, max_tokens_per_game=200_000,
            timezone="UTC", started_at="t0", ended_at="t1", links={},
            github_commit=COMMIT),
        "config": build_config(identity=ID, sub_game_number=1,
                               agreed_between=["sharNamr", "rival"], sections=SECTIONS,
                               links={}, config_name="config_demo-vs-rival_g01.json"),
        "log": build_log(identity=ID, summary=SUMMARY, links={},
                         mutual_agreement=AGREEMENT, records=[RECORD]),
        "result": build_result(identity=ID, groups=GROUPS, sub_games=[SUB_GAME],
                               final_result=FINAL, timezone="UTC",
                               mutual_agreement=AGREEMENT),
    }


@pytest.mark.parametrize("name", ["declaration", "config", "log", "result"])
def test_the_real_builder_produces_an_artifact_that_validates(name: str) -> None:
    """`M7-012a-d`. Parametrised so a failure names the artifact that broke rather than
    stopping the whole set at the first one."""
    validate_artifact(name, artifacts()[name])


def test_the_four_artifacts_of_one_match_share_a_game_uid() -> None:
    """`M7-012e` / `AR-001`, against the real builders rather than hand-written dicts."""
    assert check_shared_game_uid(artifacts()) == ID.game_uid


def test_an_artifact_from_another_match_breaks_the_set() -> None:
    """The realistic failure: one file left over from the previous game. Each validates;
    together they describe a match that never happened."""
    mixed = artifacts()
    mixed["log"] = build_log(identity=MatchIdentity("other", "z" * 32), summary=SUMMARY,
                             links={}, mutual_agreement=AGREEMENT, records=[RECORD])
    with pytest.raises(ArtifactSchemaError, match="game_uid"):
        check_shared_game_uid(mixed)
