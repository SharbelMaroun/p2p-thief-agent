"""`M7-014c`, the call: `users().messages().send` with the body it expects.

Split from `test_gmail_wire.py`, which proves the *encoding*. This proves the **call shape**
and the refusals around it — a different concern with a different failure: a wrong encoding
corrupts a report that arrives, a wrong call shape means nothing arrives at all.

The service object is injected and records rather than sends, so the API contract is
provable with no credential and no connection. That is deliberate: `M7-013`/`M7-013a` stay
unclaimed because running the consent flow is the operator's action on their own machine.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.reporting.email_report import compose_report
from p2p_thief_agent.reporting.gmail_wire import (
    AUTHENTICATED_USER,
    GmailWireError,
    api_send,
    decode_raw,
    encode_raw,
)

AGREED = {"state": "agreed", "our_outcome": "survival", "their_outcome": "survival",
          "audit_passed": True, "audit_failed_at": None}
RESULT = {"total_score": 25, "sub_games": [{"n": n, "tokens": 1000 + n} for n in range(1, 7)]}


def message():
    return compose_report(result=RESULT, settlement=AGREED, sender="me@example.com",
                          game_id="g42", team_code="sharNamr")


class FakeSend:
    """Records what the API would have been asked to do. Opens nothing."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def users(self):
        return self

    def messages(self):
        return self

    def send(self, *, userId: str, body: dict):  # noqa: N803 — the API's own parameter name
        self.calls.append({"userId": userId, "body": body})
        return self

    def execute(self):
        return {"id": "sent-1", "labelIds": ["SENT"]}


# --- the call ----------------------------------------------------------------------------------


def test_the_send_uses_the_authenticated_user_alias() -> None:
    """`userId="me"`. A literal address here would be a second place the sender identity is
    configured, and the two would eventually disagree."""
    service = FakeSend()
    assert api_send(service, message())["id"] == "sent-1"
    assert service.calls[0]["userId"] == AUTHENTICATED_USER == "me"


def test_the_send_passes_the_wire_body_rather_than_the_message() -> None:
    service = FakeSend()
    api_send(service, message())
    assert set(service.calls[0]["body"]) == {"raw"}


# --- refusals ------------------------------------------------------------------------------------


def test_encoding_something_that_is_not_a_message_is_refused() -> None:
    """A `str` would encode happily and produce a body Gmail rejects at send time, which is
    the one moment there is nothing useful to do about it."""
    with pytest.raises(GmailWireError, match="expected an EmailMessage"):
        encode_raw("Subject: hi\r\n\r\nbody")  # type: ignore[arg-type]


def test_a_service_without_the_send_chain_is_refused_clearly() -> None:
    """The realistic injection mistake is passing the credentials object instead of the
    built service; `AttributeError` deep in a chain says nothing about which."""
    with pytest.raises(GmailWireError, match="users\\(\\).messages\\(\\).send"):
        api_send(object(), message())


@pytest.mark.parametrize("body", [{}, {"raw": None}, {"raw": 7}])
def test_a_wire_body_without_a_string_raw_is_refused(body: dict) -> None:
    with pytest.raises(GmailWireError, match="no string 'raw' field"):
        decode_raw(body)


def test_a_raw_field_that_is_not_base64url_is_refused() -> None:
    with pytest.raises(GmailWireError, match="not valid base64url"):
        decode_raw({"raw": "not base64!!"})
