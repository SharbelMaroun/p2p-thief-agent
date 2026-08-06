"""`M8-008d`: detecting a reordered log — and deliberately not bannering it.

Every commitment covers one record, so shuffling, deleting or duplicating records leaves
**every digest valid**. A hash-only verifier stamps `Verified OK` on all three; that is
what the companion repository does today, and what this module exists to catch.

The design point is which way the finding flows. Both sources say sequence checking is
neither mandated nor implemented:

* the **book** — rule 19 is "any mismatch **in the digest**" (p.129/271); a missing step is
  instead "contradictory reports" under rule 35 (p.131/275) and an illegal state jump under
  rule 5, both of which carry *different sanctions* from rule 19;
* the **reference** — `verify_record` checks each record "with no reference to its place in
  the sequence or the value of the `step` field", `normalize_log` neither sorts nor
  re-indexes, and nothing rejects a duplicate or missing step.

So a differently-ordered log is not evidence of forgery, and red-bannering one would be a
false accusation carrying no appeal (`:1769`) — with rule 35 scoring zero for *both* teams
if we then filed a contradicting report. Detect and report; let settlement decide.
"""

from __future__ import annotations

import hashlib
import json

from p2p_thief_agent.replay import Verdict, inspect_sequence, verify_records

NONCE = "c3" * 16


def _record(step: int) -> dict:
    payload = {"step": step, "move": "NSEW"[step % 4]}
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return {"step": step, "move": payload["move"], "payload": payload, "nonce": NONCE,
            "commit": hashlib.sha256(f"{canonical}|{NONCE}".encode()).hexdigest()}


def _records(count: int = 5) -> list[dict]:
    return [_record(n) for n in range(1, count + 1)]


# --- the finding the digests cannot make ------------------------------------------------


def test_a_clean_log_reports_an_intact_sequence() -> None:
    report = inspect_sequence(_records(5))
    assert report.contiguous
    assert report.summary == "sequence intact — 5 steps, 1..5"


def test_a_reordered_log_is_detected() -> None:
    """`M8-008d`. Every digest is still valid here — the shuffle is the whole forgery."""
    records = _records(5)
    shuffled = [records[i] for i in (0, 3, 1, 4, 2)]

    assert verify_records(shuffled).verdict is Verdict.VERIFIED_OK, "hashes cannot see it"
    report = inspect_sequence(shuffled)
    assert not report.contiguous
    assert any(f.kind == "out-of-order" for f in report.findings)


def test_a_deleted_step_is_detected_as_a_gap() -> None:
    """The companion repository's equivalent test asserted only that its *fixture* had a
    gap, never that the code noticed. This one asserts the product."""
    records = _records(5)
    del records[2]

    assert verify_records(records).verdict is Verdict.VERIFIED_OK
    report = inspect_sequence(records)
    finding = next(f for f in report.findings if f.kind == "gap")
    assert "[3]" in finding.detail and finding.rule == "AE-35"


def test_a_duplicated_step_is_detected() -> None:
    records = _records(4)
    records.insert(2, records[1])

    assert verify_records(records).verdict is Verdict.VERIFIED_OK
    finding = next(f for f in inspect_sequence(records).findings if f.kind == "duplicate")
    assert "[2]" in finding.detail


def test_records_without_an_integer_step_are_reported_not_crashed_on() -> None:
    records = _records(3)
    records[1] = {**records[1], "step": "two"}
    assert any(f.kind == "unnumbered" for f in inspect_sequence(records).findings)


def test_a_boolean_step_is_not_mistaken_for_an_integer() -> None:
    """`True == 1` in Python, so a bool would silently pass an `isinstance(int)` check and
    read as step 1 — the kind of forgery that survives precisely because it type-checks."""
    records = _records(2)
    records[0] = {**records[0], "step": True}
    assert any(f.kind == "unnumbered" for f in inspect_sequence(records).findings)


def test_an_empty_log_reports_nothing_rather_than_raising() -> None:
    assert inspect_sequence([]).contiguous


# --- the separation itself is the design decision ----------------------------------------


def test_a_structural_anomaly_never_changes_the_cryptographic_verdict() -> None:
    """**The assertion this module exists for.** Neither the book nor the reference
    requires ordering, so a differently-ordered honest log must not be red-bannered —
    `:1769` gives that verdict no appeal, and rule 35 would score zero for both teams."""
    records = _records(6)
    mangled = [records[i] for i in (5, 0, 1, 3, 4)]  # shuffled and one deleted

    assert verify_records(mangled).verdict is Verdict.VERIFIED_OK
    assert not inspect_sequence(mangled).contiguous


def test_every_finding_names_the_rule_it_answers_to() -> None:
    """The sanctions differ — rule 19 is 0 for the falsifying group, rule 35 is 0 for
    both — so a finding that does not name its rule invites the wrong one being applied."""
    records = _records(5)
    del records[1]
    records.append(records[0])
    for finding in inspect_sequence(records).findings:
        assert finding.rule.startswith("AE-") and finding.detail


def test_the_summary_of_a_damaged_log_lists_every_finding_with_its_rule() -> None:
    """What an operator actually reads. A summary that said only "sequence problem" would
    leave them guessing which sanction applies, which is the whole reason for the split."""
    records = _records(5)
    del records[2]
    records.append(records[0])

    summary = inspect_sequence(records).summary
    assert "gap" in summary and "duplicate" in summary
    assert "[AE-35]" in summary
    assert "intact" not in summary
