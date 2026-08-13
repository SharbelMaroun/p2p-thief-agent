"""A missed claim under the amireman profile is the pursuer's true position.

Their Cop claims its OWN post-move cell every turn (interop guide S5). The first
smoke's Thief game was lost by discarding exactly that intel: our belief wandered,
and we walked into a cop whose position we had been told nine times. Gated by
``claim_reveals_cop`` because the default profile's claim names the cell the Cop
believes WE are on — collapsing belief there would chase our own shadow.
"""

from p2p_thief_agent.orchestration.thief_policy import make_decide


def incoming(step: int, **extra: object) -> dict:
    return {"step": step, "sender": "police", "hint": "x", "smell_grid": {},
            "commit": "0" * 64, "timestamp": f"t{step}", **extra}


def test_a_missed_claim_pins_the_belief_to_the_claimed_cell() -> None:
    decide = make_decide(start=(3, 3), threshold=35, claim_reveals_cop=True)
    decide(incoming(1, capture_claim=[0, 6]), 1)
    believed = decide.believed_cop_cell()
    assert [believed.row, believed.col] == [0, 6]


def test_without_the_flag_the_claim_is_not_position_intel() -> None:
    """Default profile: the claim names where they think WE are; belief must not move there."""
    decide = make_decide(start=(3, 3), cop_start=(0, 0), threshold=35)
    decide(incoming(1, capture_claim=[6, 6]), 1)
    believed = decide.believed_cop_cell()
    assert [believed.row, believed.col] != [6, 6]


def test_a_correct_claim_still_concedes_not_retargets() -> None:
    """Co-location is a capture even with the intel flag on."""
    decide = make_decide(start=(3, 3), threshold=35, claim_reveals_cop=True)
    message, _record = decide(incoming(1, capture_claim=[3, 3]), 1)
    assert message["claim_response"] == {"claim": [3, 3], "caught": True}


def test_the_known_pursuer_is_fled_not_approached() -> None:
    """With the cop's true cell known, the chosen move must not shrink the distance."""
    decide = make_decide(start=(3, 3), threshold=35, claim_reveals_cop=True)
    message, record = decide(incoming(1, capture_claim=[3, 1]), 1)
    row, col = record["payload"]["position"]
    assert abs(row - 3) + abs(col - 1) >= 2  # started 2 away; never step closer
