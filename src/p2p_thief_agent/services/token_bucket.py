"""Token-bucket rate limiter (`M7-003b`, `AE-28`).

Appendix E rule 28 names the algorithm exactly: a bucket of at most `C` tokens refills at
`r` tokens per second, `tokens ← min(C, tokens + r·Δt)`, and a call is allowed **iff**
`tokens ≥ 1`, consuming one. This permits a burst up to `C` and then a steady `r`, which is
what a rate limiter in front of Gmail/LLM providers needs to avoid a `429` without stalling
ordinary play.

Time is **injected** — every method takes `now` — so a rate is tested by advancing a number
rather than by waiting. Time that appears to move backwards contributes no refill rather than
draining the bucket, so a clock hiccup can never manufacture or destroy allowance.
"""

from __future__ import annotations


class TokenBucketError(ValueError):
    """Raised when a bucket is configured with a non-positive capacity or refill rate."""


class TokenBucket:
    """A refilling bucket: burst up to ``capacity``, then ``refill_per_second`` steady."""

    __slots__ = ("_last", "_tokens", "capacity", "refill_per_second")

    def __init__(self, capacity: float, refill_per_second: float) -> None:
        if capacity <= 0:
            raise TokenBucketError(f"capacity must be positive, got {capacity}")
        if refill_per_second <= 0:
            raise TokenBucketError(f"refill_per_second must be positive, got {refill_per_second}")
        self.capacity = float(capacity)
        self.refill_per_second = float(refill_per_second)
        self._tokens = float(capacity)  # start full: a fresh bucket permits an immediate burst
        self._last: float | None = None

    def _refill(self, now: float) -> None:
        if self._last is not None:
            elapsed = max(0.0, now - self._last)  # backwards time adds nothing, never drains
            self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_per_second)
        self._last = now

    def available(self, now: float) -> float:
        """Return the tokens available now, without consuming one."""
        self._refill(now)
        return self._tokens

    def allow(self, now: float) -> bool:
        """Consume one token if available; return whether the call may proceed (`AE-28`)."""
        self._refill(now)
        if self._tokens >= 1.0:
            self._tokens -= 1.0
            return True
        return False
