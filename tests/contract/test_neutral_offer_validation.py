"""Independent closed-offer, active-context, and source validation negatives."""

import base64

import pytest

from p2p_thief_agent.protocol.canonical import (
    agreed_configuration_sha256,
    canonicalize,
    loads,
    source_sha256,
)
from tests.contract.neutral_helpers import node_result, offer, offer_context


def result_for(proposed: dict, context: dict | None = None) -> dict:
    """Validate one incoming offer against its active context."""
    return node_result({
        "op": "accept_offer",
        "offer": proposed,
        "context": context or offer_context(proposed),
    })


def rewrite_participants(proposed: dict, participants: list[str]) -> None:
    """Keep every hash self-consistent while changing the semantic binding."""
    config = proposed["configuration"]
    game = loads(base64.b64decode(config["game_source_b64"]))
    rates = loads(base64.b64decode(config["rate_limits_source_b64"]))
    game["agreed_between"] = participants
    raw = canonicalize(game)
    config["game_source_b64"] = base64.b64encode(raw).decode()
    config["game_source_sha256"] = source_sha256("game.json", raw)
    config["agreed_configuration_sha256"] = agreed_configuration_sha256(game, rates)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("profile", "UNSUPPORTED_PROFILE"),
        ("required_order", "CAPABILITY_MISMATCH"),
        ("optional_duplicate", "CAPABILITY_MISMATCH"),
        ("step_unknown", "UNKNOWN_FIELD"),
        ("config_unknown", "UNKNOWN_FIELD"),
        ("negative_zero", "MALFORMED"),
        ("bad_message_id", "MALFORMED"),
    ],
)
def test_closed_offer_and_primitives_fail(mutation: str, expected: str) -> None:
    proposed = offer("alpha", "beta", "offer-errors")
    if mutation == "profile":
        proposed["profile"] = "other"
    elif mutation == "required_order":
        proposed["required_capabilities"].reverse()
    elif mutation == "optional_duplicate":
        proposed["optional_capabilities"].append("receive_control")
    elif mutation == "step_unknown":
        proposed["step_zero"]["extra"] = True
    elif mutation == "config_unknown":
        proposed["configuration"]["extra"] = True
    elif mutation == "negative_zero":
        proposed["step_zero"]["ram_mb"] = -0.0
    else:
        proposed["message_id"] = "A" * 32

    assert result_for(proposed)["rejection"]["error"]["code"] == expected


@pytest.mark.parametrize("field", ["game_id", "game_uid", "sub_game_number", "remote_role"])
def test_active_match_context_mismatch_rejects(field: str) -> None:
    proposed = offer("alpha", "beta", "active-game")
    context = offer_context(proposed)
    context[field] = 2 if field == "sub_game_number" else "other"

    assert result_for(proposed, context)["rejection"]["error"]["code"] == "IDENTITY_MISMATCH"


def test_expired_offer_and_wrong_running_commit_reject() -> None:
    proposed = offer("alpha", "beta", "expiry-game")
    expired = offer_context(proposed, now_ms=201)
    commit = offer_context(proposed)
    commit["remote_git_commit"] = "b" * 40

    assert result_for(proposed, expired)["rejection"]["error"]["code"] == "EXPIRED"
    assert result_for(proposed, commit)["rejection"]["error"]["code"] == "IDENTITY_MISMATCH"


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("base64", "MALFORMED"),
        ("whitespace", "CONFIG_MISMATCH"),
        ("root", "CONFIG_MISMATCH"),
    ],
)
def test_configuration_source_failures(mutation: str, expected: str) -> None:
    proposed = offer("alpha", "beta", "source-game")
    if mutation == "base64":
        proposed["configuration"]["game_source_b64"] = "***="
    elif mutation == "whitespace":
        raw = base64.b64decode(proposed["configuration"]["game_source_b64"])
        proposed["configuration"]["game_source_b64"] = base64.b64encode(b" " + raw).decode()
    else:
        proposed["configuration"]["game_source_b64"] = base64.b64encode(b"[]").decode()

    assert result_for(proposed)["rejection"]["error"]["code"] == expected


@pytest.mark.parametrize(
    "field",
    ["game_source_sha256", "rate_limits_source_sha256", "agreed_configuration_sha256"],
)
def test_each_declared_hash_is_independently_recomputed(field: str) -> None:
    proposed = offer("alpha", "beta", "hash-game")
    proposed["configuration"][field] = "f" * 64

    assert result_for(proposed)["rejection"]["error"]["code"] == "HASH_MISMATCH"


def test_multiple_faults_follow_profile_precedence() -> None:
    malformed = offer("alpha", "beta", "precedence-a")
    malformed["profile"] = "other"
    malformed["message_id"] = "bad"
    capability = offer("alpha", "beta", "precedence-b")
    capability["required_capabilities"] = []
    identity_context = offer_context(capability)
    identity_context["local_group_id"] = "other"
    hash_first = offer("alpha", "beta", "precedence-c")
    hash_first["configuration"]["game_source_sha256"] = "f" * 64

    assert result_for(malformed)["rejection"]["error"]["code"] == "MALFORMED"
    assert result_for(capability, identity_context)["rejection"]["error"]["code"] == (
        "CAPABILITY_MISMATCH"
    )
    assert result_for(
        hash_first, offer_context(hash_first, now_ms=201)
    )["rejection"]["error"]["code"] == "HASH_MISMATCH"


@pytest.mark.parametrize("participants", [["beta", "alpha"], ["alpha"], ["alpha", "beta", "x"]])
def test_agreed_between_requires_exact_sorted_pair(participants: list[str]) -> None:
    proposed = offer("alpha", "beta", "participants")
    rewrite_participants(proposed, participants)

    assert result_for(proposed)["rejection"]["error"]["code"] == "IDENTITY_MISMATCH"
