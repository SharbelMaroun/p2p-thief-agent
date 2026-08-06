"""`M7-016`, `M7-011`: agree only after auditing, and persist without a torn write.

Two rules punish different people, and conflating them is expensive. Rule 19: a technical
mismatch at audit is an "iron rule" scoring 0 for **the falsifying group** — one side.
Rule 35: a conflicting report scores 0 for **both teams**. So catching an opponent's
forgery is not a reason to race them to the lecturer with our own number.

Rule 36 fixes the audit's *position*, not just its existence: "Mandatory condition before
agreement on the JSON result."

Authored here rather than copied. `THIEF-002` forbids this repository any access to the
companion Cop repo, which solved the same problem today; `M1-015` set the discipline.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p2p_thief_agent.orchestration.settlement import (
    Settled,
    SettlementError,
    agree,
    audit_series,
    require_reportable,
    settlement_record,
)
from p2p_thief_agent.protocol.crypto import commit_of
from p2p_thief_agent.reporting.emit import EmitError, artifact_bytes, write_artifact


def _record(step: int, move: str, nonce: str) -> dict:
    payload = {"step": step, "move": move}
    return {"payload": payload, "nonce": nonce, "commit": commit_of(payload, nonce)}


def _reveal(sub_game: int, *, tamper: bool = False) -> dict:
    records = [_record(1, "N", "a" * 32), _record(2, "E", "b" * 32)]
    if tamper:
        records[1] = {**records[1], "payload": {"step": 2, "move": "S"}}
    return {"sub_game": sub_game, "records": records}


# --- M7-016: audit, then agree ------------------------------------------------------------


def test_a_clean_series_passes() -> None:
    audit = audit_series([_reveal(1), _reveal(2)])
    assert audit.passed and audit.sub_games == (1, 2)


def test_a_tampered_sub_game_fails_and_is_named() -> None:
    """Rule 19: "iron rule; score of 0 for the falsifying group"."""
    audit = audit_series([_reveal(1), _reveal(2, tamper=True)])
    assert not audit.passed and audit.failed_at == 2


def test_auditing_nothing_does_not_pass() -> None:
    """The commonest way an audit gate is bypassed is by never running it."""
    assert not audit_series([]).passed


def test_agreement_is_impossible_without_a_passed_audit() -> None:
    """Rule 36 makes the audit "a mandatory condition before agreement", so it is refused
    here rather than left for a caller to remember."""
    failed = audit_series([_reveal(1, tamper=True)])
    assert agree(failed, "capture", "capture").state is Settled.AUDIT_FAILED


def test_matching_outcomes_agree_and_differing_ones_conflict() -> None:
    passed = audit_series([_reveal(1)])
    assert agree(passed, "survival", "survival").state is Settled.AGREED
    assert agree(passed, "survival", "capture").state is Settled.CONFLICT


def test_silence_is_its_own_state_not_consent() -> None:
    """Treating a missing reply as agreement would let a peer that crashed decide our
    report for us."""
    assert agree(audit_series([_reveal(1)]), "survival", None).state is Settled.UNANSWERED


def test_both_claims_survive_into_the_record() -> None:
    """Adopting their number to keep the peace files a result we do not believe and
    destroys the evidence an auditor needs."""
    record = settlement_record(agree(audit_series([_reveal(1)]), "survival", "capture"))
    assert record["our_outcome"] == "survival" and record["their_outcome"] == "capture"


def test_only_an_agreed_settlement_may_be_reported() -> None:
    require_reportable(agree(audit_series([_reveal(1)]), "survival", "survival"))
    with pytest.raises(SettlementError, match="0 for BOTH teams"):
        require_reportable(agree(audit_series([_reveal(1)]), "survival", "capture"))


def test_the_three_refusals_carry_three_different_remedies() -> None:
    """A conflict needs a human and the lecturer; an audit failure needs the evidence
    preserved; silence needs the *exchange* retried, not the report. One generic message
    would send all three down the same wrong path."""
    passed, failed = audit_series([_reveal(1)]), audit_series([_reveal(1, tamper=True)])
    messages = set()
    for settled in (agree(passed, "a", "b"), agree(failed, "a", "b"), agree(passed, "a", None)):
        with pytest.raises(SettlementError) as raised:
            require_reportable(settled)
        messages.add(str(raised.value))
    assert len(messages) == 3


# --- M7-011: atomic persistence -------------------------------------------------------------


def test_an_artifact_round_trips_through_the_file(tmp_path: Path) -> None:
    artifact = {"_schema": "result-report", "game_uid": "u1"}
    assert json.loads(write_artifact(tmp_path, "result_g1.json", artifact).read_text("utf-8")) == artifact


def test_no_temporary_file_survives_a_successful_write(tmp_path: Path) -> None:
    """A stray `.tmp` would be committed alongside the real artifact and read as part of
    the evidence set."""
    write_artifact(tmp_path, "result_g1.json", {"a": 1})
    assert [p.name for p in tmp_path.iterdir()] == ["result_g1.json"]


def test_a_rewrite_replaces_rather_than_appends(tmp_path: Path) -> None:
    """A torn or doubled file reads as a technical mismatch at audit, whose sanction is
    score 0 -- and nothing in the artifact distinguishes it from a deliberate forgery."""
    write_artifact(tmp_path, "result_g1.json", {"v": 1})
    write_artifact(tmp_path, "result_g1.json", {"v": 2})
    assert json.loads((tmp_path / "result_g1.json").read_text("utf-8")) == {"v": 2}


@pytest.mark.parametrize("bad", ["../escape.json", "a/b.json", "", "."])
def test_a_filename_with_a_path_component_is_refused(tmp_path: Path, bad: str) -> None:
    """The last line of defence if a negotiated `game_id` ever reached a path unchecked."""
    with pytest.raises(EmitError):
        write_artifact(tmp_path, bad, {"a": 1})


def test_the_bytes_are_utf8_with_a_trailing_newline() -> None:
    raw = artifact_bytes({"hint": "café near the north edge"})
    assert raw.endswith(b"\n") and "café" in raw.decode("utf-8")


def test_emission_takes_no_transport(tmp_path: Path) -> None:
    """A game that ends because the opponent vanished still produces its artifacts -- the
    only way the files can be evidence of a game that went wrong."""
    from inspect import signature

    assert set(signature(write_artifact).parameters) == {"directory", "filename", "artifact"}
