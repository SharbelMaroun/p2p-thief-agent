"""Unit tests for the simulator-conformant commit-reveal and canonical hashing."""

import re

import pytest

from p2p_thief_agent.protocol.crypto import (
    CryptoError,
    audit_records,
    canonical_sha256,
    commit_of,
    new_nonce,
    seal,
    verify,
)

NONCE = "000102030405060708090a0b0c0d0e0f"


def named_payload() -> dict:
    return {
        "domain": "p2p-thief/move-commitment/v1",
        "game_id": "match-01",
        "game_uid": "match-01-sub-1",
        "sub_game_number": 1,
        "step": 1,
        "sender_group_id": "sharNamr",
        "role": "thief",
        "position": [3, 3],
        "move": "N",
        "intent": "lie",
        "hint": "Central Park",
        "barrier": None,
    }


def test_commit_matches_frozen_simulator_vector():
    # Same construction as the Phase-1 commitment vector for this exact payload.
    assert commit_of(named_payload(), NONCE) == (
        "349470332e9917b65f0ebe6dd23b63fadb18371ef5f790f50aed981a2a73cc3d"
    )


def test_seal_then_verify_round_trip():
    payload = {"step": 1, "move": "N"}
    sealed = seal(payload)
    assert re.fullmatch(r"[0-9a-f]{32}", sealed["nonce"])
    verify(payload, sealed["nonce"], sealed["commit"])


def test_verify_rejects_tampered_payload_or_nonce():
    commit = commit_of(named_payload(), NONCE)
    tampered = named_payload()
    tampered["move"] = "S"
    with pytest.raises(CryptoError):
        verify(tampered, NONCE, commit)
    with pytest.raises(CryptoError):
        verify(named_payload(), "f" * 32, commit)


def test_verify_accepts_any_payload_roster():
    # The opponent's field set is its own choice; verification just re-hashes.
    opponent = {"totally": "different", "fields": [1, 2, 3], "step": 4}
    sealed = seal(opponent)
    verify(opponent, sealed["nonce"], sealed["commit"])


def test_new_nonce_is_fresh_lowercase_hex():
    assert new_nonce() != new_nonce()
    assert re.fullmatch(r"[0-9a-f]{32}", new_nonce())


def test_two_identical_moves_produce_different_commitments():
    """`M4-010a` / `AE-18`: a fresh nonce per commit defeats a dictionary attack."""
    payload = {"step": 1, "move": "N"}
    first, second = seal(payload), seal(payload)
    assert first["nonce"] != second["nonce"]
    assert first["commit"] != second["commit"]


def test_verify_rejects_a_near_miss_commitment():
    """`M4-012`: constant-time compare still rejects a digest differing in one byte."""
    payload = {"step": 1, "move": "N"}
    sealed = seal(payload)
    last = sealed["commit"][-1]
    near_miss = sealed["commit"][:-1] + ("0" if last != "0" else "1")
    with pytest.raises(CryptoError):
        verify(payload, sealed["nonce"], near_miss)
    verify(payload, sealed["nonce"], sealed["commit"])


def test_canonical_sha256_is_key_order_independent():
    assert canonical_sha256({"a": 1, "b": 2}) == canonical_sha256({"b": 2, "a": 1})


def test_audit_records_reports_pass_and_failures():
    good_payload = {"step": 1}
    good = {"payload": good_payload, **seal(good_payload)}
    bad = {"payload": {"step": 2}, "nonce": NONCE, "commit": "0" * 64}
    summary = audit_records([good, bad])
    assert summary["passed"] is False
    assert summary["verified_steps"] == 1
    assert summary["failed_steps"] == [2]


def test_audit_records_all_pass():
    records = [{"payload": {"step": s}, **seal({"step": s})} for s in (1, 2, 3)]
    summary = audit_records(records)
    assert summary == {"passed": True, "verified_steps": 3, "failed_steps": []}
