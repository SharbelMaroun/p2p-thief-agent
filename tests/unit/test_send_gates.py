"""`M7-006`: the two gates this repository was missing, and the order of all three.

`:2096` fixes the flow before any Gmail call — Quota Manager, Token Bucket, DOS Detector,
Gmail — with three distinct outcomes (`:2098`) because they differ in remedy: *try
tomorrow*, *try shortly*, *the code is wrong*.

`services/token_bucket` already implemented the middle gate correctly, so a report could
previously reach Gmail having passed **one gate of three**.

One API difference is worth the attention it gets below: this repository's
`TokenBucket.allow` *consumes* a token. A fail-fast check needs a pure query, so `attempt`
inspects with `available` and only `send` calls `allow` — otherwise every request the DOS
gate refused would still have burned a token, a silent gradual throttle nothing reports.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.services.send_gates import (
    DosDetector,
    QuotaManager,
    SendPipeline,
    SendVerdict,
)
from p2p_thief_agent.services.token_bucket import TokenBucket

DAY = 86_400.0


def _empty_bucket() -> TokenBucket:
    bucket = TokenBucket(capacity=1, refill_per_second=0.0001)
    bucket.allow(0.0)  # drain the one token it starts with
    return bucket


# --- M7-006a: the daily quota ------------------------------------------------------------


def test_the_quota_stops_sending_when_exhausted() -> None:
    """`:2083`: "the **final line before account blocking**: if the quota is exhausted, no
    further requests are sent"."""
    quota = QuotaManager(daily_quota=2)
    for _ in range(2):
        assert quota.allow(0.0)
        quota.record(0.0)
    assert not quota.allow(0.0)


def test_the_quota_rolls_over_at_a_day_boundary() -> None:
    quota = QuotaManager(daily_quota=1)
    quota.record(0.0)
    assert not quota.allow(0.0) and quota.allow(DAY + 1)


# --- M7-006b: the DOS detector -----------------------------------------------------------


def test_a_runaway_burst_locks_the_pipeline() -> None:
    """`:2087`: it detects "a bug or an infinite loop **in the agent's code**", and rule 29
    (Mandatory) sanctions with "locking of the interface to prevent account blocking"."""
    detector = DosDetector(window_seconds=10, burst_limit=3)
    for _ in range(4):
        detector.record(0.0)
    assert detector.locked and not detector.allow(0.0)


def test_the_lock_does_not_clear_itself() -> None:
    """It guards against *our own* runaway, so a lock that reset after a quiet spell would
    let the same loop resume the moment it briefly looked calm."""
    detector = DosDetector(window_seconds=1, burst_limit=1)
    detector.record(0.0)
    detector.record(0.0)
    assert not detector.allow(10_000.0)


def test_steady_sending_within_the_limit_never_locks() -> None:
    detector = DosDetector(window_seconds=10, burst_limit=3)
    for tick in range(10):
        detector.record(tick * 20.0)
    assert not detector.locked


# --- M7-006c: fail-fast ordering ----------------------------------------------------------


def test_the_gates_run_in_the_books_order() -> None:
    assert SendPipeline(quota=QuotaManager(daily_quota=0)).attempt(0.0).gate == "quota"
    assert SendPipeline(bucket=_empty_bucket()).attempt(0.0).gate == "bucket"
    locked = DosDetector(window_seconds=1, burst_limit=0)
    locked.record(0.0)
    assert SendPipeline(detector=locked).attempt(0.0).gate == "detector"


def test_a_refused_attempt_never_consumes_a_token() -> None:
    """The bug the `available`/`allow` distinction prevents. With this repository's
    consuming `allow`, a naive check would burn a token on every request a *later* gate
    refused — throttling us gradually for sends that never happened, and reporting
    nothing."""
    locked = DosDetector(window_seconds=1, burst_limit=0)
    locked.record(0.0)
    pipeline = SendPipeline(detector=locked)
    before = pipeline.bucket.available(0.0)
    pipeline.attempt(0.0)
    assert pipeline.bucket.available(0.0) == before


def test_a_blocked_send_does_not_register_in_the_dos_window() -> None:
    """Otherwise a legitimately throttled burst looks like a runaway loop and locks the
    pipeline for the wrong reason — a self-inflicted outage."""
    pipeline = SendPipeline(bucket=_empty_bucket(),
                            detector=DosDetector(window_seconds=10, burst_limit=1))
    for _ in range(5):
        pipeline.attempt(0.0)
    assert not pipeline.detector.locked


def test_an_allowed_send_transmits_and_consumes_from_every_gate() -> None:
    pipeline = SendPipeline(quota=QuotaManager(daily_quota=5))
    decision, result = pipeline.send(lambda: "sent", 0.0)
    assert decision.verdict is SendVerdict.ALLOWED and result == "sent"
    assert pipeline.quota.remaining(0.0) == 4


def test_a_refused_send_never_calls_the_transmitter() -> None:
    def explode() -> object:
        raise AssertionError("transmitted despite a refusal")

    decision, result = SendPipeline(quota=QuotaManager(daily_quota=0)).send(explode, 0.0)
    assert decision.verdict is SendVerdict.REJECTED_QUOTA and result is None


def test_a_transmitter_that_raises_still_counts_against_the_gates() -> None:
    """A gate counting only successes would let a failing loop retry without limit."""
    pipeline = SendPipeline(quota=QuotaManager(daily_quota=5))
    with pytest.raises(RuntimeError):
        pipeline.send(lambda: (_ for _ in ()).throw(RuntimeError("gmail down")), 0.0)
    assert pipeline.quota.remaining(0.0) == 4


def test_the_rate_comes_from_the_signed_match_object() -> None:
    """Table 19 makes 30 a `Minimum`, so a negotiated higher value is honoured rather than
    clamped back to the floor — clamping a minimum is the classic misreading."""
    pipeline = SendPipeline.from_match({"rate_limiter_gatekeeper": {"requests_per_minute": 45}})
    assert pipeline.bucket.capacity == 45
    assert SendPipeline.from_match({}).bucket.capacity == 30
