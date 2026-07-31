"""`M5-007`: a whole sub-game and its audit, across a real socket.

The unit tests drive the sub-game against a fake transport, which proves the
decision logic. This proves the same run survives an actual carrier: every turn and
the final audit cross HTTP into a **separate operating-system process** that
validates each one and writes down what it saw.

The Cop's replies still come from a local script — a second peer that plays back is
later work — so what is shown here is this peer completing a bounded sub-game and
delivering a reproducible audit to a real remote, not two agents playing each other.
"""

from __future__ import annotations

from p2p_thief_agent.orchestration.phases import PhaseMachine
from p2p_thief_agent.orchestration.sub_game import run_sub_game_over_wire
from p2p_thief_agent.protocol.crypto import audit_records
from p2p_thief_agent.state.scoring import Outcome
from tests.integration.conftest import transcript_entries
from tests.unit.test_turn_loop import decide


def cop_turn(step: int, **extra: object) -> dict:
    return {"step": step, "sender": "police", "hint": "closing in",
            "smell_grid": {"0,0": 0.9}, "commit": "a" * 64,
            "timestamp": f"t{step}", **extra}


def scripted(*messages: dict):
    queue = list(messages)
    return lambda: queue.pop(0) if queue else None


def play(client, receive, threshold: int, answer=lambda _cell: False):
    return run_sub_game_over_wire(
        machine=PhaseMachine(),
        transport=client,
        receive=receive,
        decide=decide,
        answer_claim=answer,
        survival_threshold=threshold,
    )


def test_a_full_sub_game_and_its_audit_cross_a_real_socket(remote_peer) -> None:
    """Every turn and the audit are validated by an interpreter that is not this one."""
    client, transcript, _ = remote_peer

    result = play(client, scripted(cop_turn(1), cop_turn(2)), 3)

    assert result.outcome is Outcome.SURVIVAL
    assert result.steps == 3

    entries = transcript_entries(transcript)
    turns = [e for e in entries if e["tool"] == "receive_turn"]
    audits = [e for e in entries if e["tool"] == "submit_audit"]

    assert len(turns) == 3 and all(e["accepted"] for e in turns)
    assert len(audits) == 1 and audits[0]["accepted"] is True


def test_the_delivered_audit_reproduces_every_commitment(remote_peer) -> None:
    """`AE-019`: the remote peer accepted it, and it recomputes here too."""
    client, transcript, _ = remote_peer

    result = play(client, scripted(cop_turn(1)), 2)

    assert audit_records(result.audit["records"])["passed"] is True
    assert len(result.audit["records"]) == 2
    assert [e["accepted"] for e in transcript_entries(transcript)
            if e["tool"] == "submit_audit"] == [True]


def test_a_correct_capture_claim_ends_the_run_early_over_the_wire(remote_peer) -> None:
    """This peer concedes from its own knowledge, not because it was told to."""
    client, transcript, _ = remote_peer

    result = play(
        client,
        scripted(cop_turn(1, capture_claim=[3, 2]), cop_turn(2), cop_turn(3)),
        10,
        answer=lambda cell: cell == [3, 2],
    )

    assert result.outcome is Outcome.CAPTURE
    assert result.steps == 2
    assert result.audit["result_claim"] == "capture"

    turns = [e for e in transcript_entries(transcript) if e["tool"] == "receive_turn"]
    assert len(turns) == 2, "the run must stop sending once the game is decided"


def test_a_tampered_audit_is_rejected_by_the_remote_peer(remote_peer) -> None:
    """If this were accepted, the audit would be proving nothing at all."""
    client, transcript, _ = remote_peer

    result = play(client, scripted(cop_turn(1)), 2)
    forged = {**result.audit, "records": [
        {**r, "payload": {**r["payload"], "move": "MOVE:N"}} for r in result.audit["records"]
    ]}
    client.submit_audit(forged)

    audits = [e for e in transcript_entries(transcript) if e["tool"] == "submit_audit"]
    assert [e["accepted"] for e in audits] == [True, False]
    assert audits[1]["reason"]
