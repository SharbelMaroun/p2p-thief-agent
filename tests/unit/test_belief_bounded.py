"""`M6-023`: belief memory is bounded across a long series — no history accumulation.

The Thief's whole perception state is the belief grid (fixed at the board size) and a scalar
trust; neither grows with the number of turns. So six sub-games of the step limit cannot
accumulate unbounded memory: every update returns a fresh `size × size` grid, never a growing
per-turn log.
"""

from p2p_thief_agent.perception.belief import uniform_belief
from p2p_thief_agent.perception.consume import consume_hint
from p2p_thief_agent.perception.trust import NEUTRAL_TRUST, update_trust

SERIES_STEPS = 6 * 35  # six sub-games of the negotiated step limit


def test_the_belief_stays_a_fixed_size_grid_over_a_whole_series() -> None:
    belief = uniform_belief(7, 7)
    for _ in range(SERIES_STEPS):
        belief = consume_hint(belief, "north", NEUTRAL_TRUST, 7, 7)
    assert len(belief) == 7 and all(len(row) == 7 for row in belief)
    # 49 cells regardless of how many updates ran: the grid is the entire state.
    assert sum(len(row) for row in belief) == 49


def test_trust_stays_a_single_scalar_across_a_series() -> None:
    trust, north, scent = NEUTRAL_TRUST, [[1.0, 0.0]], [[1.0, 0.0]]
    for _ in range(SERIES_STEPS):
        trust = update_trust(trust, north, scent)
    assert isinstance(trust, float) and 0.0 <= trust <= 1.0  # one number, not a history
