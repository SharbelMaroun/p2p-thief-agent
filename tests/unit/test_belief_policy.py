"""`M6-004a`/`M6-004e`/`M6-004g`: the belief-driven evasion policy.

The move is read off the belief but produced by the deterministic baseline policy, so it
is always legal (belief may misdirect, never make an illegal move), maximises distance from
the believed Cop cell, and is reproducible.
"""

import inspect

import pytest

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Action, Coordinate, DomainError
from p2p_thief_agent.domain.movement import legal_actions, resolve_move
from p2p_thief_agent.strategy.belief_policy import believed_cop_cell, choose_evasive_action
from p2p_thief_agent.strategy.metrics import manhattan_distance

BOARD = Board(size=5)


def peaked(row: int, col: int) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(1.0 if (r, c) == (row, col) else 0.0 for c in range(5)) for r in range(5))


def uniform() -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(1 / 25 for _ in range(5)) for _ in range(5))


def test_the_believed_cell_is_the_argmax_of_the_belief() -> None:
    assert believed_cop_cell(peaked(3, 4), BOARD) == Coordinate(3, 4)


def test_a_flat_belief_breaks_ties_deterministically_at_the_lowest_cell() -> None:
    assert believed_cop_cell(uniform(), BOARD) == Coordinate(0, 0)


def test_a_belief_of_the_wrong_size_is_rejected() -> None:
    with pytest.raises(DomainError, match="5x5 grid"):
        believed_cop_cell(((1.0, 0.0), (0.0, 0.0)), BOARD)


def test_the_move_increases_distance_from_the_believed_cop() -> None:
    """`M6-004a`: from the centre, believing the Cop is in a corner drives the Thief away."""
    here = Coordinate(2, 2)
    action = choose_evasive_action(BOARD, here, peaked(0, 0))
    landed = resolve_move(BOARD, here, action, frozenset())
    assert manhattan_distance(landed, Coordinate(0, 0)) > manhattan_distance(here, Coordinate(0, 0))


def test_every_emitted_action_is_legal_even_when_belief_points_at_our_own_cell() -> None:
    """`M6-004e`: a misdirecting belief can never yield an illegal move."""
    here = Coordinate(2, 2)
    action = choose_evasive_action(BOARD, here, peaked(2, 2))
    assert action in legal_actions(BOARD, here, frozenset())


def test_the_policy_is_deterministic() -> None:
    """`M6-004g`: identical inputs yield an identical action, every call."""
    here = Coordinate(1, 1)
    belief = peaked(4, 4)
    first = choose_evasive_action(BOARD, here, belief)
    for _ in range(5):
        assert choose_evasive_action(BOARD, here, belief) == first
    assert isinstance(first, Action)


def test_the_policy_carries_no_tunable_weights_to_leak() -> None:
    """`M6-004h`: the policy is deliberately weight-free — its criteria are lexicographic,
    not a weighted sum — so there is no tuning value that could enter the shared JSON. If
    tuning is ever added it must load from the private TOML only (`ADR-0004`)."""
    assert set(inspect.signature(choose_evasive_action).parameters) == {
        "board", "position", "belief", "barriers",
    }
