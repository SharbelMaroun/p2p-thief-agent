"""When to refresh the Gmail access token, and what to do when it cannot be (`M7-013b`).

The refresh token is what turns a one-time consent into months of unattended operation. A
series can run for an hour and the access token expires in about one, so the failure this
prevents is specific: the report send at the very end of a series is the call most likely to
meet an expired token, and rule 32 makes sending Mandatory.

**This module holds no credential and performs no network call.** The refresh itself is an
injected callable and the clock is injected too, so the *policy* — when to refresh, what
counts as expired, what happens when refresh fails — is provable without OAuth. Running the
consent flow is the operator's action on their own machine (`M7-013`, `M7-013a`, deliberately
unclaimed), and an agent should not be creating or reading real credentials on their behalf.

**Nothing here ever returns, logs or formats a token value.** `TokenState.__repr__` redacts,
because the realistic leak is not a deliberate print — it is a token reaching a log through
an exception message or a debugger repr, and rule 39 forbids secrets in the repository "even
if it is private and shared only with the lecturer".

The **skew margin** matters more than it looks. A token with four seconds left passes a
naive `expires_at > now` and expires mid-request, producing a 401 on the one call that must
not fail. Refreshing early costs a cheap round trip; refreshing late costs the report.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

# Refresh this far before the stated expiry. Long enough to cover a slow send plus a retry,
# short enough that a normally-issued hour-long token is not refreshed on every call.
SKEW_SECONDS = 300.0


class CredentialRefreshError(RuntimeError):
    """Raised when a usable access token cannot be obtained without human action."""


@dataclass(frozen=True, slots=True)
class TokenState:
    """An access token and when it stops working. The value never leaves this object."""

    access_token: str
    expires_at: float
    has_refresh_token: bool = True

    def __repr__(self) -> str:
        """Redacted deliberately. A token reaching a log through a debugger repr or an
        exception message is the realistic leak, not a deliberate print.

        Done here rather than with `field(repr=False)` for two reasons. A hand-written
        `__repr__` is what the test asserts against, so the redaction cannot be lost to a
        refactor that rebuilds the field list — and `field(repr=False)` puts the field name,
        a colon, a type and an equals sign on one line, which the repository's own secret
        scanner reads as a credential assignment. Silencing that would have meant an
        allowlist entry, and an allowlist is where a real leak eventually hides.
        """
        return (f"TokenState(access_token=<redacted>, expires_at={self.expires_at}, "
                f"has_refresh_token={self.has_refresh_token})")

    def expired(self, now: float, *, skew: float = SKEW_SECONDS) -> bool:
        """True while there is less than `skew` left, not merely once the moment passes."""
        return now >= self.expires_at - skew


def ensure_fresh(
    state: TokenState | None,
    *,
    now: float,
    refresh: Callable[[], TokenState],
    skew: float = SKEW_SECONDS,
) -> TokenState:
    """Return a token good for the next `skew` seconds, refreshing only if it is not.

    Refuses rather than refreshes when there is no refresh token: that state needs the
    operator to re-run consent, and a silent failure here is indistinguishable from a
    successful send in a log that only records errors (`M7-013c`).
    """
    if state is not None and not state.expired(now, skew=skew):
        return state
    if state is not None and not state.has_refresh_token:
        raise CredentialRefreshError(
            "the access token has expired and there is no refresh token; re-run the "
            "one-time consent flow — refusing to skip a Mandatory report [AE-32]")
    try:
        refreshed = refresh()
    except CredentialRefreshError:
        raise
    except Exception as exc:  # noqa: BLE001 — the provider's exception type is not ours
        raise CredentialRefreshError(
            f"refreshing the access token failed: {type(exc).__name__}") from exc
    if not isinstance(refreshed, TokenState):
        raise CredentialRefreshError(
            f"refresh returned {type(refreshed).__name__}, not a TokenState")
    if refreshed.expired(now, skew=skew):
        raise CredentialRefreshError(
            "refresh returned a token that is already inside the skew margin; a clock "
            "disagreement here would loop, so it stops instead")
    return refreshed


def seconds_until_refresh(state: TokenState, now: float, *, skew: float = SKEW_SECONDS) -> float:
    """How long until a refresh is due. Never negative — an overdue token is due *now*."""
    return max(0.0, state.expires_at - skew - now)
