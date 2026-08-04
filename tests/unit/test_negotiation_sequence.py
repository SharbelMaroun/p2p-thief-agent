"""`M5-019f`: negotiation is sequenced before the first move, autonomously.

No socket here — the sequencer is transport-neutral, so the whole handshake is driven
with an in-memory `send_offer`/`take_offer` pair and injected time. The live wire is
proven in `tests/integration/`.
"""

import pytest

from p2p_thief_agent.orchestration.negotiation import (
    NegotiationError,
    negotiate_match,
    run_autonomous_match,
)
from p2p_thief_agent.protocol.handshake import Handshake

# Terms that clear every Appendix F gate: FIXED scent/series values exact, MINIMUM
# board/steps/barriers at their floor, and every required term present.
TERMS = {
    "board_size": 7, "smell_grid_size": 5, "decay_per_step": 0.10, "emit_intensity": 0.9,
    "max_steps": 35, "barriers_max": 14, "thief_start": [0, 0], "cop_start": [6, 6],
    "num_games": 6,
}


def opponent_offer(terms: dict) -> dict:
    return Handshake(dict(terms), identity={"group_id": "opp"}).signed()


def returns_once(offer: dict):
    box = [offer]
    return lambda: box.pop() if box else None


def counting_clock():
    ticks = [0.0]

    def clock() -> float:
        ticks[0] += 1.0
        return ticks[0]

    return clock


def test_it_sends_our_offer_then_agrees_on_the_opponents() -> None:
    sent: list[dict] = []
    mine = Handshake(dict(TERMS), identity={"group_id": "us"})
    agreed = negotiate_match(
        handshake=mine, my_terms=TERMS,
        send_offer=lambda offer: sent.append(dict(offer)),
        take_offer=returns_once(opponent_offer(TERMS)),
        clock=lambda: 0.0, sleep=lambda _s: None, timeout=5.0,
    )
    assert sent and sent[0]["terms"] == TERMS  # our signed offer went out first
    assert agreed.terms == TERMS
    assert agreed.peer_identity == {"group_id": "opp"}


def test_a_weakened_minimum_is_refused_by_name() -> None:
    weak = {**TERMS, "max_steps": 30}  # below the MINIMUM of 35
    with pytest.raises(NegotiationError, match="max_steps"):
        negotiate_match(
            handshake=Handshake(dict(TERMS)), my_terms=TERMS,
            send_offer=lambda _o: None, take_offer=returns_once(opponent_offer(weak)),
            clock=lambda: 0.0, sleep=lambda _s: None, timeout=5.0,
        )


def test_silence_before_the_deadline_is_a_refusal_not_a_hang() -> None:
    beats: list[int] = []
    with pytest.raises(NegotiationError, match="no signed offer"):
        negotiate_match(
            handshake=Handshake(dict(TERMS)), my_terms=TERMS,
            send_offer=lambda _o: None, take_offer=lambda: None,
            clock=counting_clock(), sleep=lambda _s: None, timeout=3.0,
            heartbeat=lambda: beats.append(1),
        )
    assert beats  # the wait pulsed the watchdog rather than freezing silently


def test_play_opens_only_after_agreement_bounded_by_the_negotiated_horizon() -> None:
    played: list[int] = []
    agreed, outcome = run_autonomous_match(
        handshake=Handshake(dict(TERMS)), my_terms=TERMS,
        send_offer=lambda _o: None, take_offer=returns_once(opponent_offer(TERMS)),
        play_sub_game=lambda horizon: played.append(horizon) or "survival",
        clock=lambda: 0.0, sleep=lambda _s: None, timeout=5.0,
    )
    assert agreed.terms == TERMS
    assert played == [35]  # the sub-game ran to the agreed max_steps, not a local default
    assert outcome == "survival"
