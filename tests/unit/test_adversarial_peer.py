"""`M5-011`: the runtime survives a hostile or broken opponent.

Every hostile behaviour class the ledger names already has a guard somewhere in the
runtime — the phase machine, the inbound idempotency check, the strict wire decoder,
or the sub-game's terminal exits. This module is the single proof that gathers them,
so a regression in any one guard fails here under an explicit adversarial name rather
than only in the subsystem that happens to own it. Nothing new is built: each guard
is exercised against its real code path (`AE-005`, `AE-007`, `AE-019`).
"""

import pytest

from p2p_thief_agent.adapters.fastmcp_client import TransportError
from p2p_thief_agent.orchestration.phases import Phase, PhaseError, PhaseMachine
from p2p_thief_agent.peer import InboundPeer
from p2p_thief_agent.protocol.wire import WireError
from p2p_thief_agent.state.scoring import Outcome
from tests.unit.test_sub_game import Opponent, cop_turn, play


def test_a_peer_that_never_responds_is_a_technical_loss_not_a_hang() -> None:
    """`M5-011a`: silence is not patience — the deadline forces a terminal outcome.

    The opener seals step 1 and one reply lands, then the peer goes quiet; the loop
    reaches `TECHNICAL_LOSS` in a bounded number of steps instead of blocking. The
    watchdog's freeze path is proven independently in `test_watchdog.py`.
    """
    result = play(Opponent(cop_turn(1)), threshold=5)
    assert result.outcome is Outcome.TECHNICAL_LOSS
    assert result.steps < 5
    assert "did not send a turn" in result.reason


def test_a_peer_that_responds_out_of_order_is_rejected_by_the_state_machine() -> None:
    """`M5-011b`: the declared machine refuses any transition outside its table.

    A peer that tried to jump straight to reveal without first committing is exactly
    an undeclared ``WAITING_FOR_OPPONENT -> AWAITING_REVEAL`` edge, which raises
    rather than silently advancing (`AE-005`).
    """
    machine = PhaseMachine()
    with pytest.raises(PhaseError, match="illegal transition"):
        machine.to(Phase.AWAITING_REVEAL)
    assert machine.current is Phase.WAITING_FOR_OPPONENT


def test_a_replayed_turn_is_rejected_by_the_idempotency_guard() -> None:
    """`M5-011c`: a duplicated ``(step, sender)`` is refused by name, never re-applied."""
    peer = InboundPeer()
    turn = cop_turn(4)
    assert peer.receive_turn(turn) == {"ok": True}
    with pytest.raises(WireError, match="replayed turn for step 4"):
        peer.receive_turn(turn)
    assert len(peer.turns) == 1


def test_oversized_or_malformed_input_is_rejected_before_domain_code_runs() -> None:
    """`M5-011d`: the wire decoder rejects junk before the game ever sees it.

    An injected extra field — here carrying a 10 000-character payload a hostile
    peer might use to probe for a buffer — is refused as an unknown field, and a
    turn missing required fields is refused as incomplete. Neither reaches domain
    code, because `TurnMessage.from_dict` runs first.
    """
    peer = InboundPeer()
    with pytest.raises(WireError, match="unknown fields"):
        peer.receive_turn({**cop_turn(1), "inject": "x" * 10_000})
    with pytest.raises(WireError, match="missing fields"):
        peer.receive_turn({"step": 1, "sender": "police"})
    assert peer.turns == []


class DropsAtAudit:
    """Accepts turns but is gone by audit time — a peer that leaves mid-audit."""

    def receive_turn(self, message: dict) -> dict:
        return {"ok": True}

    def submit_audit(self, payload: dict) -> dict:
        raise TransportError("peer disconnected before the audit")


def test_a_peer_that_disconnects_mid_audit_still_records_the_outcome() -> None:
    """`M5-011e`: the audit is still decided and revealed even if it cannot be sent.

    A reveal that cannot reach a departed peer is still built and returned, so this
    side's proof stands (`AE-019`). The sub-game reaches its outcome rather than
    hanging on an undeliverable audit.
    """
    result = play(Opponent(), threshold=1, transport=DropsAtAudit())
    assert result.outcome is Outcome.SURVIVAL
    assert result.audit is not None
    assert len(result.audit["records"]) == 1
