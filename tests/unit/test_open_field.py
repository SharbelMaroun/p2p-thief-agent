"""The space-defending evasion (`open_field_v3`).

Written against a measured threat rather than a hypothetical one. yanell11's Cop has never
placed a barrier -- 0 of 14, in every game either side has played -- while our own Cop won
run 7 by placing 10 and herding their Thief into a corner. Their logs contain that lesson
three times. When they copy it, the arm that was surviving on their omission stops
surviving; `arms_race.py` measures exactly that, and only this policy comes through.

These tests pin the properties that result rests on, not the outcome of any one duel.
"""

import pytest

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Action, Coordinate
from p2p_thief_agent.perception.belief import uniform_belief
from p2p_thief_agent.strategy.belief_policy import initial_belief
from p2p_thief_agent.strategy.open_field import (
    choose_open_field_action,
    reachable_room,
)

BOARD = Board(size=7)


def move(position, belief, blocked=frozenset()):
    return choose_open_field_action(
        BOARD, position, belief, None, 1, blocked, threshold=35, quota_remaining=14)


def test_the_open_middle_holds_more_room_than_a_corner() -> None:
    """The quantity the policy maximises has to rank the board the way a player would."""
    cop = Coordinate(0, 0)
    middle = reachable_room(BOARD, Coordinate(3, 3), cop, frozenset())
    corner = reachable_room(BOARD, Coordinate(6, 6), cop, frozenset())
    edge = reachable_room(BOARD, Coordinate(3, 6), cop, frozenset())
    assert middle > edge > corner


def test_a_wall_shrinks_the_room_immediately_not_when_it_lands_on_you() -> None:
    """Why distance cannot see a barrier coming, and this can.

    The Cop's distance is identical before and after it seals a doorway; the reachable
    region is not. That difference is the whole reason this policy exists.
    """
    cop, thief = Coordinate(0, 0), Coordinate(5, 5)
    before = reachable_room(BOARD, thief, cop, frozenset())
    penned = frozenset({Coordinate(4, 5), Coordinate(5, 4), Coordinate(4, 4)})
    after = reachable_room(BOARD, thief, cop, penned)
    assert after < before


def test_it_refuses_to_end_a_turn_beside_the_pursuer() -> None:
    """Adjacency is losing, not risky: the Cop moves first, so it simply steps on.

    The old policy chose STAY at distance 1 four times in run 4 and was captured for it.
    """
    cop = Coordinate(3, 4)
    belief = initial_belief(BOARD, cop)
    chosen = move(Coordinate(3, 3), belief)
    landed = {
        Action.NORTH: Coordinate(2, 3), Action.SOUTH: Coordinate(4, 3),
        Action.EAST: Coordinate(3, 4), Action.WEST: Coordinate(3, 2),
        Action.STAY: Coordinate(3, 3),
    }[chosen]
    assert abs(landed.row - cop.row) + abs(landed.col - cop.col) > 1


def test_it_walks_away_from_a_corner_it_is_standing_in() -> None:
    """Run 4 and run 7 both ended with the Thief pinned against an edge."""
    cop = Coordinate(3, 3)
    chosen = move(Coordinate(6, 6), initial_belief(BOARD, cop))
    assert chosen in (Action.NORTH, Action.WEST), "a corner must not be a resting place"


def test_a_flat_belief_still_produces_a_legal_move() -> None:
    """`M6-033`: no belief state may leave the Thief without an action."""
    assert move(Coordinate(3, 3), uniform_belief(BOARD.size, BOARD.size)) in set(Action)


def test_it_is_deterministic() -> None:
    """One message sequence must reproduce one game, or a replay audit disagrees."""
    belief = initial_belief(BOARD, Coordinate(1, 1))
    assert move(Coordinate(4, 4), belief) == move(Coordinate(4, 4), belief)


def test_walled_in_on_every_side_still_answers() -> None:
    """The fail-safe case: boxed completely, it must return STAY rather than raise."""
    blocked = frozenset({Coordinate(2, 3), Coordinate(4, 3),
                         Coordinate(3, 2), Coordinate(3, 4)})
    assert move(Coordinate(3, 3), initial_belief(BOARD, Coordinate(0, 0)), blocked) \
        is Action.STAY


@pytest.mark.parametrize("cell", [Coordinate(0, 0), Coordinate(0, 6),
                                  Coordinate(6, 0), Coordinate(6, 6)])
def test_every_corner_is_left_rather_than_defended(cell: Coordinate) -> None:
    chosen = move(cell, initial_belief(BOARD, Coordinate(3, 3)))
    assert chosen is not Action.STAY
