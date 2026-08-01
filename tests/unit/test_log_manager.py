"""`M5-008`: the append-only match log.

The Log Manager records every sent and received message, every phase transition, and
every commitment, in order and enough to reconstruct the match for the end-of-game
audit (`AE-36`). It is append-only by construction — no method edits or deletes a prior
entry — writes under a per-match path so two matches never collide, and withholds each
nonce until the audit is opened after the final reveal (`AE-18`). Time is injected.
"""

import json

import pytest

from p2p_thief_agent.services.log_manager import LogError, LogManager


class Clock:
    """A hand-wound clock so entry timestamps are deterministic."""

    def __init__(self) -> None:
        self.t = 1000.0

    def __call__(self) -> float:
        self.t += 1.0
        return self.t


def mgr(tmp_path, uid: str = "match-01-g1") -> LogManager:
    return LogManager(uid, tmp_path, clock=Clock())


def test_the_log_path_is_per_match(tmp_path) -> None:
    a = LogManager("game-A", tmp_path, clock=Clock())
    b = LogManager("game-B", tmp_path, clock=Clock())
    assert a.path != b.path
    assert "game-A" in a.path.name and a.path.suffix == ".jsonl"


def test_an_empty_game_uid_is_refused(tmp_path) -> None:
    with pytest.raises(LogError, match="game_uid is required"):
        LogManager("", tmp_path, clock=Clock())


def test_records_sent_and_received_messages_in_order(tmp_path) -> None:
    log = mgr(tmp_path)
    log.record_sent({"step": 1, "sender": "thief"})
    log.record_received({"step": 1, "sender": "police"})
    assert [e["kind"] for e in log.entries] == ["sent", "received"]
    assert [e["seq"] for e in log.entries] == [0, 1]
    assert log.entries[0]["message"] == {"step": 1, "sender": "thief"}


def test_records_transitions_and_commitments(tmp_path) -> None:
    log = mgr(tmp_path)
    log.record_transition("COMPUTING_MOVE")
    log.record_commitment(step=1, commit="a" * 64)
    assert log.entries[0]["kind"] == "transition"
    assert log.entries[0]["phase"] == "COMPUTING_MOVE"
    assert log.entries[1]["kind"] == "commitment" and log.entries[1]["commit"] == "a" * 64


def test_a_phase_enum_is_recorded_by_its_value(tmp_path) -> None:
    from p2p_thief_agent.orchestration.phases import Phase

    log = mgr(tmp_path)
    log.record_transition(Phase.COMMITTING)
    assert log.entries[-1]["phase"] == "COMMITTING"


def test_a_nonce_cannot_be_logged_before_the_audit_is_opened(tmp_path) -> None:
    log = mgr(tmp_path)
    with pytest.raises(LogError, match="nonce cannot be logged before the audit"):
        log.reveal_nonce(step=1, nonce="deadbeef")


def test_a_nonce_is_logged_once_the_audit_is_open(tmp_path) -> None:
    log = mgr(tmp_path)
    assert log.audit_open is False
    log.open_audit()
    assert log.audit_open is True
    entry = log.reveal_nonce(step=1, nonce="deadbeef")
    assert entry["kind"] == "nonce" and entry["nonce"] == "deadbeef"


def test_the_log_is_written_append_only_and_survives_a_reopen(tmp_path) -> None:
    log = mgr(tmp_path)
    log.record_sent({"step": 1})
    reopened = LogManager("match-01-g1", tmp_path, clock=Clock())
    reopened.record_sent({"step": 2})
    lines = log.path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2, "the reopened manager appended rather than truncating"
    assert [json.loads(line)["message"] for line in lines] == [{"step": 1}, {"step": 2}]
    assert [json.loads(line)["seq"] for line in lines] == [0, 1], "seq continues after reopen"


def test_there_is_no_method_to_edit_or_delete_an_entry(tmp_path) -> None:
    log = mgr(tmp_path)
    log.record_sent({"step": 1})
    forbidden = {"pop", "remove", "clear", "insert", "delete", "edit", "update", "__setitem__"}
    assert not (forbidden & set(dir(log)))
    assert isinstance(log.entries, tuple), "entries is a copy, not the mutable backing list"
