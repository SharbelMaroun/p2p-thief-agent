"""Danger-gated barrier-aware policy: no mover regression, safe overrides (`M6-035`)."""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.domain.movement import legal_actions
from p2p_thief_agent.strategy.adaptive_policy import PursuerTracker, choose_adaptive_action
from p2p_thief_agent.strategy.barrier_aware_policy import (
    choose_barrier_aware_action,
    is_dangerous,
)
from p2p_thief_agent.strategy.barrier_search import escape_actions_walled
from p2p_thief_agent.strategy.belief_policy import believed_cop_cell, initial_belief
from p2p_thief_agent.strategy.waller_models import interceptor_waller

BOARD = Board(size=7)


def _belief(cop: Coordinate):
    return initial_belief(BOARD, cop)


def test_legacy_gate_when_shut_matches_the_shipped_policy() -> None:
    """With the legacy gate (`always=False`), a far mover is no danger: identical to adaptive.

    The default is `always=True` (plan every step); this pins the retained gated variant.
    """
    thief, belief = Coordinate(3, 3), _belief(Coordinate(0, 0))
    assert is_dangerous(BOARD, thief, Coordinate(0, 0), frozenset()) is False
    ours = choose_barrier_aware_action(
        BOARD, thief, belief, PursuerTracker(35), 1, (), quota_remaining=14, always=False)
    theirs = choose_adaptive_action(BOARD, thief, belief, PursuerTracker(35), 1, frozenset())
    assert ours == theirs


def test_default_is_always_on_and_stays_legal() -> None:
    """The shipped default plans every step; the result is still always a legal action."""
    thief, belief = Coordinate(3, 3), _belief(Coordinate(0, 0))
    action = choose_barrier_aware_action(
        BOARD, thief, belief, PursuerTracker(35), 1, (), quota_remaining=14, depth_cap=5)
    assert action in legal_actions(BOARD, thief, frozenset())


def test_a_disclosed_barrier_opens_the_gate() -> None:
    thief = Coordinate(3, 3)
    assert is_dangerous(BOARD, thief, Coordinate(0, 0), frozenset({Coordinate(5, 5)})) is True


def test_wall_pressure_opens_the_gate_without_a_barrier() -> None:
    """Cornered with the Police adjacent: a single wall could seal us, so plan."""
    thief, cop = Coordinate(6, 6), Coordinate(6, 5)
    assert is_dangerous(BOARD, thief, cop, frozenset()) is True


def test_when_active_the_move_survives_the_assumed_waller() -> None:
    """If any walled-safe action exists, the returned action is one of them."""
    thief, cop = Coordinate(3, 3), Coordinate(1, 3)
    belief = _belief(cop)
    barriers = frozenset({Coordinate(5, 5)})  # opens the gate
    action = choose_barrier_aware_action(
        BOARD, thief, belief, PursuerTracker(35), 5, barriers,
        quota_remaining=14, depth_cap=6)
    safe = escape_actions_walled(
        BOARD, interceptor_waller, thief, believed_cop_cell(belief, BOARD), 6,
        barriers, 14, {})
    if safe:
        assert action in safe


def test_result_is_always_legal_across_a_sweep() -> None:
    for cr, cc in ((0, 0), (3, 3), (6, 0)):
        for tr, tc in ((3, 3), (2, 4), (5, 5)):
            cop, thief = Coordinate(cr, cc), Coordinate(tr, tc)
            if cop == thief:
                continue
            belief = _belief(cop)
            barriers = frozenset({Coordinate(4, 4)})
            action = choose_barrier_aware_action(
                BOARD, thief, belief, PursuerTracker(35), 3, barriers,
                quota_remaining=14, depth_cap=5)
            assert action in legal_actions(BOARD, thief, barriers)


def test_policy_is_deterministic() -> None:
    thief, cop = Coordinate(4, 4), Coordinate(2, 4)
    belief, barriers = _belief(cop), frozenset({Coordinate(4, 2)})
    first = choose_barrier_aware_action(
        BOARD, thief, belief, PursuerTracker(35), 6, barriers, quota_remaining=14, depth_cap=5)
    second = choose_barrier_aware_action(
        BOARD, thief, belief, PursuerTracker(35), 6, barriers, quota_remaining=14, depth_cap=5)
    assert first == second


def test_stats_record_activation() -> None:
    thief, cop = Coordinate(3, 3), Coordinate(1, 3)
    stats: dict = {}
    choose_barrier_aware_action(
        BOARD, thief, _belief(cop), PursuerTracker(35), 4, frozenset({Coordinate(5, 5)}),
        quota_remaining=14, depth_cap=5, stats=stats)
    assert stats.get("activations", 0) >= 1
    assert stats.get("decisions", 0) == 1


def test_a_hopeless_state_falls_back_without_raising() -> None:
    """No guaranteed escape must degrade to the shipped pick, never raise (fail-safe)."""
    thief = Coordinate(6, 6)
    barriers = frozenset({Coordinate(5, 6)})  # one exit left, Police adjacent on the other
    cop = Coordinate(6, 5)
    action = choose_barrier_aware_action(
        BOARD, thief, _belief(cop), PursuerTracker(35), 30, barriers,
        quota_remaining=14, depth_cap=6)
    assert action in legal_actions(BOARD, thief, barriers)
