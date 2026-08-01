"""`M5-010a`: a transport fault is retried; a content rejection never is.

The two failure kinds must be handled oppositely. Re-sending a sealed turn's bytes after
a transport blip is safe — the receiver keys on ``(step, sender)`` — so a `TransportError`
is retried up to the agreed limit. A `PeerRejectionError` means the opponent was reached
and declined, so it terminates the exchange at once and reaches a defined terminal state
(`M5-010b`). Time is injected.
"""

import pytest

from p2p_thief_agent.adapters.fastmcp_client import PeerRejectionError, TransportError
from p2p_thief_agent.orchestration.delivery import deliver
from p2p_thief_agent.services.deadlines import DeadlineError, RetryPolicy

POLICY = RetryPolicy(max_retries=3, backoff_sec=5, response_timeout_sec=30)


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


def test_a_successful_delivery_returns_the_acknowledgement() -> None:
    clock = Clock()
    ack = deliver(lambda _m: {"ok": True}, {"step": 1}, policy=POLICY, clock=clock, sleep=clock.sleep)
    assert ack == {"ok": True}


def test_a_transient_transport_fault_is_retried_then_succeeds() -> None:
    clock, calls = Clock(), []

    def send(_message: dict) -> dict:
        calls.append(1)
        if len(calls) < 3:
            raise TransportError("tunnel blip")
        return {"ok": True}

    assert deliver(send, {"step": 1}, policy=POLICY, clock=clock, sleep=clock.sleep) == {"ok": True}
    assert len(calls) == 3


def test_a_persistent_transport_fault_exhausts_the_budget_and_raises() -> None:
    clock = Clock()

    def send(_message: dict) -> dict:
        raise TransportError("unreachable")

    with pytest.raises(DeadlineError, match="exhausted"):
        deliver(send, {"step": 1}, policy=POLICY, clock=clock, sleep=clock.sleep)


def test_a_rejection_is_not_retried_and_terminates_at_once() -> None:
    clock, calls = Clock(), []

    def send(_message: dict) -> dict:
        calls.append(1)
        raise PeerRejectionError("declined")

    with pytest.raises(PeerRejectionError):
        deliver(send, {"step": 1}, policy=POLICY, clock=clock, sleep=clock.sleep)
    assert len(calls) == 1, "a rejection terminates immediately, no retry"
