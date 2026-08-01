"""`M4-009`: every tampering class is detected at audit, not merely most.

Each sealed record is ``{payload, nonce, commit}``. Because the commitment hashes the
whole canonical payload together with the nonce, any change — to the move, the bluff
intent, the nonce, a single byte anywhere, or the bound step index — makes the
recomputed hash diverge, so the audit catches it. The step index living *inside* the
hashed payload is what defeats a reordered sequence: a record cannot lie about which
step it was, whatever order it arrives in.
"""

import pytest

from p2p_thief_agent.protocol.crypto import CryptoError, audit_records, verify
from p2p_thief_agent.protocol.sealing import StepDecision, sealed_step_record


def record(step: int = 1, move: str = "N", verdict: str = "truth") -> dict:
    return sealed_step_record(
        step=step, board_size=7, position=[3, step], barriers=[],
        decision=StepDecision(move=move, verdict=verdict, hint="near the park"),
    )


def expect_rejected(rec: dict, **changes: object) -> None:
    payload = {**rec["payload"], **changes}
    with pytest.raises(CryptoError):
        verify(payload, rec["nonce"], rec["commit"])


def test_a_mutated_move_is_detected() -> None:
    expect_rejected(record(move="N"), move="S")


def test_a_mutated_intent_flag_is_detected() -> None:
    expect_rejected(record(verdict="truth"), intent="lie", verdict="lie")


def test_a_substituted_nonce_is_detected() -> None:
    rec = record()
    with pytest.raises(CryptoError):
        verify(rec["payload"], "f" * 32, rec["commit"])


def test_a_single_byte_mutation_anywhere_is_detected() -> None:
    expect_rejected(record(), hint="near the parl")  # one byte: k -> l


def test_a_renumbered_step_index_is_detected() -> None:
    """The step is bound in the payload, so a record cannot be silently renumbered."""
    expect_rejected(record(step=3), step=4)


def test_audit_reports_the_failed_step_whatever_order_records_arrive_in() -> None:
    good = [record(step=s) for s in (1, 2, 3)]
    tampered = {**good[1], "payload": {**good[1]["payload"], "move": "S"}}
    summary = audit_records([good[2], tampered, good[0]])  # reordered on the wire
    assert summary["passed"] is False
    assert summary["failed_steps"] == [2]
