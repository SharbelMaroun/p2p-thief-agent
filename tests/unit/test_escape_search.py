"""The exact escape solver: correct at the edges, consistent under memoisation (`M6-029`)."""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.domain.movement import legal_actions, resolve_move
from p2p_thief_agent.strategy.escape_search import escape_actions, survives
from p2p_thief_agent.strategy.pursuer_models import PURSUERS, greedy_step

BOARD = Board(size=7)
SMALL = Board(size=5)
OPEN = frozenset()


def test_the_horizon_itself_is_survival() -> None:
    assert survives(BOARD, greedy_step, Coordinate(0, 0), Coordinate(0, 1), 0, OPEN, {})


def test_a_thief_in_the_pursuers_hands_is_caught() -> None:
    """The pursuer moves first: adjacent means its next step lands on us."""
    assert not survives(BOARD, greedy_step, Coordinate(3, 3), Coordinate(3, 4), 1, OPEN, {})


def test_escape_actions_are_legal_and_their_promise_holds() -> None:
    thief, cop = Coordinate(3, 3), Coordinate(0, 0)
    memo: dict = {}
    winners = escape_actions(BOARD, greedy_step, thief, cop, 10, OPEN, memo)
    assert winners, "an open board with the pursuer three walls away is survivable"
    legal = set(legal_actions(BOARD, thief, OPEN))
    for action in winners:
        assert action in legal
        target = resolve_move(BOARD, thief, action, OPEN)
        assert target != cop
        assert survives(BOARD, greedy_step, cop, target, 10, OPEN, memo)


def test_the_ceiling_row_reproduces_on_a_small_board() -> None:
    """The report's ceiling — escape always available against every archetype from
    every opposite-perimeter opening — checked exhaustively at 5×5, horizon 15."""
    from scripts.run_experiments import openings

    for model in PURSUERS.values():
        memo: dict = {}
        for cop, thief in openings(5):
            chased = model(SMALL, cop, thief, OPEN)
            if chased == thief:
                continue  # the opening itself is decided before the thief moves
            assert escape_actions(SMALL, model, thief, chased, 14, OPEN, memo), (
                f"no escape from {thief} against {model.__name__} — the ceiling row "
                "says one always exists")


def test_a_warm_memo_changes_nothing_but_speed() -> None:
    cop, thief = Coordinate(0, 0), Coordinate(4, 4)
    cold: dict = {}
    first = survives(BOARD, greedy_step, cop, thief, 12, OPEN, cold)
    again = survives(BOARD, greedy_step, cop, thief, 12, OPEN, cold)
    fresh = survives(BOARD, greedy_step, cop, thief, 12, OPEN, {})
    assert first == again == fresh


def test_barriers_change_the_answer_through_the_graph() -> None:
    """A wall that seals the corner corridor turns an escape into a capture."""
    thief, cop = Coordinate(0, 1), Coordinate(0, 3)
    walls = frozenset({Coordinate(1, 0), Coordinate(1, 1), Coordinate(1, 2)})
    open_answer = survives(BOARD, greedy_step, cop, thief, 6, OPEN, {})
    walled_answer = survives(BOARD, greedy_step, cop, thief, 6, walls, {})
    assert open_answer and not walled_answer


def test_negative_steps_are_refused() -> None:
    import pytest

    with pytest.raises(ValueError, match="steps_after"):
        escape_actions(BOARD, greedy_step, Coordinate(3, 3), Coordinate(0, 0), -1, OPEN, {})
