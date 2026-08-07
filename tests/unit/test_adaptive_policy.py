"""The sixth attempt's machinery: correct, legal, history-deterministic (`M6-030`).

The policy is measured worse than shipped under the real estimator and is not wired
into the live loop; these tests pin why the machinery is still worth keeping — it is
provably correct given the state (truth-fed it reaches the ceiling), it degrades to
exactly the shipped policy when it has nothing to add, and its behaviour is
reproducible from its observation history.
"""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.domain.movement import resolve_move
from p2p_thief_agent.strategy.adaptive_policy import PursuerTracker, choose_adaptive_action
from p2p_thief_agent.strategy.belief_policy import choose_evasive_action, initial_belief
from p2p_thief_agent.strategy.pursuer_models import PURSUERS, greedy_step

BOARD = Board(size=7)
COP_START = Coordinate(0, 0)
THIEF_START = Coordinate(4, 4)


def drive(pursuer, steps: int, board: Board = BOARD,
          cop: Coordinate = COP_START, thief: Coordinate = THIEF_START):
    """Play truth-fed turns; return (survived_steps, actions, tracker)."""
    tracker = PursuerTracker(steps)
    actions = []
    for step in range(1, steps + 1):
        cop = pursuer(board, cop, thief, frozenset())
        if cop == thief:
            return step - 1, actions, tracker
        action = choose_adaptive_action(board, thief, initial_belief(board, cop),
                                        tracker, step)
        actions.append(action)
        thief = resolve_move(board, thief, action, frozenset())
        if thief == cop:
            return step, actions, tracker
    return steps, actions, tracker


def test_identical_histories_give_identical_actions() -> None:
    _, first, _ = drive(greedy_step, 12)
    _, second, _ = drive(greedy_step, 12)
    assert first == second


def test_the_tracker_identifies_a_greedy_pursuer() -> None:
    _, _, tracker = drive(greedy_step, 10)
    assert tracker.best() == "greedy"
    assert tracker.scores["greedy"] >= max(tracker.scores.values())


def test_truth_fed_it_escapes_every_archetype_to_the_horizon() -> None:
    """The diagnostic that localised the six failures: given the state, the planner
    is perfect — so the estimator, not the strategy, is the remaining gap."""
    for pursuer in PURSUERS.values():
        survived, _, _ = drive(pursuer, 20)
        assert survived == 20


def test_with_nothing_to_add_it_is_exactly_the_shipped_policy() -> None:
    """No escape under any model → the ranking is the shipped one, bit for bit."""
    board = Board(size=3)
    thief, believed = Coordinate(1, 1), Coordinate(0, 1)
    tracker = PursuerTracker(300)  # a horizon no 3x3 escape survives against anyone
    belief = initial_belief(board, believed)
    adaptive = choose_adaptive_action(board, thief, belief, tracker, 1)
    shipped = choose_evasive_action(board, thief, belief)
    assert adaptive == shipped


def test_actions_are_always_legal_around_disclosed_barriers() -> None:
    barriers = {Coordinate(4, 5), Coordinate(3, 4)}
    tracker = PursuerTracker(35)
    action = choose_adaptive_action(BOARD, Coordinate(4, 4),
                                    initial_belief(BOARD, Coordinate(0, 0)),
                                    tracker, 1, barriers)
    target = resolve_move(BOARD, Coordinate(4, 4), action, frozenset(barriers))
    assert target not in barriers
    BOARD.validate_position(target)


def test_a_barrier_change_invalidates_the_solver_memos() -> None:
    tracker = PursuerTracker(35)
    choose_adaptive_action(BOARD, Coordinate(4, 4),
                           initial_belief(BOARD, Coordinate(0, 0)), tracker, 1)
    assert sum(len(memo) for memo in tracker._memos.values()) > 0
    sentinel = ("stale-graph-answer",)
    tracker._memos["greedy"][sentinel] = True
    choose_adaptive_action(BOARD, Coordinate(4, 4),
                           initial_belief(BOARD, Coordinate(0, 0)), tracker, 2,
                           barriers={Coordinate(6, 6)})
    assert sentinel not in tracker._memos["greedy"], (
        "the old graph's answers must not survive a new wall")


def test_the_tracker_refuses_a_nonsense_horizon() -> None:
    import pytest

    with pytest.raises(ValueError, match="horizon"):
        PursuerTracker(0)
