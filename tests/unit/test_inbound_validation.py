"""`M8-004a`: malformed peer input cannot reach domain code.

`:12/50` states it in four words — **"never trust an unverified move"** — and rule 33 makes
the same point about reports: an invalid structure "will be rejected; score 0 in
processing".

**This repository validates differently from the companion**, so this is written against
what it actually does rather than mirrored. The companion checks JSON Schema files; here
`protocol/wire.py` uses dataclasses with explicit field checks and an `_known_only` filter.
That difference is load-bearing for the last test in this file: a schema can only *reject*
an unexpected member, while `_known_only` **drops** it — so an extra field never reaches a
constructor at all, which is a stronger guarantee and worth pinning as such.

**Why "cannot reach" rather than "is rejected".** A refusal that lands after the value has
touched a board, a ledger or a belief has already changed state, and rule 5 makes an
illegal state transition "a logical error leading to loss".
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.protocol.wire import (
    CONTROL_KINDS,
    ROLES,
    AuditPayload,
    ControlMessage,
    TurnMessage,
    WireError,
)

TURN = {"step": 1, "sender": "thief", "hint": "slipping past the market",
        "smell_grid": {"0,0": 0.9}, "commit": "a" * 64,
        "timestamp": "2026-08-07T10:00:00Z"}
CONTROL = {"kind": "status", "sender": "thief"}
REQUIRED_TURN = ("step", "sender", "hint", "smell_grid", "commit", "timestamp")


# --- the well-formed baseline, so the negatives are not vacuous --------------------------


def test_a_well_formed_turn_and_control_are_accepted() -> None:
    """A validator that refused everything would pass every negative below while making
    the agent unable to play at all."""
    assert TurnMessage.from_dict(TURN).step == 1
    assert ControlMessage.from_dict(CONTROL).kind == "status"


# --- M8-004a: the whole required-field surface -------------------------------------------


@pytest.mark.parametrize("field", REQUIRED_TURN)
def test_removing_any_required_turn_field_is_refused(field: str) -> None:
    """One parameter per field, so a failure names the field rather than the loop."""
    with pytest.raises(WireError):
        TurnMessage.from_dict({k: v for k, v in TURN.items() if k != field})


@pytest.mark.parametrize("shape", [None, [], "a string", 42, True])
def test_a_message_that_is_not_an_object_is_refused(shape: object) -> None:
    """The first thing a broken or hostile peer sends is often not an object at all."""
    with pytest.raises(WireError):
        TurnMessage.from_dict(shape)
    with pytest.raises(WireError):
        ControlMessage.from_dict(shape)
    with pytest.raises(WireError):
        AuditPayload.from_dict(shape)


@pytest.mark.parametrize("bad", ["cop", "COP", "Police", "", "thief ", "police\n", None, 1])
def test_a_sender_outside_the_wire_vocabulary_is_refused(bad: object) -> None:
    """The wire vocabulary is `thief`/`police`. `cop` is the companion repository's
    *internal* name and is not on the wire — a distinction the series rehearsal caught."""
    with pytest.raises(WireError):
        TurnMessage.from_dict({**TURN, "sender": bad})


def test_both_wire_roles_are_accepted() -> None:
    for role in ROLES:
        assert TurnMessage.from_dict({**TURN, "sender": role}).sender == role


@pytest.mark.parametrize("bad", ["start", "STATUS", "", None, 1])
def test_an_unknown_control_kind_is_refused(bad: object) -> None:
    with pytest.raises(WireError):
        ControlMessage.from_dict({**CONTROL, "kind": bad})


def test_every_declared_control_kind_is_accepted() -> None:
    """The allow-list must actually admit what it declares, or a legal control signal is
    refused mid-match and the phase machine stalls."""
    for kind in CONTROL_KINDS:
        assert ControlMessage.from_dict({**CONTROL, "kind": kind}).kind == kind


# --- "cannot reach domain code" ------------------------------------------------------------


def test_an_unexpected_member_is_dropped_rather_than_carried() -> None:
    """**The guarantee this repository has and the companion does not.** A JSON Schema can
    reject an unknown member; `_known_only` *removes* it, so it never reaches a constructor
    and cannot be read by anything downstream that later learns the name.

    The planted member is deliberately one that would matter — an objective coordinate.
    """
    smuggled = {**TURN, "true_thief_position": [3, 3], "opponent_seed": 99}
    message = TurnMessage.from_dict(smuggled)
    assert not hasattr(message, "true_thief_position")
    assert "true_thief_position" not in message.to_dict()
    assert "opponent_seed" not in message.to_dict()


def test_validation_refuses_before_any_domain_object_is_built() -> None:
    """A refusal after the value touched the domain has already changed state. The payload
    here would be catastrophic if used — an off-board cell and a negative step."""
    with pytest.raises(WireError):
        TurnMessage.from_dict({k: v for k, v in TURN.items() if k != "commit"}
                              | {"step": -1, "smell_grid": {"999,999": 5.0}})


def test_the_optional_fields_stay_optional() -> None:
    """`barrier_placed`, `capture_claim`, `claim_response` and `win_claim` are absent on an
    ordinary turn. Requiring them would refuse every normal message the opponent sends."""
    message = TurnMessage.from_dict(TURN)
    assert message.barrier_placed is None and message.capture_claim is None
    assert message.claim_response is None and message.win_claim is None
