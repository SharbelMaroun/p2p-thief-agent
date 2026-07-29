"""Independent check that the neutral peer requires the live-reveal capability."""

from tests.contract.neutral_helpers import node_result, offer, offer_context


def _result_for(proposed: dict) -> dict:
    """Validate one incoming offer against its own active context."""
    return node_result({
        "op": "accept_offer",
        "offer": proposed,
        "context": offer_context(proposed),
    })


def test_live_reveal_is_required_while_control_remains_optional() -> None:
    """The neutral peer rejects the old capability set before gameplay."""
    missing_reveal = offer("alpha", "beta", "missing-reveal")
    missing_reveal["required_capabilities"].remove("receive_reveal")
    assert _result_for(missing_reveal)["rejection"]["error"]["code"] == (
        "CAPABILITY_MISMATCH"
    )

    without_control = offer("alpha", "beta", "without-control")
    without_control["optional_capabilities"] = []
    response = _result_for(without_control)
    assert response["ok"] is True
    assert response["ack"]["accepted_capabilities"] == [
        "negotiate",
        "receive_move",
        "receive_reveal",
        "submit_audit",
    ]
