"""`M7-005f`: no report can be composed for a result that was not audited and agreed.

The gap this closes was a **layering** one, not a missing check. `orchestration/settlement.py`
already refused to agree without a passed audit — `agree(audit, ours, theirs)` takes the
audit first precisely so the ordering cannot be forgotten. But `compose_report` took a bare
result mapping, so nothing stopped a caller from skipping settlement entirely and emailing a
number the opponent had never confirmed.

Rule 36 makes the comprehensive mutual audit "a mandatory condition before agreement on the
JSON result". Rule 35 scores a conflicting report 0 for **both** teams. So the expensive
mistake is not sending a wrong number — it is sending a number the other side contradicts,
and that is what an unaudited send maximises.

The settlement record crosses the boundary rather than the module, so `reporting/` stays
free of `orchestration/` and a disconnected game can still emit its artifacts (`M7-023`).
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.orchestration.settlement import SeriesAudit, agree, settlement_record
from p2p_thief_agent.reporting.email_report import ReportSendError, compose_report

RESULT = {"total_score": 25}
PASSED = SeriesAudit(passed=True, sub_games=(1, 2), failed_at=None)
FAILED = SeriesAudit(passed=False, sub_games=(1,), failed_at=1, failed_steps=(7,))


def compose(settlement) -> object:
    return compose_report(result=RESULT, settlement=settlement, sender="me@example.com",
                          game_id="g42", team_code="sharNamr")


# --- the record the real settlement produces is the one that is accepted --------------------


def test_a_report_composes_from_a_real_agreed_settlement() -> None:
    """Against `settlement_record` output rather than a hand-written dict, so the two
    cannot drift into disagreeing about the key names."""
    settled = agree(PASSED, ours="survival", theirs="survival")
    assert compose(settlement_record(settled))["Subject"].endswith("g42")


@pytest.mark.parametrize(
    ("audit", "ours", "theirs", "why"),
    [(FAILED, "survival", "survival", "the audit did not pass"),
     (PASSED, "survival", "capture", "the two sides disagree — rule 35 is 0 for both"),
     (PASSED, "survival", None, "the opponent never answered")],
)
def test_no_settlement_short_of_agreed_can_be_reported(audit, ours, theirs, why) -> None:
    """Every non-agreed state, driven through the real `agree`. Each is a different
    failure with a different remedy, and none of them is a report."""
    settled = agree(audit, ours=ours, theirs=theirs)
    assert why  # the reason is documentation for the failure output, not an assertion
    with pytest.raises(ReportSendError, match=r"AE-3[56]"):
        compose(settlement_record(settled))


# --- the forged-consent shapes ----------------------------------------------------------------


def test_a_settlement_claiming_agreement_without_a_passed_audit_is_refused() -> None:
    """**The shape that matters.** `state: agreed` with `audit_passed: False` is what a
    hand-assembled record looks like when somebody wants the send to go through — rule 36
    puts the audit *before* agreement, so agreement alone is not evidence of it."""
    with pytest.raises(ReportSendError, match="AE-36"):
        compose({"state": "agreed", "audit_passed": False})


def test_a_missing_audit_flag_is_not_read_as_a_passed_audit() -> None:
    """`.get` returning `None` must not pass a truthiness check. An absent flag and a
    failed audit are both "not audited", and only an explicit `True` is evidence."""
    with pytest.raises(ReportSendError, match="AE-36"):
        compose({"state": "agreed"})


@pytest.mark.parametrize("truthy", [1, "yes", "True", [1]])
def test_a_truthy_non_boolean_audit_flag_is_refused(truthy: object) -> None:
    """`is not True`, not `not ...`. A JSON round-trip that turned the flag into the
    string "True" would otherwise satisfy a truthiness check."""
    with pytest.raises(ReportSendError, match="AE-36"):
        compose({"state": "agreed", "audit_passed": truthy})


@pytest.mark.parametrize("shape", [None, "agreed", 42, ["agreed"]])
def test_something_that_is_not_a_settlement_record_is_refused(shape: object) -> None:
    with pytest.raises(ReportSendError, match="AE-36"):
        compose(shape)


def test_the_refusal_names_the_state_so_the_operator_knows_the_remedy() -> None:
    """A conflict needs a human and the lecturer; an audit failure needs the evidence
    preserved. "Refused" alone sends someone to read the source."""
    with pytest.raises(ReportSendError, match="'conflict'"):
        compose({"state": "conflict", "audit_passed": True})
