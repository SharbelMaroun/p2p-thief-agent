"""`M8-002b` / `M8-002c`: the two verdicts, and the one that voids the match.

Rule 20 makes the replay app a **threshold condition** for submission (p.129/272), so
these are not tests of a feature — they are tests of the thing whose absence is a rejected
project. The binding assertions are that a single altered record condemns the whole match
(`:1753`) and that there is no third verdict to hide in (`:1769`: "no appeal process").

Sequence integrity is `test_replay_sequence.py`; which construction is authoritative is
`test_replay_authority.py`.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from p2p_thief_agent.replay import Verdict, verify_record, verify_records

NONCE = "a1" * 16


def _commit(payload: object, nonce: str = NONCE) -> str:
    """Recompute the way an outsider would, from the published construction only."""
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(f"{canonical}|{nonce}".encode()).hexdigest()


def _record(step: int, move: str = "N", nonce: str = NONCE) -> dict:
    payload = {"step": step, "move": move, "intent": True}
    return {"step": step, "sender": "thief", "move": move, "hint": "north", "intent": True,
            "payload": payload, "nonce": nonce, "commit": _commit(payload, nonce)}


def _records(count: int = 4) -> list[dict]:
    return [_record(n) for n in range(1, count + 1)]


# --- the happy path is the submission evidence ------------------------------------------


def test_an_untouched_log_verifies_and_says_how_many_steps() -> None:
    result = verify_records(_records(4))
    assert result.verdict is Verdict.VERIFIED_OK
    assert result.first_bad is None
    assert result.banner == "Verified OK — 4 steps re-verified"


def test_verification_recomputes_rather_than_trusting_the_stored_commit() -> None:
    """The commits above come from this test's own hashing expression, which imports
    nothing from `protocol.crypto`. If the two constructions drift, this fails."""
    assert verify_record(_record(1)).ok


# --- M8-002c: one bad record voids the whole match ---------------------------------------


def test_a_single_altered_move_condemns_the_entire_match() -> None:
    """`:1753` — "If any single step returns TAMPERED, the entire match is invalidated"."""
    records = _records(5)
    records[2]["payload"] = {**records[2]["payload"], "move": "S"}

    result = verify_records(records)
    assert result.verdict is Verdict.TAMPERED
    assert result.first_bad is not None and result.first_bad.step == 3
    assert "step 3" in result.banner


def test_the_records_after_a_forgery_are_still_checked_and_still_pass() -> None:
    """The match is void either way, but "which step" is the auditor's next question and
    re-running to answer it would mean trusting the same code twice."""
    records = _records(5)
    records[1]["nonce"] = "b" * 32
    assert [c.ok for c in verify_records(records).checks] == [True, False, True, True, True]


def test_a_forgery_in_the_very_last_record_is_caught_too() -> None:
    """A verifier that stopped early — or sampled — would pass this log."""
    records = _records(6)
    records[-1]["commit"] = "0" * 64
    assert verify_records(records).verdict is Verdict.TAMPERED


# --- unverifiable is TAMPERED, not an exception -----------------------------------------


@pytest.mark.parametrize("field", ["commit", "payload", "nonce"])
def test_a_record_stripped_of_a_verification_input_is_tampered(field: str) -> None:
    """`protocol.crypto.verify` raises; the translation to a verdict happens in the replay
    layer. Damaging a record must not be an easier escape than rewriting one."""
    record = _record(1)
    del record[field]
    check = verify_record(record)
    assert check.verdict is Verdict.TAMPERED and field in check.reason


def test_a_crypto_error_becomes_a_verdict_rather_than_propagating() -> None:
    """The whole point of catching `CryptoError` here: a malformed nonce must red-banner
    the match, not crash the viewer during the demonstration it exists to produce."""
    record = {**_record(1), "nonce": None}
    check = verify_record(record)
    assert check.verdict is Verdict.TAMPERED and "commitment rejected" in check.reason


def test_a_record_that_is_not_an_object_is_tampered_rather_than_a_crash() -> None:
    assert verify_records([_record(1), "not a record"]).verdict is Verdict.TAMPERED


def test_an_empty_record_list_is_tampered_not_vacuously_verified() -> None:
    """The dangerous default: returning OK for zero records would stamp `Verified OK` on
    an emptied log, which is the easiest forgery of all."""
    result = verify_records([])
    assert result.verdict is Verdict.TAMPERED and result.first_bad is not None


def test_two_verdicts_exist_and_no_third() -> None:
    """`:1769` leaves "no room for manual correction"; a `PARTIAL` state would be one."""
    assert [v.value for v in Verdict] == ["Verified OK", "TAMPERED"]


# --- the visible fields must agree with the seal ----------------------------------------


def test_rewriting_only_the_displayed_move_is_tampered() -> None:
    """The commitment binds the payload, not the record's own `move` key — which is what a
    viewer paints. Without this check, a forger leaves the seal intact, rewrites only the
    display, and collects a green stamp over a game nobody played. `:1691`."""
    record = _record(1, move="N")
    record["move"] = "S"
    check = verify_record(record)
    assert check.verdict is Verdict.TAMPERED
    assert "contradicts the sealed payload" in check.reason


def test_a_payload_that_is_not_an_object_still_verifies_by_its_digest() -> None:
    """An opponent may seal an array rather than an object. The digest binds it; there are
    simply no named fields to cross-check. Refusing would fail rule 36 on a shape opinion."""
    payload = ["N", 1, True]
    record = {"step": 1, "move": "N", "payload": payload, "nonce": NONCE,
              "commit": _commit(payload)}
    assert verify_record(record).ok
