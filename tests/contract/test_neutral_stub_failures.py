"""Independent neutral-stub hashes and fail-closed negotiation vectors."""

import pytest

from p2p_thief_agent.protocol.canonical import agreed_configuration_sha256
from p2p_thief_agent.protocol.negotiation import accept_offer
from p2p_thief_agent.protocol.profile import ConformanceError
from tests.contract.neutral_helpers import node_result, offer, offer_context


def test_config_hash_matches_independent_implementation() -> None:
    """Semantic configuration uses a separate, reproduced hash domain."""
    game = {"agreed_between": ["alpha", "beta"], "rate": 0.1, "steps": 35}
    rate_limits = {"concurrent_requests": 2, "requests_per_minute": 30}

    response = node_result({"op": "config_hash", "game": game, "rate_limits": rate_limits})

    assert response["sha256"] == agreed_configuration_sha256(game, rate_limits)


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        ("version", "UNSUPPORTED_VERSION"),
        ("participant", "IDENTITY_MISMATCH"),
        ("hash", "HASH_MISMATCH"),
        ("unknown", "UNKNOWN_FIELD"),
        ("value", "CONFIG_MISMATCH"),
    ],
)
def test_neutral_stub_rejects_negative_offer_vectors(mutation: str, code: str) -> None:
    """Version, identity, hash, fields, and selected-value mismatches fail closed."""
    proposed = offer("alpha", "beta", "game-negative")
    context = offer_context(proposed)
    command = {"op": "accept_offer", "offer": proposed, "context": context}
    if mutation == "version":
        proposed["supported_versions"] = ["2.0"]
    elif mutation == "participant":
        context["local_group_id"] = "other"
    elif mutation == "hash":
        proposed["configuration"]["game_source_sha256"] = "f" * 64
    elif mutation == "unknown":
        proposed["extension"] = {}
    else:
        context["agreed_configuration_sha256"] = "f" * 64

    response = node_result(command)

    assert response["ok"] is False
    assert response["rejection"]["error"]["code"] == code
    assert response["rejection"]["status"] == "rejected"
    assert response["rejection"]["acknowledges"] == proposed.get("message_id")
    assert set(response["rejection"]) == {"status", "acknowledges", "error"}


def test_python_rejects_selected_value_mismatch() -> None:
    """Self-consistent bytes cannot override the locally selected agreement."""
    proposed = offer("neutral", "sharNamr", "game-values")

    with pytest.raises(ConformanceError) as captured:
        accept_offer(
            proposed,
            expected_recipient="sharNamr",
            now_ms=150,
            expected_configuration_sha256="f" * 64,
        )

    assert captured.value.code == "CONFIG_MISMATCH"
