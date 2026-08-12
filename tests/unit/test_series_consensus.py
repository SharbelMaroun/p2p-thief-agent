"""Companion C-040: tolerate the post-series `series_consensus` envelope.

`uoh-ay26` closes a series with one extra `submit_audit`: empty records, a
`consensus_sha` over the six agreed result rows, `result_claim: "series_consensus"`.
It is a SHA exchange, never a game outcome. This side's wire model now parses it;
the inbound handler acknowledges it because `audit_records([])` verifies zero
records vacuously; and it can alter nothing, because every log is written before
the series finale arrives.
"""

import pytest

from p2p_thief_agent.protocol.wire import AuditPayload, WireError


def consensus(**extra: object) -> dict:
    return {"sender": "police", "records": [], "result_claim": "series_consensus",
            "consensus_sha": "ab" * 32, **extra}


def test_a_consensus_envelope_parses() -> None:
    audit = AuditPayload.from_dict(consensus())
    assert audit.result_claim == "series_consensus"
    assert audit.records == []


def test_a_consensus_with_records_is_refused() -> None:
    """A consensus that smuggles records is not a consensus."""
    record = {"payload": {"step": 1}, "nonce": "ab" * 16, "commit": "c" * 64}
    with pytest.raises(WireError):
        AuditPayload.from_dict(consensus(records=[record]))


def test_unknown_result_claims_are_still_refused() -> None:
    """Widening to one named extension is not accepting anything."""
    with pytest.raises(WireError):
        AuditPayload.from_dict(consensus(result_claim="vibes"))


def test_ordinary_game_claims_are_unchanged() -> None:
    audit = AuditPayload.from_dict(
        {"sender": "police", "records": [], "result_claim": "timeout"})
    assert audit.result_claim == "timeout"
