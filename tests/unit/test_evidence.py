"""`M9-010` / `M9-021`: the bundle, and whether the league minimum is actually met.

One place to answer what a submission turns on — for each counted game, do we still have the
artifacts, the commit that ran it, and evidence it was reported? Each part exists somewhere
already; none was assembled per game, and a gap is only visible when they are read together.

What a *sender* can honestly claim is tested next door in `test_send_receipt.py`.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.reporting.evidence import (
    EvidenceBundle,
    archive_is_complete,
    missing_evidence,
)
from p2p_thief_agent.reporting.league_ledger import PlayedGame
from p2p_thief_agent.reporting.send_receipt import EvidenceError, SendReceipt

SHA = "a" * 40
PROV = {"github_commit": SHA, "working_tree_clean": True}
FULL_SET = ["declaration_g.json", "config_g_g01.json", "log_g_g01.json", "result_g.json"]


def game(gid: str, opponent: str, *, counted: bool = True, won: bool = True) -> PlayedGame:
    return PlayedGame(game_id=gid, opponent_group_id=opponent, counted=counted, won=won)


def receipt(gid: str) -> SendReceipt:
    return SendReceipt.from_api_response({"id": f"msg-{gid}"}, game_id=gid,
                                         sent_at="2026-08-07T12:00:00+03:00",
                                         recipient="rmisegal+uoh26finalgame@gmail.com")


def bundle(*games: PlayedGame, receipts: bool = True) -> EvidenceBundle:
    b = EvidenceBundle()
    for g in games:
        b.add_game(g, provenance=PROV)
        if receipts:
            b.add_receipt(receipt(g.game_id))
    return b


# --- the bundle -----------------------------------------------------------------------------


def test_a_game_without_a_resolved_commit_is_refused() -> None:
    """Rule 53. The reference hard-codes `"unknown"` here, which identifies nothing while
    satisfying every shape check."""
    with pytest.raises(EvidenceError, match="AE-53"):
        EvidenceBundle().add_game(game("g1", "rival"),
                                  provenance={"github_commit": "unknown"})


def test_the_same_game_cannot_be_added_twice() -> None:
    b = bundle(game("g1", "rival"))
    with pytest.raises(EvidenceError, match="already in the bundle"):
        b.add_game(game("g1", "rival"), provenance=PROV)


def test_a_second_receipt_for_one_game_is_refused() -> None:
    """Two sends for one game is the easiest accidental route to the rule 35 conflict
    verdict, which scores 0 for **both** teams."""
    b = bundle(game("g1", "rival"))
    with pytest.raises(EvidenceError, match="BOTH teams"):
        b.add_receipt(receipt("g1"))


def test_a_counted_game_with_no_receipt_is_listed_as_unreported() -> None:
    """Rule 32: a side that does not report scores nothing for that game, whatever the
    result was."""
    b = bundle(game("g1", "rival"), receipts=False)
    assert b.unreported_games() == ("g1",)


def test_a_warm_up_without_a_receipt_is_not_listed() -> None:
    """Warm-ups are uncounted, so there is nothing to report and nothing to lose."""
    b = bundle(game("w1", "rival", counted=False), receipts=False)
    assert b.unreported_games() == ()


# --- M9-010d: reconciling the declared counts ---------------------------------------------------


def test_declared_counts_matching_the_bundle_pass() -> None:
    b = bundle(game("g1", "rival"), game("g2", "other"))
    b.reconcile({"rival": 2, "other": 2})


def test_every_mismatched_opponent_is_reported_in_one_pass() -> None:
    """Rule 38's sanction is absolute disqualification of the project — not something to
    discover one opponent at a time."""
    b = bundle(game("g1", "rival"), game("g2", "other"))
    with pytest.raises(EvidenceError) as caught:
        b.reconcile({"rival": 9, "other": 7})
    assert "rival" in str(caught.value) and "other" in str(caught.value)


# --- M9-010a: what a counted game is still missing ------------------------------------------------


def test_a_complete_game_reports_no_gaps() -> None:
    b = bundle(game("g1", "rival"))
    assert missing_evidence(b, {"g1": FULL_SET}) == {}


def test_an_incomplete_artifact_set_is_reported() -> None:
    """Three of four files is not an archived set — the missing one is the one an auditor
    would have asked for."""
    b = bundle(game("g1", "rival"))
    assert missing_evidence(b, {"g1": FULL_SET[:3]}) == {"g1": ["archived artifact set"]}


def test_a_game_with_nothing_archived_lists_every_gap_at_once() -> None:
    b = EvidenceBundle()
    b.add_game(game("g1", "rival"), provenance=PROV)
    assert missing_evidence(b, {}) == {"g1": ["archived artifact set", "send receipt"]}


@pytest.mark.parametrize(("files", "complete"),
                        [(FULL_SET, True), (FULL_SET[:3], False), ([], False)])
def test_an_archive_needs_all_four_artifact_kinds(files, complete) -> None:
    assert archive_is_complete(files) is complete
