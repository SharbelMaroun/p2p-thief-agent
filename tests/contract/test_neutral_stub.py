"""Bidirectional conformance against the independent Node neutral stub."""

import pytest

from p2p_thief_agent.protocol.canonical import canonicalize
from p2p_thief_agent.protocol.negotiation import accept_offer
from tests.contract.neutral_helpers import node_result, offer, offer_context


@pytest.mark.parametrize(
    ("proposer", "responder", "game_uid"),
    [("alpha", "beta", "game-alpha"), ("sharNamr", "group42", "game-sharNamr")],
)
def test_python_offer_is_accepted_by_neutral_stub(
    proposer: str, responder: str, game_uid: str
) -> None:
    """Two match identities pass without editing a profile file."""
    proposed = offer(proposer, responder, game_uid)
    response = node_result(
        {"op": "accept_offer", "offer": proposed, "context": offer_context(proposed)}
    )

    assert response["ok"] is True
    assert response["ack"] == accept_offer(proposed, expected_recipient=responder, now_ms=150)


def test_neutral_offer_is_accepted_by_python() -> None:
    """The reverse proposal direction uses no project serializer in the producer."""
    expected = offer("neutral", "sharNamr", "game-neutral")
    command = {
        "op": "make_offer",
        **{
            key: expected[key]
            for key in (
                "proposer_group_id",
                "proposer_role",
                "responder_group_id",
                "responder_role",
                "game_id",
                "game_uid",
                "sub_game_number",
                "message_id",
                "negotiation_id",
                "sent_at_ms",
                "expires_at_ms",
                "step_zero",
                "optional_capabilities",
            )
        },
        "game_source_b64": expected["configuration"]["game_source_b64"],
        "rate_limits_source_b64": expected["configuration"]["rate_limits_source_b64"],
    }
    response = node_result(command)

    assert response["ok"] is True
    assert (
        accept_offer(response["offer"], expected_recipient="sharNamr", now_ms=150)["status"]
        == "accepted"
    )


@pytest.mark.parametrize(
    "value",
    [
        {"z": [3, {"β": "é", "a": True}], "a": {"n": None, "arr": [2, 1]}},
        {"numbers": [333333333.33333329, 1e30, 4.5, 2e-3, 1e-27]},
        {"text": 'quote=" backslash=\\ line=\n tab=\t nul=\x00 slash=/'},
        {"decomposed": "e\u0301", "emoji": "😀", "é": "café"},
    ],
)
def test_cross_language_rfc8785_vectors(value: object) -> None:
    """Nested, number, escaping, and non-BMP vectors reproduce independently."""
    response = node_result({"op": "canonicalize", "value": value})

    assert response == {"ok": True, "canonical": canonicalize(value).decode()}
