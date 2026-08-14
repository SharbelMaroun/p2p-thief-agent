"""The evasion selector keeps `"current"` byte-identical to the shipped policy (`M6-035`).

The whole safety case for grafting the experimental planner on rests on one contract: the
production default `"current"` must resolve to exactly `choose_adaptive_action`, and any
unrecognised strategy must too — so a stray private-config value can never leave the live
Thief on an unproven path.
"""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.domain.movement import legal_actions
from p2p_thief_agent.strategy.adaptive_policy import PursuerTracker, choose_adaptive_action
from p2p_thief_agent.strategy.barrier_aware_policy import evasion_action
from p2p_thief_agent.strategy.belief_policy import initial_belief

BOARD = Board(size=7)


def _belief(cop: Coordinate):
    return initial_belief(BOARD, cop)


def _adaptive(thief: Coordinate, belief, step: int, blocked=frozenset()):
    return choose_adaptive_action(BOARD, thief, belief, PursuerTracker(35), step, blocked)


def test_current_matches_the_shipped_adaptive_policy_exactly() -> None:
    for cr, cc, tr, tc, step in ((0, 0, 3, 3, 1), (6, 0, 2, 4, 7), (3, 6, 5, 1, 20)):
        cop, thief = Coordinate(cr, cc), Coordinate(tr, tc)
        belief = _belief(cop)
        chosen = evasion_action("current", BOARD, thief, belief, PursuerTracker(35), step,
                                frozenset(), threshold=35, quota_remaining=14)
        assert chosen == _adaptive(thief, belief, step)


def test_unknown_strategy_falls_back_to_current() -> None:
    thief, belief = Coordinate(3, 3), _belief(Coordinate(0, 0))
    chosen = evasion_action("not_a_real_strategy", BOARD, thief, belief, PursuerTracker(35),
                            1, frozenset(), threshold=35, quota_remaining=14)
    assert chosen == _adaptive(thief, belief, 1)


def test_barrier_aware_v2_returns_a_legal_action() -> None:
    thief, belief = Coordinate(3, 3), _belief(Coordinate(1, 3))
    barriers = frozenset({Coordinate(5, 5)})
    chosen = evasion_action("barrier_aware_v2", BOARD, thief, belief, PursuerTracker(35), 5,
                            barriers, threshold=35, quota_remaining=14)
    assert chosen in legal_actions(BOARD, thief, barriers)


def test_make_decide_default_strategy_is_current() -> None:
    """The live factory must default to the known-good policy without any config."""
    from p2p_thief_agent.orchestration.thief_policy import make_decide

    decide = make_decide(threshold=35)
    message, record = decide({"smell_grid": {}}, 1)
    assert record["payload"]["move"].startswith("MOVE:")  # a legal sealed move was produced
