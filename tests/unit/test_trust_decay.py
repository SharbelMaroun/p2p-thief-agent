"""`M6-027`: how trust falls on repeated lies and recovers on truthful hints.

The policy is linear and symmetric: a full contradiction moves trust by `rate` (default 0.2)
toward 0, a full corroboration by `rate` toward 1, both clipped — so about `1/rate` ≈ 5 hints
swing it end to end, and partial agreement moves it proportionally. It recovers: a peer that
lied can rebuild trust by telling the truth, so one bad hint is not a life sentence.
"""

from p2p_thief_agent.perception.trust import NEUTRAL_TRUST, update_trust

TOP_LEFT = [[1.0, 0.0], [0.0, 0.0]]
BOTTOM_RIGHT = [[0.0, 0.0], [0.0, 1.0]]


def test_repeated_lies_drive_trust_to_the_floor_monotonically() -> None:
    trust, seen = NEUTRAL_TRUST, [NEUTRAL_TRUST]
    for _ in range(6):  # the hint points bottom-right while scent is top-left: a lie each time
        trust = update_trust(trust, BOTTOM_RIGHT, TOP_LEFT)
        seen.append(trust)
    assert seen[-1] == 0.0
    assert all(earlier >= later for earlier, later in zip(seen, seen[1:], strict=False))


def test_truthful_hints_recover_trust_to_the_ceiling() -> None:
    trust = 0.0
    for _ in range(6):  # the hint now agrees with the scent: corroboration each time
        trust = update_trust(trust, TOP_LEFT, TOP_LEFT)
    assert trust == 1.0
