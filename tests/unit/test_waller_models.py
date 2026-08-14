"""Walling pursuer archetypes: legality, finish/seal/chase, determinism (`M6-034`)."""

from p2p_thief_agent.domain.barriers import validate_barrier_placement
from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate, DomainError
from p2p_thief_agent.strategy.metrics import mobility
from p2p_thief_agent.strategy.waller_models import (
    WALLERS,
    greedy_waller,
    interceptor_waller,
    wall_candidates,
)

BOARD = Board(size=7)


def test_every_proposed_wall_is_a_legal_domain_placement() -> None:
    """Strategy proposes, the domain validates: no candidate may be an illegal placement."""
    for r in range(7):
        for c in range(7):
            cop = Coordinate(r, c)
            for cell in wall_candidates(BOARD, cop, frozenset()):
                # Raises DomainError if illegal; a clean return is the assertion.
                validate_barrier_placement(BOARD, cop, cell, frozenset(), quota=14)


def test_candidates_are_orthogonal_and_on_board() -> None:
    cop = Coordinate(0, 0)
    cells = wall_candidates(BOARD, cop, frozenset())
    assert Coordinate(0, 1) in cells and Coordinate(1, 0) in cells
    assert all(BOARD.contains(cell) for cell in cells)
    assert Coordinate(-1, 0) not in cells  # off-board pruned


def test_a_wall_finishes_an_adjacent_thief() -> None:
    """When the Thief sits on an in-range cell the waller walls it, forgoing the move."""
    cop, thief = Coordinate(5, 6), Coordinate(6, 6)
    new_cop, wall = greedy_waller(BOARD, cop, thief, frozenset(), 14)
    assert wall == thief and new_cop == cop


def test_a_seal_removes_an_exit_when_room_is_scarce() -> None:
    """With the Thief down to two exits, and its own cell out of walling range, the waller
    spends a wall on one of the Thief's exits rather than chasing."""
    thief, cop = Coordinate(6, 0), Coordinate(6, 2)  # a scarce corner, Police two cells away
    before = mobility(BOARD, thief, frozenset())
    _, wall = greedy_waller(BOARD, cop, thief, frozenset(), 14)
    assert wall is not None
    assert mobility(BOARD, thief, frozenset({wall})) < before


def test_no_quota_forces_a_move_not_a_wall() -> None:
    cop, thief = Coordinate(5, 6), Coordinate(6, 6)
    new_cop, wall = greedy_waller(BOARD, cop, thief, frozenset(), 0)
    assert wall is None and new_cop != cop  # it moved


def test_open_board_far_thief_just_chases() -> None:
    cop, thief = Coordinate(0, 0), Coordinate(6, 6)
    new_cop, wall = interceptor_waller(BOARD, cop, thief, frozenset(), 14)
    assert wall is None
    assert new_cop != cop  # moved toward the thief


def test_wallers_are_deterministic() -> None:
    cop, thief = Coordinate(1, 1), Coordinate(4, 5)
    for name, waller in WALLERS.items():
        first = waller(BOARD, cop, thief, frozenset(), 14)
        second = waller(BOARD, cop, thief, frozenset(), 14)
        assert first == second, name


def test_a_placed_wall_is_not_reproposed() -> None:
    """An already-blocked candidate is not offered again (no double placement)."""
    cop = Coordinate(3, 3)
    first = Coordinate(2, 3)
    assert first not in wall_candidates(BOARD, cop, frozenset({first}))


def test_invalid_placement_far_cell_is_rejected_by_domain() -> None:
    """Guard: a non-adjacent cell is not a legal wall, proving the domain is the authority."""
    try:
        validate_barrier_placement(BOARD, Coordinate(0, 0), Coordinate(3, 3), frozenset(), quota=14)
    except DomainError:
        return
    raise AssertionError("a distant cell must not validate as a legal barrier")
