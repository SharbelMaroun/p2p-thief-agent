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
import re
from collections.abc import Callable, Mapping
from email.message import EmailMessage
from pathlib import Path

GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"  # send only, no read/modify
REPORTING_ADDRESS = "rmisegal+uoh26finalgame@gmail.com"  # AF-020; Table 20 "rimesegal" is a typo
# Rule 45 (Mandatory): "enter a unique 8-character team identification code without
# spaces. Sanction: organizational failure that will prevent AUTOMATIC REPORT ASSIGNMENT
# to the team." A subject without it is deterministic but unassignable.
_TEAM_CODE = re.compile(r"[A-Za-z0-9]{8}")

# The transport actually delivers the message and returns a provider response, or raises
# RateLimitError on an HTTP 429. Injected so the live googleapiclient adapter stays out of here.
SendTransport = Callable[[EmailMessage], object]


class RateLimitError(RuntimeError):
    """Raised by a transport on an HTTP 429 — the caller must back off, not resend at once."""


class ReportSendError(RuntimeError):
    """Raised when the report could not be delivered after the configured retries."""


def report_subject(team_code: str, game_id: str) -> str:
    """The machine-read subject. Rule 45 ties automatic assignment to the team code, so a
    subject that merely names the game is deterministic and still unassignable."""
    if not isinstance(team_code, str) or _TEAM_CODE.fullmatch(team_code) is None:
        raise ReportSendError(
            f"team code {team_code!r} must be exactly 8 characters without spaces [AE-45]"
        )
    return f"[{team_code}] UOH26 Final Result {game_id}"


def _require_agreed(settlement: Mapping) -> None:
    """Refuse to compose a report for a result that was not audited and then agreed.

    Rule 36 makes the comprehensive mutual audit "a mandatory condition before agreement on
    the JSON result", and rule 35 scores a conflicting report 0 for **both** teams. Until
    now `compose_report` took a bare result mapping, so the ordering lived entirely in the
    caller — and a precondition a caller can forget is not a precondition, which is the
    argument `orchestration/settlement.agree` already makes by taking its audit first.

    The `settlement_record` mapping crosses this boundary, not the module: `reporting/`
    stays free of `orchestration/`, so a disconnected game can still emit its artifacts
    (`M7-023`).
    """
    if not isinstance(settlement, Mapping):
        raise ReportSendError("compose_report needs the settlement record [AE-36]")
    if settlement.get("state") != "agreed" or settlement.get("audit_passed") is not True:
        raise ReportSendError(
            f"refusing to compose a report for a settlement in state "
            f"{settlement.get('state')!r} with audit_passed="
            f"{settlement.get('audit_passed')!r}; rule 36 makes the mutual audit a "
            "mandatory condition before agreement, and rule 35 scores a conflicting "
            "report 0 for BOTH teams [AE-35] [AE-36]")


def compose_report(*, result: Mapping, settlement: Mapping, sender: str, game_id: str,
                   team_code: str, recipient: str = REPORTING_ADDRESS) -> EmailMessage:
    """Build the report email: the result JSON as an attachment, never as body text.

    `settlement` is the `settlement_record` from `orchestration/settlement.py` (`M7-005f`).
    """
    _require_agreed(settlement)
    message = EmailMessage()
    message["To"] = recipient
    message["From"] = sender
    message["Subject"] = report_subject(team_code, game_id)  # M7-014b
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
    game_id: str | None = None,
    sent_games: set[str] | None = None,
    credential_path: Path | None = None,
) -> object:
    """Send the report through the gate, backing off on a 429 (`M7-005e`, `M7-005g`).

    `submit` routes the call through the gatekeeper (e.g. a partial of `guard`). The send does
    not wait on the opponent — a side that does not send scores nothing, whatever the other does.
    """
    # `M7-015c`. Rule 35 scores a conflicting report 0 for BOTH teams, and two sends for
    # one game is the easiest way to produce one by accident.
    if game_id is not None and sent_games is not None and game_id in sent_games:
        raise ReportSendError(
            f"{game_id} was already reported; a second report risks the rule 35 conflict "
            "verdict, which scores 0 for BOTH teams"
        )
    # `M7-013c`. A missing credential must not degrade into "skipped the report": that
    # failure is indistinguishable from success in a log that only records errors.
    if credential_path is not None and not Path(credential_path).exists():
        raise ReportSendError(
            f"no Gmail credential at {credential_path!r}; refusing to skip a Mandatory "
            "report [AE-32]. Run the one-time consent flow first"
        )
    last_error: RateLimitError | None = None
    for attempt in range(max_retries + 1):
        try:
            response = submit(lambda: transport(message))
        except RateLimitError as exc:
            last_error = exc
            # Doubling, not constant: a fixed delay against a provider that is still
            # throttling just spends every retry at the same rate it already refused.
            sleep(backoff_seconds * (2 ** attempt))
            continue
        if game_id is not None and sent_games is not None:
            sent_games.add(game_id)
        return response
    raise ReportSendError(f"report send failed after {max_retries} retries: {last_error}")
