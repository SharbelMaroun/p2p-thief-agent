"""`M7-002a`–`d`/`f`/`g`: the four artifact builders (U-019-provisional, documented shape)."""

import pytest

from p2p_thief_agent.reporting.config_artifact import build_config
from p2p_thief_agent.reporting.declaration import build_declaration
from p2p_thief_agent.reporting.log_artifact import build_log
from p2p_thief_agent.reporting.naming import ArtifactError, MatchIdentity
from p2p_thief_agent.reporting.result_artifact import build_result

ID = MatchIdentity("g42", "uid-9")
HARDWARE = {"cpu_type": "x", "cpu_freq_mhz": 3000, "cpu_cores": 8,
            "ram_gb": 16, "gpu_model": "none", "vram_gb": 0}


def group(gid: str, cop: str, thief: str) -> dict:
    return {"group_id": gid, "group_name": gid, "members": ["m"],
            "repos": {"cop": cop, "thief": thief}, "mcp_servers": {},
            "llm_model": "template", "hardware_spec": HARDWARE, "signature": "sig"}


GROUPS = [group("sharNamr", "https://c1", "https://t1"), group("opp", "https://c2", "https://t2")]
SECTIONS = {name: {"k": 1} for name in
            ("board_and_agents", "world", "movement_and_barriers", "scoring", "pheromones",
             "network_and_league", "rate_limiter_gatekeeper")}
SUBGAME = {"sub_game_number": 1, "roles": {}, "started_at": "t0", "ended_at": "t1",
           "result": "survival", "winner_group": "sharNamr", "tie": False,
           "github_commit": "a" * 40, "tokens": 0, "score": 10, "log_files": [], "audit": {}}
FINAL = {"total_score": 25, "sub_games_won": 3, "ties": 0, "winner_group": "sharNamr",
         "series_tie": False, "tokens_total_series": 0}
SUMMARY = dict.fromkeys(
    ("sub_game_number", "group_id", "role", "opponent_group_id", "result", "winner_role",
     "steps", "timezone", "started_at", "ended_at", "duration_seconds", "tokens_total", "audit"),
    0,
)
RECORD = {"payload": {"step": 1}, "nonce": "n", "commit": "c"}


def test_the_declaration_carries_the_documented_top_level_and_shared_uid() -> None:
    art = build_declaration(identity=ID, groups=GROUPS, num_sub_games=6, max_tokens_per_game=1000,
                            timezone="UTC", started_at="t0", ended_at="t1", links={})
    assert art["_schema"] == "declaration" and art["game_uid"] == "uid-9"
    assert set(art["groups"][0]) >= {"hardware_spec", "signature", "repos"}


def test_a_declaration_group_missing_hardware_is_rejected() -> None:
    broken = [{**GROUPS[0], "hardware_spec": {"cpu_type": "x"}}, GROUPS[1]]
    with pytest.raises(ArtifactError, match="hardware_spec missing"):
        build_declaration(identity=ID, groups=broken, num_sub_games=6, max_tokens_per_game=1,
                          timezone="UTC", started_at="t0", ended_at="t1", links={})


def test_the_config_locks_its_content_with_a_sha256() -> None:
    art = build_config(identity=ID, sub_game_number=3, agreed_between=["sharNamr", "opp"],
                       sections=SECTIONS, links={}, config_name="cfg")
    assert len(art["config_sha256"]) == 64 and art["sub_game_number"] == 3
    assert art["game_uid"] == "uid-9" and "scoring" in art


def test_the_log_carries_the_commit_reveal_records() -> None:
    art = build_log(identity=ID, summary=SUMMARY, records=[RECORD],
                    mutual_agreement={"opponent_group_id": "opp", "sha256": "s", "confirmed": True},
                    links={})
    assert art["records"][0] == RECORD and art["game_uid"] == "uid-9"


def test_the_result_carries_four_repo_links_and_per_game_commit_and_tokens() -> None:
    art = build_result(identity=ID, groups=GROUPS, sub_games=[SUBGAME], final_result=FINAL,
                       timezone="UTC", mutual_agreement={"sha256": "s", "confirmed": True})
    assert len(art["links"]["repositories"]) == 4  # M7-002f: two per group
    assert art["sub_games"][0]["github_commit"] and art["sub_games"][0]["tokens"] == 0  # M7-002g


def test_a_result_missing_the_per_game_commit_is_rejected() -> None:
    no_commit = {k: v for k, v in SUBGAME.items() if k != "github_commit"}
    with pytest.raises(ArtifactError, match="github_commit"):
        build_result(identity=ID, groups=GROUPS, sub_games=[no_commit], final_result=FINAL,
                     timezone="UTC", mutual_agreement={"sha256": "s", "confirmed": True})


def test_an_empty_declaration_or_log_is_rejected() -> None:
    with pytest.raises(ArtifactError, match="at least one group"):
        build_declaration(identity=ID, groups=[], num_sub_games=6, max_tokens_per_game=1,
                          timezone="UTC", started_at="t0", ended_at="t1", links={})
    with pytest.raises(ArtifactError, match="at least one step"):
        build_log(identity=ID, summary=SUMMARY, records=[],
                  mutual_agreement={"opponent_group_id": "opp", "sha256": "s", "confirmed": True},
                  links={})


def test_config_rejects_a_bad_sub_game_number_or_participant_count() -> None:
    with pytest.raises(ArtifactError, match="sub_game_number"):
        build_config(identity=ID, sub_game_number=7, agreed_between=["a", "b"],
                     sections=SECTIONS, links={}, config_name="cfg")
    with pytest.raises(ArtifactError, match="exactly two"):
        build_config(identity=ID, sub_game_number=1, agreed_between=["a"],
                     sections=SECTIONS, links={}, config_name="cfg")


def test_result_rejects_wrong_group_count_or_missing_links() -> None:
    with pytest.raises(ArtifactError, match="exactly two groups"):
        build_result(identity=ID, groups=[GROUPS[0]], sub_games=[SUBGAME], final_result=FINAL,
                     timezone="UTC", mutual_agreement={"sha256": "s", "confirmed": True})
    no_repos = [{**GROUPS[0], "repos": {}}, GROUPS[1]]
    with pytest.raises(ArtifactError, match="four repository links"):
        build_result(identity=ID, groups=no_repos, sub_games=[SUBGAME], final_result=FINAL,
                     timezone="UTC", mutual_agreement={"sha256": "s", "confirmed": True})
