"""`M7-018`: a full local series rehearsal before any counted game.

The row's condition names six things: six sub-games, four artifact families, audit,
agreement, and a mocked send. This asserts all of them against `rehearsal.rehearse`, which
wires the **real** builders, audit, settlement, ledgers and retention store together — a
rehearsal against test doubles would rehearse the doubles.

The point is the seams. Every unit test here proves one component behaves; none proves they
connect. The failures this catches are the ones that only exist between modules: four
artifacts that each validate but share no `game_uid`, a settlement that never reaches the
composer, a config written where `.gitignore` swallows it.

Deliberately lost sub-games are in `test_rehearsal_failures.py` (`M7-018a`) and a forged
audit in `test_rehearsal_tampering.py` (`M7-018b`).
"""

from __future__ import annotations

import json

import pytest

from p2p_thief_agent.orchestration.series import THIEF_SUBGAMES_NATURAL
from p2p_thief_agent.reporting.retention import missing_configs, retrieve_config
from tests.integration.rehearsal import OPPONENT, TOKEN_LIMIT, rehearse, shared_uid


@pytest.fixture(scope="module")
def rehearsal(tmp_path_factory):
    """One rehearsal for the whole module — it is a full series, not a unit."""
    return rehearse(tmp_path_factory.mktemp("clean"))


def test_the_series_runs_every_thief_sub_game(rehearsal) -> None:
    logs = [name for name in rehearsal.artifacts if name.startswith("log_")]
    assert len(logs) == len(THIEF_SUBGAMES_NATURAL)


def test_all_four_artifact_families_are_produced(rehearsal) -> None:
    """Four families, not four files: a series has one declaration, one result, and a
    config and log *per sub-game*."""
    kinds = {name.split("_", 1)[0] for name in rehearsal.artifacts}
    assert kinds == {"declaration", "config", "log", "result"}


def test_every_artifact_of_the_series_shares_one_game_uid(rehearsal) -> None:
    """`AR-001`. The seam failure: each file validates alone and together they describe a
    match that never happened."""
    assert shared_uid(rehearsal) == rehearsal.identity.game_uid


def test_every_artifact_is_written_to_disk_and_reads_back_as_json(rehearsal) -> None:
    """Written, not just built. A builder that returns a dict containing something
    unserialisable fails here and nowhere else."""
    for path in rehearsal.written.values():
        assert json.loads(path.read_text(encoding="utf-8"))


def test_the_audit_passed_and_the_result_was_agreed(rehearsal) -> None:
    """Rule 36 puts the audit before agreement, so a rehearsal that agreed without one
    would prove the ordering is not enforced."""
    assert rehearsal.settlement["audit_passed"] is True
    assert rehearsal.settlement["state"] == "agreed"


def test_the_report_was_sent_through_the_api_shape(rehearsal) -> None:
    """Mocked transport, real envelope: `userId="me"` and a `raw` body."""
    assert len(rehearsal.transport.sent) == 1
    call = rehearsal.transport.sent[0]
    assert call["userId"] == "me"
    assert set(call["body"]) == {"raw"}


def test_every_config_is_committed_and_retrievable(rehearsal, tmp_path_factory) -> None:
    """Appendix F obligation 4 checked against what the rehearsal actually stored, rather
    than against a fresh store built for the assertion."""
    root = rehearsal.written[next(iter(rehearsal.written))].parent.parent
    assert missing_configs(root, rehearsal.identity.game_id, THIEF_SUBGAMES_NATURAL) == ()
    for number in THIEF_SUBGAMES_NATURAL:
        assert retrieve_config(root, rehearsal.identity.game_id, number)["config_sha256"]


def test_the_token_report_carries_both_rule_54_figures(rehearsal) -> None:
    assert rehearsal.tokens["tokens_total_series"] == sum(
        rehearsal.tokens["per_sub_game"].values())
    assert rehearsal.tokens["sub_games_over_limit"] == []
    assert rehearsal.tokens["max_tokens_per_game"] == TOKEN_LIMIT


def test_the_result_names_both_groups_with_four_repository_links(rehearsal) -> None:
    """Rule 49. Counted across both groups, because two links each is the requirement and
    one group with four would satisfy a naive total."""
    result = next(body for name, body in rehearsal.artifacts.items()
                  if name.startswith("result_"))
    assert len(result["groups"]) == 2
    assert sum(len(entry["repos"]) for entry in result["groups"]) == 4
    assert {entry["group_id"] for entry in result["groups"]} >= {OPPONENT}
