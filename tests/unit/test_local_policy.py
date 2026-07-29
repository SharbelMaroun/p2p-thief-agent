"""Unit tests for M3-004 baseline integration over Thief-local state."""

from p2p_thief_agent.domain import Board, Coordinate, legal_actions, resolve_move
from p2p_thief_agent.state.local_state import ThiefLocalState
from p2p_thief_agent.state.policy import (
    choose_local_action,
    local_outcome,
    rank_local_actions,
    step_with_baseline,
)
from p2p_thief_agent.state.scoring import Outcome
from p2p_thief_agent.strategy.baseline import choose_action

BOARD = Board(size=7)
CENTRE = Coordinate(3, 3)


def _start(position=CENTRE, barriers=()) -> ThiefLocalState:
    state = ThiefLocalState(board=BOARD, position=position)
    for cell in barriers:
        state = state.record_barrier(cell, step=0)
    return state


def test_choice_matches_the_pure_baseline():
    police = [Coordinate(0, 0)]
    state = _start()
    assert choose_local_action(state, police) == choose_action(BOARD, CENTRE, police)


def test_choice_is_deterministic_and_repeatable():
    police = [Coordinate(1, 1)]
    state = _start()
    first = choose_local_action(state, police)
    second = choose_local_action(state, police)
    assert first == second


def test_ranking_covers_every_legal_action():
    state = _start()
    ranked = rank_local_actions(state, [Coordinate(0, 0)])
    assert set(ranked) == set(legal_actions(BOARD, CENTRE))
    assert len(ranked) == len(set(ranked))


def test_step_with_baseline_advances_by_the_chosen_action():
    police = [Coordinate(0, 0)]
    state = _start()
    chosen = choose_local_action(state, police)
    advanced = step_with_baseline(state, police)
    assert advanced.position == resolve_move(BOARD, CENTRE, chosen, ())
    assert advanced.step == 1
    assert advanced.last_action is chosen
    assert len(advanced.history) == 1


def test_known_barriers_are_honoured_by_the_bound_policy():
    # Fence the north cell into a dead end; the policy must not head north.
    barriers = [Coordinate(1, 3), Coordinate(2, 2), Coordinate(2, 4)]
    state = _start(barriers=barriers)
    advanced = step_with_baseline(state, [Coordinate(6, 3)])
    assert advanced.position != Coordinate(2, 3)


def test_trapped_state_is_a_capture_outcome():
    barriers = [Coordinate(2, 3), Coordinate(4, 3), Coordinate(3, 2), Coordinate(3, 4)]
    state = _start(barriers=barriers)
    assert local_outcome(state, Coordinate(6, 6)) is Outcome.CAPTURE


def test_same_cell_is_a_capture_outcome():
    state = _start()
    assert local_outcome(state, CENTRE) is Outcome.CAPTURE


def test_survival_outcome_at_the_horizon():
    state = ThiefLocalState(board=BOARD, position=CENTRE, step=35)
    assert local_outcome(state, Coordinate(0, 0), survival_threshold=35) is Outcome.SURVIVAL


def test_in_progress_state_has_no_outcome():
    state = _start()
    assert local_outcome(state, Coordinate(0, 0)) is None


def test_technical_loss_flag_overrides_local_outcome():
    state = _start()
    assert (
        local_outcome(state, Coordinate(0, 0), technical_loss=True) is Outcome.TECHNICAL_LOSS
    )
