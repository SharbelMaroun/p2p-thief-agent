"""The Deadline Tracker subsystem: track in-flight requests and reap on breach (`M5-009`).

Book §8.4.1 / §9: every outbound request over MCP carries an expiry, and a request past
its expiry is a failure — reaped, never awaited ("Missing a Deadline is a Failure, Not
Patience"). This subsystem registers each outbound request under a key with a deadline
from the agreed limits, reaps the ones past expiry (`M5-009a`), and — when a technical
loss is declared — clears the queue cleanly so no orphaned pending request survives
(`M5-009b`).

It builds on the deadline primitives (`Deadline`, `RetryPolicy`) rather than restating
them; both live in the Deadline Tracker subsystem, so this is not a cross-subsystem
import. Time is injected, the same discipline the rest of the reliability layer follows.
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_thief_agent.services.deadlines import Deadline, RetryPolicy


class DeadlineTrackerError(RuntimeError):
    """Raised when a request is tracked twice while still in flight."""


class RequestTracker:
    """Tracks outbound requests by key and reaps those past their expiry."""

    __slots__ = ("_policy", "_pending")

    def __init__(self, policy: RetryPolicy) -> None:
        self._policy = policy
        self._pending: dict[object, Deadline] = {}

    @classmethod
    def from_match(cls, game: Mapping) -> RequestTracker:
        """Build a tracker whose deadlines use the agreed response timeout."""
        return cls(RetryPolicy.from_match(game))

    @property
    def pending(self) -> tuple:
        """Return the keys of every request still in flight, in insertion order."""
        return tuple(self._pending)

    def deadline(self, now: float) -> Deadline:
        """Open a bare deadline (satisfies the gateway's DeadlineTracker port)."""
        return self._policy.deadline(now)

    def track(self, key: object, now: float) -> Deadline:
        """Register an outbound request under ``key`` with a fresh expiry."""
        if key in self._pending:
            raise DeadlineTrackerError(f"request {key!r} is already in flight")
        deadline = self._policy.deadline(now)
        self._pending[key] = deadline
        return deadline

    def complete(self, key: object) -> None:
        """Mark a request answered and stop tracking it; unknown keys are ignored."""
        self._pending.pop(key, None)

    def reap(self, now: float) -> tuple:
        """Remove and return the keys of every request past its expiry.

        A reaped request is a failure the caller must act on — retry, or declare a
        technical loss and ``clear`` — never a request to keep awaiting (book §8.4.1).
        """
        expired = tuple(key for key, dl in self._pending.items() if dl.expired(now))
        for key in expired:
            del self._pending[key]
        return expired

    def clear(self) -> tuple:
        """Drop every pending request cleanly on a declared technical loss (`M5-009b`)."""
        dropped = tuple(self._pending)
        self._pending.clear()
        return dropped
