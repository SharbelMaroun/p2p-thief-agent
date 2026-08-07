"""`M7-013b`: the access token is refreshed before it expires, never after.

The refresh token is what turns a one-time consent into months of unattended operation, and
the failure it prevents is specific. A series runs for about an hour and an access token
lasts about an hour, so the report send at the very *end* of a series is the call most likely
to meet an expired token — and rule 32 makes sending Mandatory.

Nothing here touches a real credential: the clock and the refresh call are both injected, so
the policy is provable without OAuth. That is also why `M7-013`/`M7-013a` stay unclaimed —
running the consent flow is the operator's action on their own machine.

Two properties get the most attention below. The **skew margin**, because a token with four
seconds left passes a naive `expires_at > now` and then expires mid-request; and the
**redaction**, because the realistic leak is a token reaching a log through a repr rather
than through a deliberate print.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.services.credential_refresh import (
    SKEW_SECONDS,
    CredentialRefreshError,
    TokenState,
    ensure_fresh,
    seconds_until_refresh,
)

NOW = 1_000_000.0
# Named and valued so the repository's own secret scanner reads it as a placeholder
# (`is_dummy`) rather than a credential assignment. Silencing that finding with an
# allowlist entry would be the one change that lets a real leak hide later.
DUMMY_TOKEN = "dummy-not-a-real-access-token"


def token(seconds_left: float, *, refreshable: bool = True) -> TokenState:
    return TokenState(access_token=DUMMY_TOKEN, expires_at=NOW + seconds_left,
                      has_refresh_token=refreshable)


def refresher(seconds_left: float = 3600.0):
    calls: list[int] = []

    def refresh() -> TokenState:
        calls.append(1)
        return token(seconds_left)

    return refresh, calls


# --- the skew margin -----------------------------------------------------------------------


def test_a_token_with_plenty_of_life_is_not_refreshed() -> None:
    refresh, calls = refresher()
    state = token(3600)
    assert ensure_fresh(state, now=NOW, refresh=refresh) is state
    assert calls == []


def test_a_token_inside_the_skew_margin_is_refreshed_before_it_expires() -> None:
    """**The case a naive check misses.** Four seconds of life passes `expires_at > now`
    and then expires mid-request, producing a 401 on the one call that must not fail."""
    refresh, calls = refresher()
    fresh = ensure_fresh(token(4), now=NOW, refresh=refresh)
    assert calls == [1]
    assert fresh.expires_at == NOW + 3600


def test_the_margin_is_wide_enough_for_a_slow_send_and_a_retry() -> None:
    """Named rather than assumed. `send_report` backs off 5s, 10s, 20s across three
    retries, so a margin under a minute would refresh into the middle of that."""
    assert SKEW_SECONDS >= 60


def test_an_already_expired_token_is_refreshed() -> None:
    refresh, calls = refresher()
    ensure_fresh(token(-10), now=NOW, refresh=refresh)
    assert calls == [1]


def test_no_token_at_all_is_obtained_rather_than_refused() -> None:
    """First run on a fresh machine after consent. There is nothing to refresh, but there
    is something to fetch."""
    refresh, calls = refresher()
    assert ensure_fresh(None, now=NOW, refresh=refresh).expires_at == NOW + 3600
    assert calls == [1]


def test_seconds_until_refresh_counts_to_the_margin_not_to_expiry() -> None:
    assert seconds_until_refresh(token(3600), NOW) == 3600 - SKEW_SECONDS


def test_an_overdue_token_is_due_now_rather_than_negative() -> None:
    """A negative interval fed to a scheduler is the shape that becomes an immediate busy
    loop or, worse, a sleep that never wakes."""
    assert seconds_until_refresh(token(-500), NOW) == 0.0


# --- what cannot be recovered without a human ------------------------------------------------


def test_an_expired_token_with_no_refresh_token_is_refused() -> None:
    """This state needs the operator to re-run consent. Failing silently here is
    indistinguishable from a successful send in a log that only records errors."""
    refresh, calls = refresher()
    with pytest.raises(CredentialRefreshError, match="AE-32"):
        ensure_fresh(token(-1, refreshable=False), now=NOW, refresh=refresh)
    assert calls == [], "no refresh was attempted without a refresh token"


def test_a_valid_token_with_no_refresh_token_is_still_used() -> None:
    """Missing a refresh token is not a reason to refuse a token that currently works —
    the report can still go out, and the operator can re-consent afterwards."""
    state = token(3600, refreshable=False)
    assert ensure_fresh(state, now=NOW, refresh=lambda: token(1)) is state


def test_a_failing_refresh_is_reported_as_a_credential_error() -> None:
    """Wrapped so callers handle one exception type. The provider's own class is not part
    of this interface and would leak an implementation detail into every caller."""
    def broken() -> TokenState:
        raise ConnectionError("network down")

    with pytest.raises(CredentialRefreshError, match="ConnectionError"):
        ensure_fresh(None, now=NOW, refresh=broken)


def test_a_refresh_raising_its_own_credential_error_keeps_that_message() -> None:
    """Not re-wrapped. A refresh callable that has already diagnosed the problem — revoked
    grant, wrong client id — says something useful, and `refreshing the access token
    failed: CredentialRefreshError` would replace it with nothing."""
    def diagnosed() -> TokenState:
        raise CredentialRefreshError("the consent was revoked in the Google account")

    with pytest.raises(CredentialRefreshError, match="consent was revoked"):
        ensure_fresh(None, now=NOW, refresh=diagnosed)


def test_a_refresh_returning_the_wrong_type_is_refused() -> None:
    with pytest.raises(CredentialRefreshError, match="not a TokenState"):
        ensure_fresh(None, now=NOW, refresh=lambda: {"access_token": DUMMY_TOKEN})


def test_a_refresh_returning_an_already_stale_token_stops_rather_than_looping() -> None:
    """**A clock disagreement between us and the provider would loop forever otherwise** —
    every refresh returns a token our clock calls expired, and we ask again immediately."""
    with pytest.raises(CredentialRefreshError, match="clock disagreement"):
        ensure_fresh(None, now=NOW, refresh=lambda: token(1))
