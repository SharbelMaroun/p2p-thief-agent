"""Unit tests for the deterministic Thief baseline policy."""

import pytest

from p2p_thief_agent.domain import Action, Board, Coordinate, DomainError, legal_actions
from p2p_thief_agent.strategy.baseline import choose_action, is_dead_end, rank_actions
from p2p_thief_agent.strategy.metrics import manhattan_distance

BOARD = Board(size=7)
CENTRE = Coordinate(3, 3)


def _target(position, action, barriers=()):
    from p2p_thief_agent.domain import resolve_move

    return resolve_move(BOARD, position, action, barriers)


def test_choice_is_always_a_legal_action():
    police = [Coordinate(0, 0)]
    for row in range(7):
        for col in range(7):
            here = Coordinate(row, col)
            assert choose_action(BOARD, here, police) in legal_actions(BOARD, here)


def test_flees_from_an_adjacent_threat():
    police = [Coordinate(3, 2)]
    chosen = choose_action(BOARD, CENTRE, police)
    moved_to = _target(CENTRE, chosen)
    assert manhattan_distance(moved_to, police[0]) > manhattan_distance(CENTRE, police[0])


def test_maximizes_distance_from_the_nearest_of_several_threats():
    # Two threats to the west; south and east are equally distance-maximizing.
    police = [Coordinate(3, 1), Coordinate(2, 1)]
    chosen = choose_action(BOARD, CENTRE, police)
    before = min(manhattan_distance(CENTRE, threat) for threat in police)
    after = min(manhattan_distance(_target(CENTRE, chosen), threat) for threat in police)
    assert after > before
    assert chosen in (Action.SOUTH, Action.EAST)


def test_never_steps_into_a_dead_end_pocket():
    # (3, 4) keeps only its way back to (3, 3), so EAST must be rejected.
    barriers = [Coordinate(2, 4), Coordinate(4, 4), Coordinate(3, 5)]
    assert is_dead_end(BOARD, Coordinate(3, 4), CENTRE, barriers)
    assert choose_action(BOARD, CENTRE, [Coordinate(0, 0)], barriers) is not Action.EAST


def test_dead_end_actions_are_ranked_last():
    barriers = [Coordinate(2, 4), Coordinate(4, 4), Coordinate(3, 5)]
    ranked = rank_actions(BOARD, CENTRE, [Coordinate(0, 0)], barriers)
    assert ranked[-1] is Action.EAST


def test_prefers_the_open_side_over_a_walled_corridor():
    # Walls north of the centre make the northern cell a narrow corridor.
    barriers = [Coordinate(2, 2), Coordinate(2, 4)]
    assert choose_action(BOARD, CENTRE, [Coordinate(6, 3)], barriers) is not Action.NORTH


def test_moves_away_from_a_threat_sitting_in_a_corner():
    here = Coordinate(1, 1)
    chosen = choose_action(BOARD, here, [Coordinate(0, 0)])
    assert chosen in (Action.SOUTH, Action.EAST)
    assert _target(here, chosen) not in (Coordinate(0, 1), Coordinate(1, 0))


def test_distance_outranks_corner_avoidance_as_specified():
    # Documented priority: fleeing beats staying central, even towards an edge.
    chosen = choose_action(BOARD, Coordinate(1, 1), [Coordinate(6, 6)])
    assert chosen in (Action.NORTH, Action.WEST)


def test_prefers_higher_mobility_when_no_threat_is_known():
    # A barrier at (1, 3) costs the northern target one onward escape.
    assert choose_action(BOARD, CENTRE, [], [Coordinate(1, 3)]) is not Action.NORTH


def test_tie_break_uses_fixed_action_order_on_a_symmetric_board():
    # Open centre, no threats: every candidate ties, so the first Action wins.
    assert choose_action(BOARD, CENTRE) is Action.NORTH


def test_absent_threats_do_not_rank_every_cell_as_threatened():
    assert choose_action(BOARD, CENTRE, []) is Action.NORTH
    assert choose_action(BOARD, CENTRE) is Action.NORTH


def test_repeated_calls_are_deterministic():
    police = [Coordinate(5, 2), Coordinate(1, 4)]
    barriers = [Coordinate(3, 4), Coordinate(2, 2)]
    results = {choose_action(BOARD, CENTRE, police, barriers) for _ in range(25)}
    assert len(results) == 1


def test_threat_order_does_not_change_the_choice():
    police = [Coordinate(5, 2), Coordinate(1, 4), Coordinate(0, 0)]
    assert choose_action(BOARD, CENTRE, police) is choose_action(BOARD, CENTRE, reversed(police))


def test_rank_actions_returns_every_legal_action_exactly_once():
    barriers = [Coordinate(2, 3)]
    ranked = rank_actions(BOARD, CENTRE, [Coordinate(0, 0)], barriers)
    assert sorted(ranked, key=str) == sorted(legal_actions(BOARD, CENTRE, barriers), key=str)


def test_fallback_still_returns_a_legal_action_when_every_option_is_a_dead_end():
    # Fully surrounded: STAY is the only legal action and is itself a dead end.
    barriers = [Coordinate(2, 3), Coordinate(4, 3), Coordinate(3, 2), Coordinate(3, 4)]
    assert legal_actions(BOARD, CENTRE, barriers) == [Action.STAY]
    assert choose_action(BOARD, CENTRE, [Coordinate(0, 0)], barriers) is Action.STAY


def test_fallback_survives_a_corner_sealed_by_barriers():
    corner = Coordinate(0, 0)
    barriers = [Coordinate(0, 1), Coordinate(1, 0)]
    assert choose_action(BOARD, corner, [Coordinate(6, 6)], barriers) is Action.STAY


def test_off_board_position_is_rejected_rather_than_repaired():
    with pytest.raises(DomainError):
        choose_action(BOARD, Coordinate(9, 9), [Coordinate(0, 0)])


def test_rank_actions_rejects_any_off_board_police_position():
    police = [Coordinate(0, 0), Coordinate(9, 9)]

    with pytest.raises(DomainError):
        rank_actions(BOARD, CENTRE, police)


def test_policy_works_on_a_board_with_a_nonzero_axis_start_index():
    board = Board(size=5, axis_start_index=1)
    here = Coordinate(3, 3)
    assert choose_action(board, here, [Coordinate(1, 1)]) in legal_actions(board, here)
