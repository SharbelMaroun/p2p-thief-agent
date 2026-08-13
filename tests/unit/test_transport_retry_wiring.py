"""A transient transport fault must not end a match (`M5-010`, wired 2026-08-09).

`orchestration/delivery.deliver` encoded the right asymmetry from the start — retry a
carrier fault, never retry a rejection — and had **no production call site**. Both live
sends went out as one bare attempt, so a single tunnel 502 or timeout was fatal:

* mid-match, `turn_loop._deliver` ended the sub-game 0/0 on the first `TransportError`;
* pre-match, `negotiate_match`'s offer send let a raw `TransportError` escape through
  `serve_match` entirely -- the shape `docs/PROMPT_LOG.md` records for the first real
  match attempt ("our offer could not be delivered: negotiate failed in transport:
  Server error '502 Bad Gateway'").

These tests pin both wirings against regressing to a single attempt. They assert on
*attempt counts* rather than on wall-clock behaviour: time and sleep are injected, so a
retry is proven by counting, never by waiting.
"""

import json
import queue
from pathlib import Path

import pytest

from p2p_thief_agent.adapters.fastmcp_client import PeerRejectionError, TransportError
from p2p_thief_agent.adapters.negotiated import NegotiatedServeError, negotiated_agreement
from p2p_thief_agent.orchestration.delivery import retrying_deliver
from p2p_thief_agent.orchestration.phases import PhaseMachine
from p2p_thief_agent.orchestration.turn_loop import TurnLoopError, run_turn

ROOT = Path(__file__).resolve().parents[2]
# The real signed limits both peers read: 3 retries after the first try, 5s backoff.
MATCH = {"network_and_league": {"response_timeout_sec": 30},
         "rate_limiter_gatekeeper": {"retry_backoff_sec": 5, "max_retries": 3}}


class FlakyTransport:
    """A peer whose first ``fail_times`` sends fail with a carrier fault."""

    def __init__(self, fail_times: int, error: Exception | None = None) -> None:
        self.fail_times = fail_times
        self.attempts = 0
        self.error = error or TransportError("502 Bad Gateway")

    def receive_turn(self, message: dict) -> dict:
        self.attempts += 1
        if self.attempts <= self.fail_times:
            raise self.error
        return {"ok": True}


def decide(_incoming: dict | None, step: int) -> tuple[dict, dict]:
    return ({"step": step}, {"payload": {"step": step}, "nonce": "n", "commit": "c"})


def play_one_turn(transport: object, slept: list) -> None:
    run_turn(1, machine=PhaseMachine(), transport=transport, receive=lambda: {"x": 1},
             decide=decide, records=[], opens=True,
             deliver=retrying_deliver(MATCH, slept.append))


def test_a_transient_transport_fault_mid_match_is_retried_not_surrendered_to() -> None:
    """The regression that matters: two 502s in a row used to end the sub-game 0/0."""
    transport, slept = FlakyTransport(fail_times=2), []
    play_one_turn(transport, slept)
    assert transport.attempts == 3, "the send must be retried, not attempted once"
    assert slept == [5, 5], "each retry waits the agreed backoff"


def test_a_persistently_unreachable_peer_still_terminates_within_the_agreed_budget() -> None:
    """Retry must be bounded: rules 6/7 permit retry-then-declare, never retry forever."""
    transport, slept = FlakyTransport(fail_times=99), []
    with pytest.raises(TurnLoopError, match="sealed but not delivered"):
        play_one_turn(transport, slept)
    assert transport.attempts == 4, "first try plus the three agreed retries, then stop"


def test_a_rejection_is_never_retried() -> None:
    """`M5-010a`: a rejection is a decided outcome. Retrying it would re-litigate a loss."""
    transport, slept = FlakyTransport(fail_times=99, error=PeerRejectionError("declined")), []
    with pytest.raises(TurnLoopError, match="sealed but not delivered"):
        play_one_turn(transport, slept)
    assert transport.attempts == 1, "a refusal must propagate on the first occurrence"


class FlakyClient:
    """A negotiate endpoint whose first ``fail_times`` calls fail with a carrier fault."""

    def __init__(self, fail_times: int) -> None:
        self.fail_times = fail_times
        self.attempts = 0

    def negotiate(self, message: dict) -> dict:
        self.attempts += 1
        if self.attempts <= self.fail_times:
            raise TransportError("negotiate failed in transport: Server error '502 Bad Gateway'")
        return {"ok": True}


class Inboxes:
    def __init__(self) -> None:
        self.agreements: queue.Queue = queue.Queue()


def negotiate(client: object) -> None:
    game_config = json.loads((ROOT / "config" / "match_amireman.json")
                             .read_text(encoding="utf-8"))
    identity = {"group_id": "sharNamr", "group_name": "sharNamr", "members": ["a"],
                "repos": {"cop": "https://x", "thief": "https://y"}, "mcp_servers": {},
                "llm_model": "template", "hardware_spec": {}}
    negotiated_agreement(client=client, inboxes=Inboxes(), game_config=game_config,
                         identity=identity, fallback_timeout=0.01, sleep=lambda _s: None)


def test_a_transient_fault_on_the_offer_send_is_retried() -> None:
    """The pre-match half: one blip on the offer used to refuse the whole match."""
    client = FlakyClient(fail_times=2)
    # No opponent offer ever arrives, so this still ends in a refusal -- but the point
    # is *where*: past the send, at the deadline, having actually delivered our offer.
    with pytest.raises(NegotiatedServeError, match="no signed offer"):
        negotiate(client)
    assert client.attempts == 3, "the offer send must be retried, not attempted once"


def test_an_undeliverable_offer_surfaces_as_a_refusal_not_a_raw_transport_error() -> None:
    """A raw `TransportError` escaping `serve_match` is an unhandled crash to the operator;
    a refusal is a decision the CLI can report. This is what the first real match hit."""
    client = FlakyClient(fail_times=99)
    with pytest.raises(NegotiatedServeError, match="could not be delivered"):
        negotiate(client)
    assert client.attempts == 4, "first try plus the three agreed retries, then stop"
