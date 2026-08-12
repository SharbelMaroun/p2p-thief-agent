"""Book (S)3.4 conditions 2 and 3, conceded truthfully (amireman interop, rules 21/22).

A barrier on our cell captures us; a barrier that leaves us no passable orthogonal
neighbour traps us. Both were silent gaps -- our Thief answered only claim
co-location -- until amireman's interop guide named them as their conditions (B) and
(C). The concession must also end OUR sub-game loop as a capture, or the opponent
records capture while we time out into technical_loss: rule 35's 0/0.
"""

from p2p_thief_agent.orchestration.thief_policy import make_decide


def incoming(step: int, **extra: object) -> dict:
    return {"step": step, "sender": "police", "hint": "x", "smell_grid": {},
            "commit": "0" * 64, "timestamp": f"t{step}", **extra}


def test_a_barrier_on_our_cell_is_conceded() -> None:
    decide = make_decide(start=(3, 3), threshold=35)
    message, _record = decide(incoming(1, barrier_placed=[3, 3]), 1)
    answer = message["claim_response"]
    assert answer["caught"] is True
    assert answer["claim"] == [3, 3]


def test_being_walled_in_is_conceded() -> None:
    """All four neighbours barriered: condition (C), regardless of any claim."""
    decide = make_decide(start=(0, 0), threshold=35)
    decide(incoming(1, barrier_placed=[0, 1]), 1)
    message, _record = decide(incoming(2, barrier_placed=[1, 0]), 2)
    answer = message["claim_response"]
    assert answer["caught"] is True


def test_an_ordinary_turn_concedes_nothing() -> None:
    decide = make_decide(start=(3, 3), threshold=35)
    message, _record = decide(incoming(1), 1)
    assert message["claim_response"] is None


def test_a_missed_claim_is_answered_false() -> None:
    decide = make_decide(start=(3, 3), threshold=35)
    message, _record = decide(incoming(1, capture_claim=[0, 0]), 1)
    answer = message["claim_response"]
    assert answer == {"claim": [0, 0], "caught": False}
