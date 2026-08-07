"""`M7-018b`: rehearse a tampered audit — detection, scoring and reporting all behave.

The tamper is the realistic one: a revealed move rewritten **after** its commitment was
taken. Nothing about the record looks wrong on its own — the nonce is present, the digest is
a valid hash, the payload is well-formed — and only recomputing the commitment shows the two
disagree. That is precisely what rule 19 calls a technical mismatch during the audit phase,
"iron rule; score of 0 for the falsifying group".

Three behaviours have to hold together, and getting any one right while missing another is
worse than failing outright:

* **detection** — the audit fails and names the sub-game;
* **scoring** — the result is not agreed, so nothing claims a score it did not earn;
* **reporting** — **nothing is sent**. Rule 35 scores a conflicting report 0 for *both*
  teams, so firing off our own contradicting report converts their rule 19 loss into a
  shared one. Catching a forgery is not a reason to race them to the lecturer.

The artifacts are still produced. Refusing to write them would destroy the evidence of the
forgery, which is the one thing an auditor needs.
"""

from __future__ import annotations

import json

import pytest

from p2p_thief_agent.orchestration.series import THIEF_SUBGAMES_NATURAL
from p2p_thief_agent.reporting.email_report import ReportSendError, compose_report
from p2p_thief_agent.reporting.retention import missing_configs
from tests.integration.rehearsal import rehearse, shared_uid

FORGED = THIEF_SUBGAMES_NATURAL[2]


@pytest.fixture(scope="module")
def tampered(tmp_path_factory):
    """One sub-game's revealed move rewritten after its commitment was taken."""
    return rehearse(tmp_path_factory.mktemp("tampered"), tamper_sub_game=FORGED)


# --- detection --------------------------------------------------------------------------------


def test_the_audit_fails_on_the_forged_sub_game(tampered) -> None:
    """Nothing about the record is malformed. Only recomputing the commitment shows it."""
    assert tampered.settlement["audit_passed"] is False
    assert tampered.settlement["audit_failed_at"] == FORGED


def test_the_settlement_is_audit_failed_rather_than_a_disagreement(tampered) -> None:
    """The distinction carries the sanction. Rule 19 is 0 for the *falsifying* group; rule
    35 is 0 for **both**. Recording a forgery as a mere disagreement gives away half the
    difference."""
    assert tampered.settlement["state"] == "audit_failed"


# --- reporting: the expensive mistake ------------------------------------------------------


def test_nothing_is_sent_when_the_audit_failed(tampered) -> None:
    """**The behaviour that costs the most to get wrong.** Sending our own contradicting
    report converts their rule 19 loss into a shared rule 35 loss."""
    assert tampered.transport.sent == []


def test_composing_a_report_from_the_failed_settlement_is_refused(tampered) -> None:
    """Refused at the composer, not merely skipped by the caller — `M7-005f`. A caller that
    forgets the check is exactly the scenario the precondition exists for."""
    result = next(body for name, body in tampered.artifacts.items()
                  if name.startswith("result_"))
    with pytest.raises(ReportSendError, match=r"AE-3[56]"):
        compose_report(result=result, settlement=tampered.settlement,
                       sender="thief@example.com", game_id=tampered.identity.game_id,
                       team_code="sharNamr")


# --- the evidence survives ----------------------------------------------------------------------


def test_the_artifacts_are_still_produced_and_written(tampered) -> None:
    """Refusing to write them would destroy the evidence of the forgery. The log that
    fails its own audit *is* the proof."""
    kinds = {name.split("_", 1)[0] for name in tampered.artifacts}
    assert kinds == {"declaration", "config", "log", "result"}
    for path in tampered.written.values():
        assert json.loads(path.read_text(encoding="utf-8"))


def test_the_forged_log_still_carries_the_commitment_that_convicts_it(tampered) -> None:
    """The nonce and digest are what let a third party recompute the mismatch without our
    code. Dropping them would leave an unverifiable accusation."""
    log = next(body for name, body in tampered.artifacts.items()
               if name.startswith("log_") and f"g{FORGED:02d}" in name)
    assert all(entry["commit"] and entry["nonce"] for entry in log["records"])


def test_the_artifact_set_still_shares_one_game_uid(tampered) -> None:
    assert shared_uid(tampered) == tampered.identity.game_uid


def test_the_logs_record_that_the_agreement_was_not_confirmed(tampered) -> None:
    """`confirmed: False` rather than an absent field. A missing flag reads as "not yet
    asked"; this game was asked and the answer was no."""
    for name, body in tampered.artifacts.items():
        if name.startswith("log_"):
            assert body["mutual_agreement"]["confirmed"] is False


def test_every_config_is_still_committed_after_a_forgery(tampered) -> None:
    """The game somebody will most want to reproduce."""
    root = tampered.written[next(iter(tampered.written))].parent.parent
    assert missing_configs(root, tampered.identity.game_id, THIEF_SUBGAMES_NATURAL) == ()


def test_the_untampered_sub_games_are_not_implicated(tampered) -> None:
    """The audit stops at the first failure, so the sub-games before it verified. Reporting
    the whole series as forged would overstate what was found."""
    assert tampered.settlement["audit_failed_at"] == FORGED
    assert THIEF_SUBGAMES_NATURAL[0] != FORGED, "the fixture must not forge the first game"
