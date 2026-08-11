"""`M9-042`: the wire log must record what the access log cannot.

The failure it exists for: on 2026-08-11 an offer arrived, did not reach the runtime, and
left nothing behind but `200 OK`. These tests pin the three things that were missing —
arrival, verdict, and reason — and the two properties that keep the log safe to run during
a counted game: it never raises, and it never writes a payload.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p2p_thief_agent.services import wire_log


@pytest.fixture(autouse=True)
def _isolate():
    """No test may inherit another's target, and none may leave the log armed."""
    wire_log.disable()
    yield
    wire_log.disable()


def _lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_nothing_is_written_until_it_is_enabled(tmp_path: Path) -> None:
    """The default is off: importing this must not create files next to someone's game."""
    wire_log.received("negotiate", {"terms": {}}, queued=True)
    wire_log.validated("negotiate", accepted=True)
    assert wire_log.target() is None
    assert not list(tmp_path.iterdir())


def test_an_arrival_and_its_verdict_are_both_recorded(tmp_path: Path) -> None:
    assert wire_log.enable(tmp_path / "logs") is True
    wire_log.received("negotiate", {"terms": {}, "nonce": "a", "signature": "b"}, queued=True)
    wire_log.validated("negotiate", accepted=True)

    events = _lines(wire_log.target())
    assert [event["event"] for event in events] == ["received", "validated"]
    assert events[0]["tool"] == "negotiate"
    assert events[0]["queued"] is True
    assert events[0]["keys"] == ["nonce", "signature", "terms"]
    assert events[1]["accepted"] is True
    assert all(event["at"].endswith("+00:00") for event in events)


def test_the_rejection_reason_survives(tmp_path: Path) -> None:
    """**The point of the whole module.** This text was computed and thrown away."""
    wire_log.enable(tmp_path / "logs")
    wire_log.validated("negotiate", accepted=False,
                       reason=ValueError("negotiate missing field: 'signature'"))

    event = _lines(wire_log.target())[-1]
    assert event["accepted"] is False
    assert "missing field" in event["reason"]


def test_a_refused_full_inbox_is_recorded(tmp_path: Path) -> None:
    """`AE-29`: we tell the opponent we refused, so we should be able to prove it."""
    wire_log.enable(tmp_path / "logs")
    wire_log.received("receive_turn", {"step": 4}, queued=False)
    assert _lines(wire_log.target())[-1]["queued"] is False


def test_no_payload_is_ever_written(tmp_path: Path) -> None:
    """Rule 18/39: a nonce or commitment in an unmanaged file is a hazard, not a diagnostic."""
    wire_log.enable(tmp_path / "logs")
    wire_log.received("receive_turn", {"step": 7, "nonce": "SECRET", "commit": "SEALED"},
                      queued=True)
    written = wire_log.target().read_text(encoding="utf-8")
    assert "SECRET" not in written
    assert "SEALED" not in written
    assert "nonce" in written  # the key name is the diagnostic; the value is not


def test_a_non_mapping_message_does_not_raise(tmp_path: Path) -> None:
    wire_log.enable(tmp_path / "logs")
    wire_log.received("negotiate", "not-an-object", queued=True)
    assert _lines(wire_log.target())[-1]["keys"] == []


def test_an_unwritable_target_disables_rather_than_raising(tmp_path: Path) -> None:
    """Logging must never be able to cost a turn — rule 6 scores a freeze 0/0."""
    clash = tmp_path / "not-a-dir"
    clash.write_text("i am a file", encoding="utf-8")
    assert wire_log.enable(clash / "logs") is False
    assert wire_log.target() is None
    wire_log.received("negotiate", {}, queued=True)  # must not raise


def test_a_write_failure_is_swallowed(tmp_path: Path) -> None:
    """Enabled, then the directory disappears mid-match: still no exception, still no turn lost."""
    wire_log.enable(tmp_path / "logs")
    target = wire_log.target()
    assert not target.exists()  # nothing written yet, so the directory is empty
    target.parent.rmdir()

    wire_log.received("negotiate", {}, queued=True)  # must not raise
    wire_log.validated("negotiate", accepted=False, reason="anything")  # nor this
    assert not target.exists()
