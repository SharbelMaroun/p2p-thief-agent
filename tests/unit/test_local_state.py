"""Unit tests for M3-001 immutable Thief-local state and history snapshots."""

import dataclasses

import pytest

from p2p_thief_agent.domain import Action, Board, Coordinate, DomainError
from p2p_thief_agent.state.local_state import ThiefLocalState, ThiefSnapshot

BOARD = Board(size=7)
CENTRE = Coordinate(3, 3)


def _start() -> ThiefLocalState:
    return ThiefLocalState(board=BOARD, position=CENTRE)


def test_start_state_has_no_history_and_step_zero():
    state = _start()
    assert state.step == 0
    assert state.history == ()
    assert state.last_action is None
    assert state.trajectory() == (state.snapshot(),)


def test_advance_returns_new_state_without_mutating_original():
    state = _start()
    moved = state.advance(Action.NORTH)
    assert state.position == CENTRE and state.step == 0 and state.history == ()
    assert moved.position == Coordinate(2, 3)
    assert moved.step == 1
    assert moved.last_action is Action.NORTH


def test_history_snapshots_accumulate_in_order():
    state = _start().advance(Action.NORTH).advance(Action.EAST)
    assert len(state.history) == 2
    assert state.history[0] == ThiefSnapshot(0, CENTRE, state.history[0].known_barriers, None)
    assert state.history[1].step == 1
    assert state.history[1].action is Action.NORTH
    assert [s.step for s in state.trajectory()] == [0, 1, 2]


def test_state_is_frozen():
    state = _start()
    with pytest.raises(dataclasses.FrozenInstanceError):
        state.position = Coordinate(0, 0)  # type: ignore[misc]


def test_advance_respects_known_barriers():
    blocked = _start().record_barrier(Coordinate(2, 3), step=0)
    with pytest.raises(DomainError):
        blocked.advance(Action.NORTH)


def test_advance_off_board_rejected():
    corner = ThiefLocalState(board=BOARD, position=Coordinate(0, 0))
    with pytest.raises(DomainError):
        corner.advance(Action.NORTH)


def test_stay_advances_step_without_moving():
    state = _start().advance(Action.STAY)
    assert state.position == CENTRE
    assert state.step == 1
    assert state.last_action is Action.STAY


def test_record_barrier_defaults_to_current_step():
    state = _start().advance(Action.NORTH)  # step 1
    known = state.record_barrier(Coordinate(1, 3))
    assert known.known_barriers.disclosed_at(Coordinate(1, 3)) == 1
    # Recording a disclosure does not advance the turn.
    assert known.step == state.step
    assert known.history == state.history


def test_record_barrier_keeps_barrier_across_advance():
    state = _start().record_barrier(Coordinate(4, 3), step=0)
    moved = state.advance(Action.NORTH)
    assert moved.known_barriers.blocks(Coordinate(4, 3))


def test_off_board_start_rejected():
    with pytest.raises(DomainError):
        ThiefLocalState(board=BOARD, position=Coordinate(9, 9))


def test_negative_step_rejected():
    with pytest.raises(DomainError):
        ThiefLocalState(board=BOARD, position=CENTRE, step=-1)


def test_snapshot_reflects_current_truth():
    state = _start().advance(Action.SOUTH)
    snap = state.snapshot()
    assert snap.step == 1
    assert snap.position == Coordinate(4, 3)
    assert snap.action is Action.SOUTH
