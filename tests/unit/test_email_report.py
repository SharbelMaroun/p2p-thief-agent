"""`M7-005`: compose and send the final report through Gmail (mocked transport)."""

import json

import pytest

from p2p_thief_agent.reporting.email_report import (
    GMAIL_SEND_SCOPE,
    REPORTING_ADDRESS,
    RateLimitError,
    ReportSendError,
    compose_report,
    send_report,
)
from p2p_thief_agent.services.gatekeeper import Gatekeeper, guard

MSG = compose_report(result={"total_score": 25}, sender="me@example.com", game_id="g42")


def test_the_oauth_scope_is_send_only() -> None:
    """`M7-005a`: gmail.send, never read or modify."""
    assert GMAIL_SEND_SCOPE.endswith("gmail.send")
    assert "readonly" not in GMAIL_SEND_SCOPE and "modify" not in GMAIL_SEND_SCOPE


def test_the_report_is_a_json_attachment_to_the_confirmed_address() -> None:
    """`M7-005c`/`M7-005d`: the JSON rides as an attachment, not the body, to the AF-020 address."""
    assert MSG["To"] == REPORTING_ADDRESS
    attachments = list(MSG.iter_attachments())
    assert len(attachments) == 1
    att = attachments[0]
    assert att.get_filename() == "result_g42.json"
    assert att.get_content_type() == "application/json"
    assert json.loads(att.get_payload(decode=True))["total_score"] == 25
    body = MSG.get_body(preferencelist=("plain",)).get_content()
    assert "total_score" not in body  # the report is not in the body


def test_the_send_routes_through_the_one_gatekeeper() -> None:
    """`M7-003a`/`M7-005g`: the report is admitted by the gate and sent independently."""
    gate = Gatekeeper(requests_per_minute=30, concurrent_requests=2, queue_depth=10)
    sent: list[object] = []
    result = send_report(MSG, transport=lambda m: sent.append(m) or "ok",
                         submit=lambda call: guard(gate, call, 0.0), sleep=lambda _s: None)
    assert result == "ok" and len(sent) == 1 and gate.queue_status().admitted == 1


def test_a_429_is_backed_off_and_retried() -> None:
    """`M7-005e`: an immediate resend risks suspension, so a 429 waits and retries."""
    attempts, sleeps = {"n": 0}, []

    def transport(_message: object) -> str:
        attempts["n"] += 1
        if attempts["n"] <= 2:
            raise RateLimitError("429 rate limit")
        return "ok"

    result = send_report(MSG, transport=transport, submit=lambda call: call(),
                         sleep=sleeps.append, max_retries=3, backoff_seconds=5.0)
    assert result == "ok" and sleeps == [5.0, 5.0]  # backed off twice, then delivered


def test_the_send_gives_up_loudly_after_the_retries() -> None:
    def always_429(_message: object) -> str:
        raise RateLimitError("429")

    with pytest.raises(ReportSendError, match="after 2 retries"):
        send_report(MSG, transport=always_429, submit=lambda call: call(),
                    sleep=lambda _s: None, max_retries=2)
