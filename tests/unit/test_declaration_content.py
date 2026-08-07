"""`M7-020`: what the declaration must actually carry, against the real builder.

`test_artifact_schema.py` proves the *table* is honest — every required key cites a rule.
`test_artifact_contents.py` proves the four builders satisfy it. This proves the
declaration's own mandated content, one test per element:

* `M7-020a-c` — both groups with their members, both repository links per group, and the
  MCP addresses in use;
* `M7-020d` — the hardware and model declaration (rule 24, sanction "denial of eligibility
  for computational bonuses" — so an incomplete spec costs points, not tidiness);
* `M7-020e` — the agreed token limit and the series start and end times.

**The commit hash was missing entirely until 2026-08-07.** Rule 53 is Mandatory — record
the commit hash in the declaration — and the artifact named who played and on what hardware
but never *which code*, which is the one thing that makes a later audit reproducible.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.reporting.declaration import build_declaration
from p2p_thief_agent.reporting.naming import ArtifactError, MatchIdentity

ID = MatchIdentity(game_id="demo-vs-rival", game_uid="u" * 32)
COMMIT = "a" * 40
HARDWARE = {"os": "Windows 11", "cpu_type": "x86_64", "cpu_freq_mhz": 3000, "cpu_cores": 8,
            "ram_gb": 16, "gpu_model": "none", "vram_gb": 0}


def group(gid: str) -> dict:
    return {"group_id": gid, "group_name": gid, "members": ["student-1", "student-2"],
            "repos": {"cop": f"https://github.com/{gid}/cop",
                      "thief": f"https://github.com/{gid}/thief"},
            "mcp_servers": {"peer": f"https://{gid}.example.com/mcp"},
            "llm_model": "template-free", "hardware_spec": HARDWARE, "signature": "sig"}


GROUPS = [group("sharNamr"), group("rival")]


def declaration(**overrides) -> dict:
    kwargs = {"identity": ID, "groups": GROUPS, "num_sub_games": 6,
              "max_tokens_per_game": 200_000, "timezone": "UTC", "started_at": "t0",
              "ended_at": "t1", "links": {}, "github_commit": COMMIT}
    return build_declaration(**{**kwargs, **overrides})


def test_the_declaration_carries_both_groups_with_members_repos_and_mcp() -> None:
    """`M7-020a`-`c` in one assertion, because they are one requirement seen three ways."""
    groups = declaration()["groups"]
    assert len(groups) == 2
    for entry in groups:
        assert entry["members"], "a group with no members names nobody"
        assert set(entry["repos"]) == {"cop", "thief"}, "rule 49 wants both repositories"
        assert entry["mcp_servers"], "a peer that is never told the address cannot play"


def test_the_declaration_carries_the_hardware_and_model_declaration() -> None:
    """`M7-020d`. Rule 24 (Mandatory), sanction "denial of eligibility for computational
    bonuses" — so an incomplete spec costs points rather than merely looking untidy."""
    for entry in declaration()["groups"]:
        assert entry["llm_model"]
        assert set(entry["hardware_spec"]) >= {"cpu_type", "cpu_cores", "ram_gb",
                                               "gpu_model", "vram_gb"}


def test_the_declaration_carries_the_token_limit_and_the_series_times() -> None:
    """`M7-020e`. The limit is what rule 54's per-game accounting is measured against, and
    a limit nobody wrote down cannot be exceeded or respected in any checkable sense."""
    document = declaration()
    assert document["max_tokens_per_game"] == 200_000
    assert document["game_started_at"] and document["game_ended_at"]


def test_the_declaration_carries_the_commit_hash_rule_53_demands() -> None:
    """**This field did not exist before 2026-08-07.** The declaration said who played and
    on what hardware but never which code."""
    assert declaration()["github_commit"] == COMMIT


def test_a_declaration_without_a_commit_hash_is_refused_at_build_time() -> None:
    """Refused where it is built, not where it is read — an artifact already written to
    disk and emailed cannot be un-sent."""
    with pytest.raises(ArtifactError, match="commit hash"):
        declaration(github_commit="")


def test_a_truncated_commit_hash_is_refused() -> None:
    """A hash short enough to be ambiguous across the repository identifies no commit, so
    it satisfies rule 53's letter while defeating its purpose."""
    with pytest.raises(ArtifactError, match="commit hash"):
        declaration(github_commit="abc")
