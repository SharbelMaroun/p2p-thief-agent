"""Exact walled escape solver: capture cases, escape sets, determinism (`M6-034`)."""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Action, Coordinate
from p2p_thief_agent.strategy.barrier_search import (
    escape_actions_walled,
    survives_walled,
)
from p2p_thief_agent.strategy.escape_search import survives as survives_mover
from p2p_thief_agent.strategy.pursuer_models import greedy_step
from p2p_thief_agent.strategy.waller_models import greedy_waller, interceptor_waller

BOARD = Board(size=7)


def test_a_wall_on_the_thiefs_cell_is_capture() -> None:
    """The Police adjacent to the Thief walls its cell on the first step (§3.4)."""
    cop, thief = Coordinate(5, 6), Coordinate(6, 6)  # (6,6) is an in-range wall candidate
    assert survives_walled(BOARD, greedy_waller, cop, thief, 1, frozenset(), 14, {}) is False


def test_far_apart_survives_a_short_window() -> None:
    """Opposite corners, only a few steps: no wall or move can close the gap."""
    cop, thief = Coordinate(0, 0), Coordinate(6, 6)
    assert survives_walled(BOARD, interceptor_waller, cop, thief, 4, frozenset(), 14, {}) is True


def test_zero_quota_matches_the_pure_mover_solver() -> None:
    """With no quota the waller can never wall, so it is exactly its underlying mover — and
    the walled solver must agree with the proven `escape_search.survives`, same step order."""
    for cop, thief in ((Coordinate(2, 2), Coordinate(5, 5)),
                       (Coordinate(0, 0), Coordinate(6, 6)),
                       (Coordinate(3, 0), Coordinate(3, 6))):
        walled = survives_walled(BOARD, greedy_waller, cop, thief, 10, frozenset(), 0, {})
        mover = survives_mover(BOARD, greedy_step, cop, thief, 10, frozenset(), {})
        assert walled == mover


def test_escape_actions_exclude_stepping_onto_the_pursuer() -> None:
    """At the decision point the pursuer has already acted; a step onto it is never safe."""
    cop, thief = Coordinate(5, 6), Coordinate(6, 6)
    actions = escape_actions_walled(BOARD, greedy_waller, thief, cop, 0, frozenset(), 14, {})
    assert Action.NORTH not in actions  # NORTH -> (5,6) is the pursuer
    assert set(actions) == {Action.STAY, Action.WEST}


def test_escape_actions_are_all_legal_and_ordered() -> None:
    cop, thief = Coordinate(0, 0), Coordinate(3, 3)
    actions = escape_actions_walled(BOARD, interceptor_waller, thief, cop, 3, frozenset(), 14, {})
    order = list(Action)
    assert list(actions) == sorted(actions, key=order.index)
    assert all(isinstance(a, Action) for a in actions)


def test_negative_steps_after_is_rejected() -> None:
    cop, thief = Coordinate(0, 0), Coordinate(6, 6)
    try:
        escape_actions_walled(BOARD, greedy_waller, thief, cop, -1, frozenset(), 14, {})
    except ValueError:
        return
    raise AssertionError("escape_actions_walled must reject a negative horizon")


def test_solver_is_deterministic() -> None:
    cop, thief = Coordinate(0, 0), Coordinate(6, 6)
    first = survives_walled(BOARD, interceptor_waller, cop, thief, 8, frozenset(), 14, {})
    second = survives_walled(BOARD, interceptor_waller, cop, thief, 8, frozenset(), 14, {})
    assert first == second


def test_memo_does_not_change_the_answer() -> None:
    """A shared memo across calls must not corrupt a later query on the same board."""
    memo: dict = {}
    cop, thief = Coordinate(0, 0), Coordinate(6, 6)
    a = survives_walled(BOARD, greedy_waller, cop, thief, 8, frozenset(), 14, memo)
    b = survives_walled(BOARD, greedy_waller, cop, thief, 8, frozenset(), 14, {})
    assert a == b


def test_existing_barrier_can_seal_a_trap() -> None:
    """A Thief boxed by prior barriers against the edge, Police adjacent, cannot survive."""
    thief = Coordinate(6, 6)
    barriers = frozenset({Coordinate(5, 6), Coordinate(6, 5)})  # only escapes were these
    # Thief already trapped: both cardinal neighbours blocked, the rest off-board.
    assert survives_walled(BOARD, greedy_waller, Coordinate(0, 0), thief, 3, barriers, 14, {}) is False
