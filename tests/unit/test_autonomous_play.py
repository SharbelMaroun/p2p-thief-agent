"""`M5-019`: a whole sub-game played from the mailbox, with nothing fed in by hand.

Every earlier sub-game test hands `run_sub_game_over_wire` a scripted `receive`.
That proves the loop, but it quietly assumes the one piece that did not exist:
something to turn the passive mailbox into a turn source. Until this existed a
peer could not play unattended -- which is why the two-machine game (`M5-005c`)
was blocked on code and not only on hardware.

Here the opponent is reachable only through the real parts: the peer sends via the
transport, the Cop's reply lands in this peer's own `PeerInboxes`, and the polling
receiver has to find it there. Mailbox -> poller -> `run_turn` -> transport ->
mailbox, closed.

**The Thief opens.** The book gives it the first move of every cycle, so step 1
sends without waiting and nothing is seeded ahead of it. From step 2 on, every
turn depends on the mailbox.
"""

from p2p_thief_agent.adapters import PeerInboxes, take_turn
from p2p_thief_agent.orchestration.phases import PhaseMachine
from p2p_thief_agent.orchestration.polling import turn_receiver
from p2p_thief_agent.orchestration.sub_game import run_sub_game_over_wire
from p2p_thief_agent.peer import InboundPeer
from p2p_thief_agent.state.scoring import Outcome
from tests.unit.test_polling import FakeClock
from tests.unit.test_turn_loop import decide


def cop_turn(step: int, **extra: object) -> dict:
    return {"step": step, "sender": "police", "hint": "closing in",
            "smell_grid": {"0,0": 0.9}, "commit": "a" * 64,
            "timestamp": f"t{step}", **extra}


class MailboxOpponent:
    """A Cop that answers into *our* inboxes, the way a real peer would.

    It is a `PeerTransport`: we call `receive_turn` to send, and its answer arrives
    asynchronously in the mailbox rather than as a return value -- which is the
    whole shape of the wire profile, where the tool only acknowledges.
    """

    def __init__(self, inboxes: PeerInboxes, *replies: dict) -> None:
        self.inboxes = inboxes
        self.replies = list(replies)
        self.sent: list[dict] = []
        self.audits: list[dict] = []

    def receive_turn(self, message: dict) -> dict:
        self.sent.append(message)
        if self.replies:
            self.inboxes.turns.put(self.replies.pop(0))
        return {"ok": True}

    def submit_audit(self, payload: dict) -> dict:
        self.audits.append(payload)
        return {"ok": True}


def play(*replies: dict, threshold: int = 5, timeout: float = 30.0,
         answer=lambda _cell: False):
    """Play a sub-game whose only turn source is the mailbox."""
    inboxes = PeerInboxes()
    peer = InboundPeer()
    opponent = MailboxOpponent(inboxes, *replies)
    clock = FakeClock()
    result = run_sub_game_over_wire(
        machine=PhaseMachine(),
        transport=opponent,
        receive=turn_receiver(
            lambda: take_turn(inboxes, peer),
            clock=clock.time,
            sleep=clock.sleep,
            timeout=timeout,
            poll_interval=0.5,
        ),
        decide=decide,
        answer_claim=answer,
        survival_threshold=threshold,
    )
    return result, opponent, clock


def test_a_whole_sub_game_plays_with_no_message_fed_in_by_hand() -> None:
    """The gap `M5-005c` named: a peer that drives itself, not one driven by a test."""
    result, opponent, _ = play(*(cop_turn(s) for s in range(1, 5)), threshold=5)
    assert result.outcome is Outcome.SURVIVAL
    assert result.steps == 5
    assert len(opponent.sent) == 5


def test_the_opponent_reply_really_travels_through_the_mailbox() -> None:
    """If the poller were bypassed the peer would stall at step 2, not reach step 5."""
    _, opponent, _ = play(*(cop_turn(s) for s in range(1, 5)), threshold=5)
    assert [m["step"] for m in opponent.sent] == [1, 2, 3, 4, 5]


def test_a_correct_capture_claim_still_ends_it_when_driven_from_the_mailbox() -> None:
    """The Thief concedes on its own knowledge; the mailbox only carried the claim."""
    result, _, _ = play(
        cop_turn(1, capture_claim=[3, 3]),
        threshold=5,
        answer=lambda _cell: True,
    )
    assert result.outcome is Outcome.CAPTURE


def test_a_silent_opponent_ends_the_game_instead_of_hanging_the_poller() -> None:
    """Rule 6, end to end: the wait is bounded, so silence decides rather than blocks."""
    result, opponent, clock = play(threshold=5, timeout=2.0)
    assert result.outcome is Outcome.TECHNICAL_LOSS
    assert len(opponent.sent) == 1  # the Thief opened, then nothing came back
    assert clock.now >= 2.0  # it really waited its budget before giving up


def test_the_audit_goes_out_even_when_this_peer_is_taking_the_loss() -> None:
    """A withheld reveal cannot be checked, and the point is that the *Cop* recomputes."""
    result, opponent, _ = play(threshold=5, timeout=1.0)
    assert result.outcome is Outcome.TECHNICAL_LOSS
    assert opponent.audits != []
