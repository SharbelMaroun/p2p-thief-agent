"""The two gates this repository was missing, and the pipeline that orders all three.

`inst/police_thief_p2p_Summary.md:2096` fixes the flow before any Gmail call:

    Outgoing report -> Quota Manager -> Token Bucket -> DOS Detector -> Gmail API

with a distinct outcome at each (`:2098`): "Rejected (quota full)", "Blocked (no token)",
"LOCKED (anomaly)". Three names because they differ in **remedy** — *try tomorrow*, *try
shortly*, *the code is wrong* — and collapsing them into one "blocked" would send all
three down the same wrong path.

`services/token_bucket.TokenBucket` already implements the middle gate correctly. The
other two were absent, so a report could reach Gmail having passed one gate of three.

**Quota Manager** (`:2083`) — "a counter that tracks the number of operations performed in
a given day and prevents crossing the daily threshold. This is the **final line before
account blocking**: if the quota is exhausted, no further requests are sent."

**DOS Detector** (`:2087`, rule 29 Mandatory) — "identifies patterns of excessive sending
that indicate **a bug or an infinite loop in the agent's code**". Note what it guards
against: not a hostile peer, but our own runaway. So its lock does **not** clear itself —
a detector that reset after a quiet spell would let the same loop resume the moment it
briefly looked calm.

**One API difference worth naming.** This repository's `TokenBucket.allow` *consumes* a
token, where a pure `available` query is what a fail-fast check needs. `attempt` therefore
inspects with `available` and only `send` calls `allow`. Copying a design that assumed a
side-effect-free `allow` would have burned a token on every request the DOS gate refused —
a silent, gradual throttle that nothing would have reported.

**Fail-fast is correctness, not efficiency.** Each gate has a side effect, so running a
later gate after an earlier refusal corrupts the counters the gates exist to protect: a
request rejected on quota must not burn a token, and a token-blocked request must not
register as a send in the DOS window, or a legitimately throttled burst would look like a
runaway loop and lock the pipeline for the wrong reason.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from p2p_thief_agent.services.token_bucket import TokenBucket

SECONDS_PER_DAY = 86_400
# Appendix F table 19 `Minimum`; the only number here with book authority.
DEFAULT_REQUESTS_PER_MINUTE = 30
# Ours. `:2083` names a "daily threshold" without fixing it, and the provider's own
# ceiling is the real constraint.
DEFAULT_DAILY_QUOTA = 100
# Ours too: "excessive sending that indicates a bug" is a behaviour, not a number.
DEFAULT_BURST_WINDOW_SECONDS = 10.0
DEFAULT_BURST_LIMIT = 12


class SendVerdict(StrEnum):
    """Why a send did or did not go out. Three refusals, three remedies."""

    ALLOWED = "allowed"
    REJECTED_QUOTA = "rejected_quota"      # try tomorrow
    BLOCKED_NO_TOKEN = "blocked_no_token"  # try shortly
    LOCKED_ANOMALY = "locked_anomaly"      # the code is wrong; a human must look


@dataclass
class QuotaManager:
    """`M7-006a`: the per-day counter, last line before the provider blocks the account."""

    daily_quota: int = DEFAULT_DAILY_QUOTA
    _used: int = 0
    _day: int | None = None

    def _roll(self, now: float) -> None:
        day = int(now // SECONDS_PER_DAY)
        if self._day != day:
            self._day, self._used = day, 0

    def remaining(self, now: float) -> int:
        self._roll(now)
        return max(0, self.daily_quota - self._used)

    def allow(self, now: float) -> bool:
        return self.remaining(now) > 0

    def record(self, now: float) -> None:
        self._roll(now)
        self._used += 1


@dataclass
class DosDetector:
    """`M7-006b`: catches our own runaway loop and locks the pipeline `[AE-29]`."""

    window_seconds: float = DEFAULT_BURST_WINDOW_SECONDS
    burst_limit: int = DEFAULT_BURST_LIMIT
    _sends: list[float] = field(default_factory=list)
    locked: bool = False

    def record(self, now: float) -> None:
        self._sends = [t for t in self._sends if now - t < self.window_seconds]
        self._sends.append(now)
        if len(self._sends) > self.burst_limit:
            self.locked = True

    def allow(self, now: float) -> bool:
        """Locked stays locked — see the module docstring."""
        del now
        return not self.locked


@dataclass(frozen=True, slots=True)
class SendDecision:
    """Whether a send may proceed, and which gate refused it."""

    verdict: SendVerdict
    gate: str | None = None

    @property
    def allowed(self) -> bool:
        return self.verdict is SendVerdict.ALLOWED


@dataclass
class SendPipeline:
    """`M7-006c`: the three gates in the book's order, first refusal short-circuiting."""

    quota: QuotaManager = field(default_factory=QuotaManager)
    bucket: TokenBucket = field(
        default_factory=lambda: TokenBucket(
            capacity=DEFAULT_REQUESTS_PER_MINUTE,
            refill_per_second=DEFAULT_REQUESTS_PER_MINUTE / 60.0,
        )
    )
    detector: DosDetector = field(default_factory=DosDetector)

    @classmethod
    def from_match(cls, game: Mapping[str, object]) -> SendPipeline:
        """Read the rate from the signed match object. Table 19 makes 30 a `Minimum`, so a
        negotiated higher value is honoured rather than clamped back to the floor."""
        section = game.get("rate_limiter_gatekeeper")
        rate = DEFAULT_REQUESTS_PER_MINUTE
        if isinstance(section, Mapping):
            value = section.get("requests_per_minute")
            if isinstance(value, int) and not isinstance(value, bool) and value > 0:
                rate = value
        return cls(bucket=TokenBucket(capacity=rate, refill_per_second=rate / 60.0))

    def attempt(self, now: float) -> SendDecision:
        """Ask each gate in order, stopping at the first refusal without touching the rest."""
        if not self.quota.allow(now):
            return SendDecision(SendVerdict.REJECTED_QUOTA, "quota")
        # `available`, not `allow`: this repository's `TokenBucket.allow` CONSUMES a
        # token, so checking with it would burn one even when the DOS gate then refuses --
        # which is precisely the fail-fast invariant this ordering exists to preserve.
        if self.bucket.available(now) < 1.0:
            return SendDecision(SendVerdict.BLOCKED_NO_TOKEN, "bucket")
        if not self.detector.allow(now):
            return SendDecision(SendVerdict.LOCKED_ANOMALY, "detector")
        return SendDecision(SendVerdict.ALLOWED)

    def send(self, transmit: Callable[[], object], now: float) -> tuple[SendDecision, object]:
        """Run the gates and, only if all three allow, transmit."""
        decision = self.attempt(now)
        if not decision.allowed:
            return decision, None
        # Consume before transmitting: a send that raises still happened as far as the
        # provider is concerned, and a gate that counted only successes would let a
        # failing loop retry without limit -- the runaway rule 29 exists to stop.
        self.bucket.allow(now)  # the consuming call; `attempt` above only inspected
        self.quota.record(now)
        self.detector.record(now)
        return decision, transmit()
