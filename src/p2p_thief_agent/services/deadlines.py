"""Deadline tracking and bounded retry (`M5-004a`, `M5-004b`, `M5-009`).

Book section 8.4.1, and its boxed note is the whole design: *"Missing a Deadline is a
Failure, Not Patience."* Every request over MCP carries a timestamp and an expiry, and
when the expiry passes the peer must **retry, or declare a technical loss and clear
the queue cleanly** — never keep waiting. The book names an un-expiring pending
request as the direct path to freezing.

So waiting is always bounded here, and running out of attempts is a decision rather
than a hang.

**Where the numbers come from.** All four live in the *shared, signed* match object,
so neither peer can quietly give itself a longer rope. Confirmed against the pinned
wire reference 2026-08-01, which reads exactly these keys:

- ``network_and_league.response_timeout_sec`` — request expiry, default 30
- ``network_and_league.watchdog_timeout_sec`` — watchdog trip, default 60
- ``rate_limiter_gatekeeper.retry_backoff_sec`` — wait between retries, default 5
- ``rate_limiter_gatekeeper.max_retries`` — retries after the first try, default 3

Appendix F table 19 marks the first, third and fourth `Minimum` — they may be made
stricter, never looser — while the watchdog timeout is `Negotiation`.
`protocol/agreement.check_appendix_f` owns enforcing the floors; this module only
reads what was agreed.

**Time is injected.** ``now`` is always a parameter, never a hidden clock call, so a
timeout is exercised by passing a number instead of sleeping through it.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from p2p_thief_agent.services.limits import (
    MARGIN,
    MAX_RETRIES,
    RESPONSE_TIMEOUT,
    RETRY_BACKOFF,
    WATCHDOG_TIMEOUT,
    read_limit,
)


class DeadlineError(RuntimeError):
    """Raised when a bounded wait ran out — a decision, never a hang."""


@dataclass(frozen=True, slots=True)
class Deadline:
    """One request's expiry. Past it, the request has failed."""

    started: float
    expires: float

    @classmethod
    def starting_at(cls, now: float, timeout: float) -> Deadline:
        """Open a deadline of ``timeout`` seconds from ``now``."""
        if timeout <= 0:
            raise DeadlineError(f"timeout must be positive, got {timeout!r}")
        return cls(started=now, expires=now + timeout)

    def expired(self, now: float) -> bool:
        """Return whether the expiry has passed; the boundary itself counts."""
        return now >= self.expires

    def remaining(self, now: float) -> float:
        """Return seconds left, never negative."""
        return max(0.0, self.expires - now)


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """How many further attempts are allowed, and how long to wait between them."""

    max_retries: int
    backoff_sec: float
    response_timeout_sec: float

    @classmethod
    def from_match(cls, game: Mapping) -> RetryPolicy:
        """Read the agreed limits out of the shared, signed match object."""
        return cls(
            max_retries=read_limit(game, *MAX_RETRIES),
            backoff_sec=read_limit(game, *RETRY_BACKOFF),
            response_timeout_sec=read_limit(game, *RESPONSE_TIMEOUT),
        )

    @property
    def attempts(self) -> int:
        """Total tries: the first, plus the permitted retries."""
        return self.max_retries + 1

    @property
    def call_timeout_sec(self) -> float:
        """Cap one outbound call so a *retry* still fits inside the signed deadline.

        **Added 2026-08-10, same defect as the companion Cop.** ``FastMCPClient`` accepts a
        ``timeout`` but ``serve`` never passed one, so ``self._timeout is None`` and every live
        call waited indefinitely. The breach is arithmetic rather than networking: the MCP
        SDK's own per-call default equals the 30s we sign as ``response_timeout_sec``, so one
        delivered-but-unanswered push, one backoff, and a second push exceed the deadline while
        **each individual call looks healthy** -- we breach a deadline we signed and hand
        ourselves the technical loss.

        ``attempts`` calls at the cap must fit the whole deadline, making the budget over the
        attempt count the largest legal cap: 7.5s of a 30s deadline at Appendix F's three
        retries. ``MARGIN`` binds only when a peer negotiates **zero** retries -- ``attempts``
        is then 1 and the division alone would hand one call the entire deadline, leaving
        nothing for transport, which is the very breach this prevents.

        The arithmetic lives in ``services.limits`` so the MCP connector can reach it without
        importing this subsystem; this property is the same rule expressed over an already-read
        policy, and must not drift from it.
        """
        return min(self.response_timeout_sec / self.attempts, self.response_timeout_sec * MARGIN)

    def deadline(self, now: float) -> Deadline:
        """Open one request's deadline at ``now``."""
        return Deadline.starting_at(now, self.response_timeout_sec)


def attempt(
    action: Callable[[], object],
    policy: RetryPolicy,
    *,
    clock: Callable[[], float],
    sleep: Callable[[float], None] = lambda _seconds: None,
    retry_on: tuple[type[BaseException], ...] = (Exception,),
) -> object:
    """Run ``action`` under a deadline, retrying a bounded number of times.

    Each attempt gets its own expiry. A retry happens only while attempts remain
    *and* the clock has not passed that expiry; otherwise this raises, so the caller
    can declare a technical loss and clear its queue — the two outcomes section 8.4.1
    permits. It never returns having quietly given up.
    """
    last: BaseException | None = None
    for remaining in range(policy.attempts - 1, -1, -1):
        deadline = policy.deadline(clock())
        try:
            return action()
        except retry_on as exc:
            last = exc
            if remaining == 0:
                break
            if deadline.expired(clock()):
                raise DeadlineError(
                    f"attempt exceeded its {policy.response_timeout_sec}s expiry: {exc}"
                ) from exc
            sleep(policy.backoff_sec)
    raise DeadlineError(
        f"exhausted {policy.attempts} attempts ({policy.max_retries} retries): {last}"
    ) from last


def limits_from_match(game: Mapping) -> dict:
    """Return every agreed reliability limit, for logging and the report."""
    return {
        "response_timeout_sec": read_limit(game, *RESPONSE_TIMEOUT),
        "watchdog_timeout_sec": read_limit(game, *WATCHDOG_TIMEOUT),
        "retry_backoff_sec": read_limit(game, *RETRY_BACKOFF),
        "max_retries": read_limit(game, *MAX_RETRIES),
    }
