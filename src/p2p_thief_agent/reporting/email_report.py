"""Compose and send the final report through Gmail (`M7-005`).

The Gmail API is external, so the send routes through the **one** gatekeeper (`M7-003a`) and
the transport is **injected**. The tests mock that transport; the live `gmail.send` adapter —
which needs OAuth and credentials (Appendix A, `U-009`, `M7-013`) and whether the default is
*draft* or *send* — is **not** built here and awaits the coordinator's `U-009` ruling.

What is fixed: the OAuth scope is `gmail.send` only (`AE-30`); the report is the result JSON
as an **attachment**, never the body (`AE-33`, `AE-34`); it goes to the confirmed address
(`AF-020`); it is sent **independently of the opponent** (`AE-32`, `AE-35`); and a `429` is
backed off, never hammered (book §12, `AE-29` risk of account suspension).
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from email.message import EmailMessage

GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"  # send only, no read/modify
REPORTING_ADDRESS = "rmisegal+uoh26finalgame@gmail.com"  # AF-020; Table 20 "rimesegal" is a typo

# The transport actually delivers the message and returns a provider response, or raises
# RateLimitError on an HTTP 429. Injected so the live googleapiclient adapter stays out of here.
SendTransport = Callable[[EmailMessage], object]


class RateLimitError(RuntimeError):
    """Raised by a transport on an HTTP 429 — the caller must back off, not resend at once."""


class ReportSendError(RuntimeError):
    """Raised when the report could not be delivered after the configured retries."""


def compose_report(*, result: Mapping, sender: str, game_id: str,
                   recipient: str = REPORTING_ADDRESS) -> EmailMessage:
    """Build the report email: the result JSON as an attachment, never as body text."""
    message = EmailMessage()
    message["To"] = recipient
    message["From"] = sender
    message["Subject"] = f"UOH26 Final Result — {game_id}"  # deterministic subject (M7-014b)
    message.set_content("Final result attached as JSON; this message carries no report in its body.")
    payload = json.dumps(dict(result), ensure_ascii=False, indent=2).encode("utf-8")
    message.add_attachment(payload, maintype="application", subtype="json",
                           filename=f"result_{game_id}.json")
    return message


def send_report(
    message: EmailMessage,
    *,
    transport: SendTransport,
    submit: Callable[[Callable[[], object]], object],
    sleep: Callable[[float], None],
    max_retries: int = 3,
    backoff_seconds: float = 5.0,
) -> object:
    """Send the report through the gate, backing off on a 429 (`M7-005e`, `M7-005g`).

    `submit` routes the call through the gatekeeper (e.g. a partial of `guard`). The send does
    not wait on the opponent — a side that does not send scores nothing, whatever the other does.
    """
    last_error: RateLimitError | None = None
    for _ in range(max_retries + 1):
        try:
            return submit(lambda: transport(message))
        except RateLimitError as exc:
            last_error = exc
            sleep(backoff_seconds)
    raise ReportSendError(f"report send failed after {max_retries} retries: {last_error}")
