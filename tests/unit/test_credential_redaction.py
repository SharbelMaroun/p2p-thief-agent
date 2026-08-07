"""`M7-013b`, the other half: the token value never leaves the object.

Split from `test_credential_refresh.py`, which covers *when* to refresh. This covers what
must never happen while doing it. The two carry different consequences — a missed refresh
costs the report; a leaked token in git history is rule 39, which forbids pushing secrets
"even if it is private and shared only with the lecturer".

Every test here attacks the same assumption: that a secret only escapes when somebody prints
it. The realistic paths are a debugger repr, an exception message quoting a failed request,
and a provider error that echoes its own input.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.services.credential_refresh import (
    CredentialRefreshError,
    TokenState,
    ensure_fresh,
)

NOW = 1_000_000.0
# Named and valued so the repository's own secret scanner reads it as a placeholder
# (`is_dummy`) rather than a credential assignment.
DUMMY_TOKEN = "dummy-not-a-real-access-token"


def token(seconds_left: float, *, refreshable: bool = True) -> TokenState:
    return TokenState(access_token=DUMMY_TOKEN, expires_at=NOW + seconds_left,
                      has_refresh_token=refreshable)


# --- the token value never leaves ---------------------------------------------------------------


def test_the_repr_redacts_the_token() -> None:
    """The realistic leak is not a deliberate print — it is a token reaching a log through
    a debugger repr or an exception message. Rule 39 forbids secrets in the repository
    "even if it is private and shared only with the lecturer"."""
    assert DUMMY_TOKEN not in repr(token(3600))
    assert "<redacted>" in repr(token(3600))


def test_the_refusal_messages_carry_no_token_value() -> None:
    """An exception message is the most common way a secret reaches a log file."""
    with pytest.raises(CredentialRefreshError) as caught:
        ensure_fresh(token(-1, refreshable=False), now=NOW, refresh=lambda: token(1))
    assert DUMMY_TOKEN not in str(caught.value)


def test_the_wrapped_provider_error_carries_only_the_exception_type() -> None:
    """A provider exception often quotes the request, and the request carries the token."""
    def leaky() -> TokenState:
        raise ValueError(f"bad grant for {DUMMY_TOKEN}")

    with pytest.raises(CredentialRefreshError) as caught:
        ensure_fresh(None, now=NOW, refresh=leaky)
    assert DUMMY_TOKEN not in str(caught.value)
