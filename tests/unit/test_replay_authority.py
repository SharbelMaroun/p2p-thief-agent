"""`M8-002d`: which hash construction the replay verifier is allowed to use.

The row this closes, and `C-016` with it, was written on a wrong premise: that chapter 5
and chapter 7 disagree and we owe the lecturer a disclosure.

Asked directly, the sources say otherwise in the book's own voice at `:1757` (p.58/146):
"the sketch simplified the input for the sake of the illustration; in practice the
signature covers all components of the step — Intent, Move, State and Nonce — as detailed
in the protocol in Chapter 5." `DEV-SPEC.md:435` annotates its own copy of the listing the
same way — "(example; real seal covers State|Move|Intent|Nonce)".

So chapter 7's listing is a **teaching simplification that names chapter 5 as normative**,
not a rival specification. Filing it as a conflict would have asked the lecturer to settle
something the source already settles. What is owed is this note, not a disclosure.

The tests pin the difference so nobody "fixes" our verifier towards p.74 later.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from p2p_thief_agent.replay import LogNotReplayableError, Verdict, parse_log, verify_records

NONCE = "a1" * 16


def _canonical(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _record(step: int, move: str = "N") -> dict:
    payload = {"step": step, "move": move, "intent": True}
    return {"step": step, "sender": "thief", "move": move, "payload": payload, "nonce": NONCE,
            "commit": hashlib.sha256(f"{_canonical(payload)}|{NONCE}".encode()).hexdigest()}


# --- the chapter-7 sketch and why we do not implement it --------------------------------


def test_the_chapter_seven_sketch_would_verify_none_of_our_records() -> None:
    """`:1733` computes `sha256(f"{nonce}|{move}")`: nonce first, and only the bare move.
    The difference is total rather than subtle — a viewer written to the sketch would
    red-banner an honest log at step 1 and disqualify us under `:1769`."""
    record = _record(1)
    sketch = hashlib.sha256(f"{record['nonce']}|{record['move']}".encode()).hexdigest()
    assert sketch != record["commit"]


def test_our_construction_is_payload_then_nonce_not_nonce_then_move() -> None:
    """Pins both differences separately, so a future "fix" that swaps only the order — or
    only the content — still fails. Either alone would look like a plausible correction."""
    payload = {"step": 1, "move": "N", "intent": True}
    ours = hashlib.sha256(f"{_canonical(payload)}|{NONCE}".encode()).hexdigest()

    swapped = hashlib.sha256(f"{NONCE}|{_canonical(payload)}".encode()).hexdigest()
    bare_move = hashlib.sha256(f"{_canonical(payload['move'])}|{NONCE}".encode()).hexdigest()
    assert ours != swapped
    assert ours != bare_move


def test_the_sealed_payload_covers_intent_which_the_sketch_would_leave_unbound() -> None:
    """`:1757` names Intent explicitly among the components the real signature covers.
    Under the sketch a bluff flag could be rewritten for free — and rule 22 turns a false
    capture declaration into "score of zero and technical loss without right of appeal"."""
    honest = _record(1)
    lied = {**honest, "payload": {**honest["payload"], "intent": False}}
    assert verify_records([lied]).verdict is Verdict.TAMPERED


# --- an in-play log is refused, not accused ---------------------------------------------


def test_a_log_whose_nonces_are_all_absent_is_refused_rather_than_called_tampered() -> None:
    """Rule 18 *requires* an in-play log to have no nonces. Stamping it `TAMPERED` would
    accuse an honest peer of the one thing `:1769` gives no appeal against."""
    in_play = {"records": [{k: v for k, v in _record(n).items() if k not in ("nonce", "payload")}
                           for n in (1, 2)]}
    with pytest.raises(LogNotReplayableError, match="in-play log"):
        parse_log(in_play)


def test_the_refusal_names_the_rule_and_points_at_settlement() -> None:
    """A peer who never reveals is a settlement matter, not a forgery. The message has to
    say so, or an operator reaches for the wrong sanction."""
    with pytest.raises(LogNotReplayableError, match="settlement matter"):
        parse_log({"records": [{"step": 1, "commit": "0" * 64}]})


def test_but_a_log_missing_only_some_nonces_goes_through_and_fails() -> None:
    """Revealed and then interfered with — that is forgery, and it must reach a verdict."""
    log = {"records": [_record(1), _record(2), _record(3)]}
    del log["records"][1]["nonce"]
    assert verify_records(parse_log(log).records).verdict is Verdict.TAMPERED
