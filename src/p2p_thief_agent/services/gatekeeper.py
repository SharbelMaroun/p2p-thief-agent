"""The Gatekeeper: rate limiting and overflow queueing for outbound calls (`M5-004f`).

Guidelines section 5 is explicit about the shape: *"All external API calls must pass
through a centralized gatekeeper"*, rate limiting is *"enforced before every call"*,
and — the part that decides the design — **"Overflow is queued, not rejected."**

That is the opposite of the usual instinct. A full queue does not raise and does not
drop; it admits the work and reports the pressure, and `queue_status()` exists so a
caller can see depth and stats rather than guess. Only when the queue is *full* does
admission fail, and even then it fails loudly rather than silently discarding.

**What this guards.** Book chapter 9.3.1 places the Gatekeeper in the Watchdog
family and aims it at *outbound* calls — Gmail and LLM providers — to avoid spamming
a service or tripping a `429`. It is not the inbound peer mailbox: an opponent's turn
is admitted by `protocol/receive.TurnInbox`, which already deduplicates and rejects
replays. Confirmed against the pinned wire reference 2026-08-01 (`THIEF-002`: its behaviour is matched, its source never copied), which notes these limits are
mostly insurance, since ordinary play generates well under one call per minute.

**Rate is a token bucket (`AE-28`, `M7-003b`).** ``requests_per_minute`` becomes a bucket of
that many tokens refilling at ``rpm / 60`` per second (`services/token_bucket.py`): a call is
admitted iff a token is available, and one is consumed only on admission. This permits a
burst up to a minute's worth and then a steady rate — the behaviour a limiter in front of
Gmail/LLM needs to avoid a `429` without stalling play. Concurrency and the overflow queue
are separate concerns layered on top.

**Limits.** ``requests_per_minute`` and ``concurrent_requests`` are Appendix F table
19 `Minimum` values (30 and 2) and ``queue_depth`` likewise (100); all three live in
the shared, signed match object under ``rate_limiter_gatekeeper``. Time is injected,
so a rate limit is tested by moving a number rather than by waiting a minute.

`Minimum` here means the limit may be made **stricter**, never looser — a peer may
choose to send less often, never more.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from p2p_thief_agent.services.limits import read_limit
from p2p_thief_agent.services.token_bucket import TokenBucket

REQUESTS_PER_MINUTE = ("rate_limiter_gatekeeper", "requests_per_minute", 30)
CONCURRENT_REQUESTS = ("rate_limiter_gatekeeper", "concurrent_requests", 2)
QUEUE_DEPTH = ("rate_limiter_gatekeeper", "queue_depth", 100)

WINDOW_SECONDS = 60.0  # `requests_per_minute` refills at rpm / 60 tokens per second


class GatekeeperError(RuntimeError):
    """Raised when work cannot be admitted at all — never a silent drop."""


@dataclass(frozen=True, slots=True)
class QueueStatus:
    """What the gatekeeper is holding right now (guidelines `get_queue_status`)."""

    depth: int
    capacity: int
    in_flight: int
    admitted: int
    queued: int

    @property
    def full(self) -> bool:
        """Return whether another item would be refused."""
        return self.depth >= self.capacity


@dataclass
class Gatekeeper:
    """Admit outbound calls under an agreed rate, queueing overflow rather than
    rejecting it."""

    requests_per_minute: int = 30
    concurrent_requests: int = 2
    queue_depth: int = 100
    _bucket: TokenBucket = field(init=False, repr=False)
    _pending: list[object] = field(default_factory=list, repr=False)
    _in_flight: int = field(default=0, repr=False)
    _admitted: int = field(default=0, repr=False)
    _queued: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        # The rate limit is a token bucket (`AE-28`): burst up to a minute's worth, then
        # refill at rpm / 60 per second. Concurrency and the overflow queue are separate.
        self._bucket = TokenBucket(
            float(self.requests_per_minute), self.requests_per_minute / WINDOW_SECONDS
        )

    @classmethod
    def from_match(cls, game: Mapping[str, object]) -> Gatekeeper:
        """Read the agreed limits from the shared, signed match object."""
        return cls(
            requests_per_minute=read_limit(game, *REQUESTS_PER_MINUTE),
            concurrent_requests=read_limit(game, *CONCURRENT_REQUESTS),
            queue_depth=read_limit(game, *QUEUE_DEPTH),
        )

    def queue_status(self) -> QueueStatus:
        """Return depth and stats, as the guidelines require of a gatekeeper."""
        return QueueStatus(
            depth=len(self._pending),
            capacity=self.queue_depth,
            in_flight=self._in_flight,
            admitted=self._admitted,
            queued=self._queued,
        )

    def submit(self, item: object, now: float) -> bool:
        """Offer one unit of work. Returns whether it may proceed immediately.

        ``False`` means **queued, not rejected** — the guidelines' rule. The caller
        drains later; nothing is discarded. A token is consumed only when admitted.
        """
        if self._in_flight < self.concurrent_requests and self._bucket.allow(now):
            self._in_flight += 1
            self._admitted += 1
            return True
        if len(self._pending) >= self.queue_depth:
            raise GatekeeperError(
                f"gatekeeper queue is full at {self.queue_depth}; "
                f"refusing to discard work silently"
            )
        self._pending.append(item)
        self._queued += 1
        return False

    def complete(self) -> None:
        """Report that an in-flight call finished, freeing a concurrency slot."""
        self._in_flight = max(0, self._in_flight - 1)

    def drain(self, now: float) -> list[object]:
        """Release as much queued work as the rate and concurrency now allow."""
        released: list[object] = []
        while (self._pending and self._in_flight < self.concurrent_requests
               and self._bucket.allow(now)):
            released.append(self._pending.pop(0))
            self._in_flight += 1
            self._admitted += 1
        return released


def limits_from_match(game: Mapping[str, object]) -> dict[str, int]:
    """Return the agreed gatekeeper limits, for logging and the report."""
    return {
        "requests_per_minute": read_limit(game, *REQUESTS_PER_MINUTE),
        "concurrent_requests": read_limit(game, *CONCURRENT_REQUESTS),
        "queue_depth": read_limit(game, *QUEUE_DEPTH),
    }


def guard(gate: Gatekeeper, call: Callable[[], object], now: float) -> object:
    """Run ``call`` through the gate, always releasing its concurrency slot."""
    if not gate.submit(call, now):
        raise GatekeeperError("no capacity right now; the call was queued")
    try:
        return call()
    finally:
        gate.complete()
