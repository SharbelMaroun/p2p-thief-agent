"""`M8-009a` / `M8-009c`: nothing secret leaves in an artifact, and the lockfile is truth.

Rule 39 (Prohibited): "Do not push secrets and credentials to the repository, **even if it
is private and shared only with the lecturer**. Sanction: severe security failure and
project failure." Rule 40 (Mandatory): credential files go in `.gitignore`.

`scripts/check_secrets.py` scans the tree, and that is the right first line. It cannot
reach this failure: the four artifacts are **built at runtime, then handed to an opponent
and emailed to the lecturer**. A secret arriving in one of them never sits in the
repository, so the scanner passes, the file leaves the machine, and the sanction is project
failure.

This builds each artifact with the real builders and inspects the product. Every group
fixture deliberately carries the fields most likely to smuggle something — repository URLs,
an MCP server map, a model name and a signature.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import tomllib

from p2p_thief_agent.reporting.config_artifact import build_config
from p2p_thief_agent.reporting.declaration import build_declaration
from p2p_thief_agent.reporting.log_artifact import build_log
from p2p_thief_agent.reporting.naming import MatchIdentity
from p2p_thief_agent.reporting.result_artifact import build_result

ROOT = Path(__file__).resolve().parents[2]
ID = MatchIdentity(game_id="secret-scan", game_uid="uid-9")

SECRET_SHAPES = (
    (r"(?i)\bsk-[A-Za-z0-9]{16,}", "an OpenAI-style API key"),
    (r"(?i)\bAIza[0-9A-Za-z_\-]{20,}", "a Google API key"),
    (r"(?i)\bghp_[A-Za-z0-9]{20,}", "a GitHub token"),
    (r"(?i)\b(client_secret|refresh_token|access_token|private_key)\b", "a credential field"),
    (r"(?i)\bBEGIN [A-Z ]*PRIVATE KEY\b", "an embedded private key"),
    (r"(?i)://[^/\s:@]+:[^/\s:@]+@", "credentials embedded in a URL"),
    (r"(?i)\b(password|passwd|api[_-]?key)\s*[:=]", "an inline password or key"),
)

HARDWARE = {"os": "Windows 11", "cpu_type": "x86_64", "cpu_cores": 8, "cpu_freq_mhz": 3600,
            "ram_gb": 16, "gpu_model": "none", "vram_gb": 0}


def _group(gid: str) -> dict:
    return {"group_id": gid, "group_name": gid, "members": ["m"],
            "repos": {"cop": f"https://github.com/{gid}/cop",
                      "thief": f"https://github.com/{gid}/thief"},
            "mcp_servers": {"peer": f"https://{gid}.example.com/mcp"},
            "llm_model": "template", "hardware_spec": HARDWARE, "signature": "sig"}


GROUPS = [_group("sharNamr"), _group("opp")]
SECTIONS = {name: {"k": 1} for name in
            ("board_and_agents", "world", "movement_and_barriers", "scoring", "pheromones",
             "network_and_league", "rate_limiter_gatekeeper")}
SUBGAME = {"sub_game_number": 1, "roles": {}, "started_at": "t0", "ended_at": "t1",
           "result": "survival", "winner_group": "sharNamr", "tie": False,
           "github_commit": "a" * 40, "tokens": 0, "score": 10, "log_files": [], "audit": {}}
FINAL = {"total_score": 25, "sub_games_won": 3, "ties": 0, "winner_group": "sharNamr",
         "series_tie": False, "tokens_total_series": 0}
# The reveal-audit block both the log and the result carry. Named so the two artifacts
# cannot drift apart in this fixture the way they could in a hand-written one.
AGREEMENT = {"confirmed": True, "opponent_group_id": "opp", "sha256": "f" * 64}
SUMMARY = {**dict.fromkeys(
    ("sub_game_number", "group_id", "role", "opponent_group_id", "result", "winner_role",
     "steps", "timezone", "started_at", "duration_seconds", "tokens_total", "audit"), 0),
    "ended_at": "t1"}  # `M7-022b`: a log with no end time is a game still in play [AE-18]


def _artifacts() -> dict[str, object]:
    """One of each family, built by the real builders rather than hand-written."""
    return {
        "declaration": build_declaration(identity=ID, groups=GROUPS, num_sub_games=6,
                                         max_tokens_per_game=1000, timezone="UTC",
                                         started_at="t0", ended_at="t1", links={}, github_commit="a" * 40),
        "config": build_config(identity=ID, sub_game_number=1,
                               agreed_between=["sharNamr", "opp"], sections=SECTIONS,
                               links={}, config_name="config_secret-scan_g01.json"),
        "log": build_log(identity=ID, summary=SUMMARY, links={},
                         mutual_agreement=AGREEMENT,
                         records=[{"payload": {"step": 1}, "nonce": "n", "commit": "c"}]),
        "result": build_result(identity=ID, groups=GROUPS, sub_games=[SUBGAME],
                               final_result=FINAL, timezone="UTC",
                               mutual_agreement=AGREEMENT),
    }


@pytest.mark.parametrize("name", ["declaration", "config", "log", "result"])
def test_no_built_artifact_contains_anything_shaped_like_a_secret(name: str) -> None:
    """**The check the repository scanner cannot make.** These are generated, then shared
    with an opponent and attached to an email — a leak here never touches the repository."""
    text = json.dumps(_artifacts()[name], ensure_ascii=False, default=str)
    for pattern, description in SECRET_SHAPES:
        assert not re.search(pattern, text), f"{name} artifact appears to carry {description}"


def test_the_scan_is_not_vacuous_because_the_patterns_match_a_real_shape() -> None:
    """A scanner that matches nothing passes everything. Proven against a synthetic value
    that is not a credential and never reaches a file."""
    assert any(re.search(p, json.dumps({"note": "sk-" + "A" * 24})) for p, _ in SECRET_SHAPES)


def test_no_artifact_carries_a_field_named_for_a_secret() -> None:
    """Shape-matching catches a value; this catches an empty or placeholder *field*, which
    is how a credential arrives in a template before anyone fills it in."""
    forbidden = {"token", "secret", "credential", "credentials", "api_key", "apikey",
                 "password", "private_key", "client_secret", "refresh_token"}
    for name, artifact in _artifacts().items():
        keys = set(re.findall(r'"([^"]+)":', json.dumps(artifact, default=str)))
        assert not (keys & forbidden), f"{name} carries {sorted(keys & forbidden)}"


# --- M8-009c: the lockfile is authoritative ---------------------------------------------


def test_the_lockfile_exists_and_is_the_authority() -> None:
    """`G§8.4`. A repository that resolves dependencies fresh on the grader's machine is a
    repository whose test results are not the ones we ran."""
    assert (ROOT / "uv.lock").exists(), "uv.lock is missing; dependencies are unpinned"


def test_every_runtime_dependency_carries_a_bound() -> None:
    """An unbounded dependency resolves to whatever exists on the day. Bounds are what make
    `uv sync --frozen` mean the same thing next month."""
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))
    loose = [d for d in pyproject["project"].get("dependencies", [])
             if not re.search(r"[<>=~^]", d)]
    assert not loose, f"unpinned dependencies: {loose}"


def test_the_gitignore_covers_every_credential_filename_rule_40_names() -> None:
    """Rule 40 (Mandatory). Checked alongside the scanner because the scanner proves no
    secret is *present*; this proves one could not be *added* silently."""
    ignored = (ROOT / ".gitignore").read_text("utf-8")
    for pattern in ("credentials.json", "token.json", ".env"):
        assert pattern in ignored, f".gitignore does not cover {pattern} [AE-40]"
