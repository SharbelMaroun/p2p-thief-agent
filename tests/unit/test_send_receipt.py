"""`M9-010c`: a send receipt claims exactly what a sender can know.

The book's decisive layer of proof is **receipt at the lecturer's address** (p.78/183) — and
that is the one we cannot observe; only the recipient can. So the test that matters here is
not that a receipt is stored, it is that the record never claims more than API acceptance.

The reference implementation records nothing at all: its sender returns `{status, reason}`
for a CLI line and none of it reaches the artifacts, so after a series the only evidence a
report was sent is somebody's memory.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.reporting.send_receipt import EvidenceError, SendReceipt


def receipt(gid: str) -> SendReceipt:
    return SendReceipt.from_api_response({"id": f"msg-{gid}"}, game_id=gid,
                                         sent_at="2026-08-07T12:00:00+03:00",
                                         recipient="rmisegal+uoh26finalgame@gmail.com")


def test_a_receipt_records_the_provider_message_id() -> None:
    assert receipt("g1").message_id == "msg-g1"


def test_a_receipt_states_that_it_evidences_acceptance_not_receipt() -> None:
    """**The test this module exists for.** "Proof the report was sent" invites the stronger
    reading, and the book's condition is receipt at the lecturer's address. The record says
    so in its own words rather than leaving a reader to infer the limit."""
    assert receipt("g1").as_record()["evidences"] == (
        "API acceptance, not receipt by the lecturer")


def test_the_class_is_not_named_for_delivery() -> None:
    """Naming carries the distinction where a docstring would be skipped."""
    assert SendReceipt.__name__ == "SendReceipt"


def test_a_send_response_with_no_message_id_is_refused() -> None:
    """Afterwards, a report that failed to send and one that sent without a receipt look
    identical — and only one of them costs the game's points."""
    with pytest.raises(EvidenceError, match="AE-32"):
        SendReceipt.from_api_response({}, game_id="g1", sent_at="t", recipient="r")


@pytest.mark.parametrize("response", [{"id": ""}, {"id": None}, {"id": 42}, {"labelIds": []}])
def test_a_response_whose_id_is_not_a_usable_string_is_refused(response: dict) -> None:
    with pytest.raises(EvidenceError, match="AE-32"):
        SendReceipt.from_api_response(response, game_id="g1", sent_at="t", recipient="r")


@pytest.mark.parametrize("field_name", ["game_id", "message_id", "sent_at", "recipient"])
def test_every_receipt_field_is_required(field_name: str) -> None:
    values = {"game_id": "g", "message_id": "m", "sent_at": "t", "recipient": "r"}
    values[field_name] = ""
    with pytest.raises(EvidenceError, match=field_name):
        SendReceipt(**values)
