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

# `M7-005f`: the audited-and-agreed settlement is now a required argument, not a caller's
# discipline. This is the shape `orchestration.settlement.settlement_record` produces.
AGREED = {"state": "agreed", "our_outcome": "survival", "their_outcome": "survival",
          "audit_passed": True, "audit_failed_at": None}

MSG = compose_report(result={"total_score": 25}, settlement=AGREED,
                     sender="me@example.com", game_id="g42", team_code="sharNamr")


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
    # Changed 2026-08-06 from a constant [5.0, 5.0] to a doubling [5.0, 10.0]. Both honour
    # Appendix F table 19's `Minimum` of 5s, so the original was not wrong -- this is a
    # deliberate strengthening, not a bug fix. A fixed delay against a provider that is
    # still throttling spends every retry at the same rate it has already refused.
    assert result == "ok" and sleeps == [5.0, 10.0]  # backed off twice, then delivered


def test_the_send_gives_up_loudly_after_the_retries() -> None:
    def always_429(_message: object) -> str:
        raise RateLimitError("429")

    with pytest.raises(ReportSendError, match="after 2 retries"):
        send_report(MSG, transport=always_429, submit=lambda call: call(),
                    sleep=lambda _s: None, max_retries=2)


# --- M7-014b / M7-015c / M7-013c: the gaps this repository had ------------------------


def test_the_subject_carries_the_eight_character_team_code() -> None:
    """Rule 45 (Mandatory): "a unique 8-character team identification code without
    spaces. Sanction: organizational failure that will prevent **automatic report
    assignment** to the team." The subject was deterministic before this and still
    unassignable — naming the game is not the same as naming the team."""
    from p2p_thief_agent.reporting.email_report import report_subject

    assert report_subject("sharNamr", "g42") == "[sharNamr] UOH26 Final Result g42"
    assert "sharNamr" in MSG["Subject"]


@pytest.mark.parametrize("bad", ["short", "waytoolongcode", "has spac", ""])
def test_a_team_code_that_is_not_eight_characters_is_refused(bad: str) -> None:
    from p2p_thief_agent.reporting.email_report import ReportSendError, report_subject

    with pytest.raises(ReportSendError, match="exactly 8 characters"):
        report_subject(bad, "g42")


def test_a_second_send_for_one_game_is_refused() -> None:
    """`M7-015c`. Rule 35: a conflicting report scores 0 for **both** teams, and two sends
    for one game is the easiest way to produce one by accident."""
    from p2p_thief_agent.reporting.email_report import ReportSendError, send_report

    sent: set[str] = set()
    kwargs = {
        "transport": lambda m: "ok", "submit": lambda call: call(),
        "sleep": lambda _s: None, "game_id": "g42", "sent_games": sent,
    }
    assert send_report(MSG, **kwargs) == "ok"
    with pytest.raises(ReportSendError, match="0 for BOTH teams"):
        send_report(MSG, **kwargs)


def test_a_missing_credential_fails_closed(tmp_path) -> None:
    """`M7-013c`. A skipped report is indistinguishable from a successful one in a log
    that only records errors, which is exactly why this must raise."""
    from p2p_thief_agent.reporting.email_report import ReportSendError, send_report

    with pytest.raises(ReportSendError, match="refusing to skip"):
        send_report(MSG, transport=lambda m: "ok", submit=lambda call: call(),
                    sleep=lambda _s: None, credential_path=tmp_path / "absent.json")


def test_the_backoff_doubles_rather_than_repeating() -> None:
    """A fixed delay against a provider that is still throttling spends every retry at the
    same rate it already refused."""
    from p2p_thief_agent.reporting.email_report import RateLimitError, ReportSendError, send_report

    slept: list[float] = []

    def throttled(_m):
        raise RateLimitError("429")

    with pytest.raises(ReportSendError):
        send_report(MSG, transport=throttled, submit=lambda call: call(),
                    sleep=slept.append, max_retries=2, backoff_seconds=5.0)
    assert slept == [5.0, 10.0, 20.0]
