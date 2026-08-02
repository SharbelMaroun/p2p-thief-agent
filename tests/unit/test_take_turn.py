"""`M5-019`: `take_turn` -- the mailbox side of the autonomous play loop.

`drain` validates everything and returns verdicts; the play loop needs the
opposite shape -- the next *turn message* the peer accepted, so it can be fed to
`run_turn`. The three behaviours pinned here are the ones that would each silently
break an unattended match:

* a rejected turn must be **consumed**, or the poller re-rejects it forever and
  starves the real turn behind it;
* a second queued turn must be **left in place**, or a hostile (or merely eager)
  peer sending two at once costs us the next step;
* the other mailboxes must be drained, or a negotiate/audit/control message parked
  in front of a turn stalls the game.
"""

from p2p_thief_agent.adapters import PeerInboxes, take_turn
from p2p_thief_agent.peer import InboundPeer
from p2p_thief_agent.protocol.crypto import seal

AGREEMENT = {"terms": {"board_size": 7}, "nonce": "0" * 32, "signature": "b" * 64,
             "identity": {"group_id": "group-beta"}}
CONTROL = {"kind": "status", "sender": "police"}


def turn_msg(step: int = 1) -> dict:
    return {"step": step, "sender": "police", "hint": "near the park",
            "smell_grid": {"3,3": 0.9}, "commit": "a" * 64, "timestamp": "t"}


def audit_msg() -> dict:
    payload = {"step": 1, "move": "MOVE:N"}
    sealed = seal(payload)
    record = {"payload": payload, "nonce": sealed["nonce"], "commit": sealed["commit"]}
    return {"sender": "police", "records": [record], "result_claim": "survival"}


def test_an_empty_mailbox_yields_nothing_rather_than_blocking() -> None:
    """The waiting belongs to the poller; this source must always answer at once."""
    assert take_turn(PeerInboxes(), InboundPeer()) is None


def test_a_queued_turn_is_validated_and_returned() -> None:
    inboxes = PeerInboxes()
    inboxes.turns.put(turn_msg(1))
    assert take_turn(inboxes, InboundPeer()) == turn_msg(1)


def test_a_rejected_turn_is_consumed_so_it_cannot_be_re_rejected_forever() -> None:
    """Leaving it queued would starve every real turn behind it."""
    inboxes = PeerInboxes()
    inboxes.turns.put({"bad": "turn"})
    assert take_turn(inboxes, InboundPeer()) is None
    assert inboxes.turns.empty()


def test_a_rejected_turn_is_skipped_and_the_next_good_one_is_returned() -> None:
    inboxes = PeerInboxes()
    inboxes.turns.put({"bad": "turn"})
    inboxes.turns.put(turn_msg(1))
    assert take_turn(inboxes, InboundPeer()) == turn_msg(1)


def test_a_second_queued_turn_is_left_for_the_next_step() -> None:
    """Draining both would discard the next step instead of playing it."""
    peer = InboundPeer()
    inboxes = PeerInboxes()
    inboxes.turns.put(turn_msg(1))
    inboxes.turns.put(turn_msg(2))
    assert take_turn(inboxes, peer) == turn_msg(1)
    assert inboxes.turns.qsize() == 1
    assert take_turn(inboxes, peer) == turn_msg(2)


def test_the_other_mailboxes_are_drained_so_nothing_parks_in_front_of_a_turn() -> None:
    inboxes = PeerInboxes()
    inboxes.agreements.put(AGREEMENT)
    inboxes.controls.put(CONTROL)
    inboxes.audits.put(audit_msg())
    inboxes.turns.put(turn_msg(1))
    assert take_turn(inboxes, InboundPeer()) == turn_msg(1)
    assert inboxes.agreements.empty()
    assert inboxes.controls.empty()
    assert inboxes.audits.empty()


def test_only_a_turn_is_returned_even_when_other_mail_is_waiting() -> None:
    """Only a turn advances the loop; the rest are validated and recorded, not played."""
    inboxes = PeerInboxes()
    inboxes.agreements.put(AGREEMENT)
    assert take_turn(inboxes, InboundPeer()) is None
