"""The Gmail API envelope: base64url of the MIME bytes (`M7-014c`).

`users().messages().send` takes `userId="me"` and a body of `{"raw": <base64url>}`. Two
details in that sentence are where this goes wrong, and both are silent:

**base64url, not standard base64.** The alphabets differ in two characters — `+/` versus
`-_` — so a message encodes correctly under either and only *some* messages differ. A short
subject may never produce a `+` or `/`; a long attachment always will. Standard base64 here
fails on the report that carries the most data and passes every test written against a small
one, which is why the test for this uses a payload chosen to contain both characters.

**Padding.** Gmail accepts padded base64url, and `urlsafe_b64encode` emits padding, so it is
kept rather than stripped. Stripping is the widely-copied idiom from JWT, where padding is
forbidden — a different specification for a different field.

This module holds **no credentials and opens no connection**. It turns a composed message
into the dict the API client wants; the client itself is injected at the call site, which is
what lets `reporting/` stay transport-free (`M7-023`) and what makes this testable without
OAuth (`M7-013`, still unclaimed pending real credentials).
"""

from __future__ import annotations

import base64
from collections.abc import Mapping
from email.message import EmailMessage

# The Gmail API's alias for the authenticated user. A literal address here would be a second
# place the sender identity is configured, and the two would eventually disagree.
AUTHENTICATED_USER = "me"


class GmailWireError(ValueError):
    """Raised when a message cannot be put on the wire as the API expects it."""


def encode_raw(message: EmailMessage) -> str:
    """base64url the full MIME bytes, padding kept."""
    if not isinstance(message, EmailMessage):
        raise GmailWireError(f"expected an EmailMessage, got {type(message).__name__}")
    return base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")


def send_body(message: EmailMessage) -> dict[str, str]:
    """The request body for `users().messages().send`."""
    return {"raw": encode_raw(message)}


def decode_raw(body: Mapping[str, object]) -> bytes:
    """Recover the MIME bytes from a wire body.

    Present so a test can assert the round trip rather than compare against a hand-computed
    string — an encoder checked against a constant somebody derived with the same mistaken
    idiom proves only that the mistake is consistent.
    """
    raw = body.get("raw")
    if not isinstance(raw, str):
        raise GmailWireError("wire body has no string 'raw' field")
    try:
        return base64.urlsafe_b64decode(raw)
    except (ValueError, TypeError) as exc:
        raise GmailWireError(f"'raw' is not valid base64url: {exc}") from exc


def api_send(service: object, message: EmailMessage, *, user_id: str = AUTHENTICATED_USER):
    """Call `users().messages().send` on an injected service object.

    The service is injected rather than constructed. Building a `googleapiclient` resource
    needs credentials, and this repository does not hold any — `M7-013`/`M7-013a` are
    deliberately unclaimed because running the consent flow is the operator's action on
    their own machine, not something an agent should do for them.
    """
    try:
        request = service.users().messages().send(userId=user_id, body=send_body(message))
    except AttributeError as exc:
        raise GmailWireError(
            f"injected service does not expose users().messages().send: {exc}") from exc
    return request.execute()
