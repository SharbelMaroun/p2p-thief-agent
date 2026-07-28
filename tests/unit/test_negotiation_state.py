"""Active-context, mirroring, replay, and readiness negotiation tests."""

from copy import deepcopy

import pytest

from p2p_thief_agent.protocol.negotiation_state import NegotiationState
from p2p_thief_agent.protocol.profile import ConformanceError
from tests.unit.negotiation_state_fixtures import (
    LOCAL,
    REMOTE,
    incoming,
    offer,
    outgoing,
    state,
)


def _assert_code(context: NegotiationState, candidate: dict, code: str) -> None:
    with pytest.raises(ConformanceError) as caught:
        context.accept(candidate, now_ms=150)
    assert caught.value.code == code


def test_ready_requires_two_exact_mirrored_acceptances() -> None:
    """One direction stays BOOTSTRAP; the swapped mirror transitions to READY."""
    context = state()
    local_offer = outgoing()
    first = context.accept(local_offer, now_ms=150)

    assert not context.ready
    assert context.accept(deepcopy(local_offer), now_ms=150) == first
    second = context.accept(incoming(), now_ms=150)
    assert context.ready
    assert first["participants"][0] == {"group_id": LOCAL, "role": "police"}
    assert second["participants"][0] == {"group_id": REMOTE, "role": "thief"}


@pytest.mark.parametrize(
    ("field", "bad"),
    [
        ("game_id", "another-match"),
        ("game_uid", "another-uid"),
        ("sub_game_number", 2),
    ],
)
def test_offer_must_match_active_game_context(field: str, bad: object) -> None:
    """Self-consistent offers cannot select a different active match identity."""
    context = state()
    candidate = outgoing()
    candidate[field] = bad
    if field == "sub_game_number":
        candidate["step_zero"][field] = bad
    _assert_code(context, candidate, "IDENTITY_MISMATCH")


def test_offer_must_match_active_participants_roles_and_configuration() -> None:
    """Valid alternate identities, roles, or terms cannot replace active context."""
    context = state()
    other_game = {"agreed_between": ["groupOther", REMOTE], "board_size": 7}
    other = offer("groupOther", "police", REMOTE, "thief", message="3", game=other_game)
    _assert_code(context, other, "IDENTITY_MISMATCH")
    wrong_roles = offer(LOCAL, "thief", REMOTE, "police", message="4")
    _assert_code(context, wrong_roles, "IDENTITY_MISMATCH")
    changed = outgoing(game={"agreed_between": [LOCAL, REMOTE], "board_size": 8})
    _assert_code(context, changed, "CONFIG_MISMATCH")


def test_offer_idempotency_conflict_and_direction_replay() -> None:
    """Exact retry is cached; changed reuse conflicts; a new ID cannot replay a side."""
    context = state()
    original = outgoing()
    context.accept(original, now_ms=150)
    changed = deepcopy(original)
    changed["step_zero"]["os"] = "changed"
    _assert_code(context, changed, "IDEMPOTENCY_CONFLICT")
    replay = deepcopy(original)
    replay["message_id"] = "f" * 32
    _assert_code(context, replay, "REPLAYED_MESSAGE")
    assert not context.ready


def test_rejection_is_cached_and_changed_retry_conflicts() -> None:
    """A validly keyed first rejection remains the exact idempotent result."""
    context = state()
    rejected = outgoing()
    rejected["game_id"] = "another-match"

    _assert_code(context, rejected, "IDENTITY_MISMATCH")
    _assert_code(context, deepcopy(rejected), "IDENTITY_MISMATCH")
    corrected = deepcopy(rejected)
    corrected["game_id"] = "match-1"
    _assert_code(context, corrected, "IDEMPOTENCY_CONFLICT")


@pytest.mark.parametrize("change", ["negotiation", "capabilities"])
def test_mirror_must_share_negotiation_and_capabilities(change: str) -> None:
    """The opposite direction cannot silently start a different negotiation."""
    context = state()
    context.accept(outgoing(), now_ms=150)
    candidate = incoming(negotiation="b" * 32) if change == "negotiation" else incoming(optional=())
    _assert_code(context, candidate, "OUT_OF_ORDER")
    assert not context.ready


def test_idempotency_key_includes_sender_identity() -> None:
    """Both directions may independently use the same message ID."""
    context = state()
    context.accept(outgoing(), now_ms=150)
    mirror = incoming()
    mirror["message_id"] = "1" * 32

    context.accept(mirror, now_ms=150)
    assert context.ready


@pytest.mark.parametrize(
    "changes",
    [{"sub_game_number": 7}, {"remote_group_id": LOCAL}, {"remote_role": []}],
)
def test_active_context_rejects_invalid_identity(changes: dict) -> None:
    """Invalid active sub-game, participants, and role types fail closed."""
    with pytest.raises(ConformanceError):
        state(**changes)
