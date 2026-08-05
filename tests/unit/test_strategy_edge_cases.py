"""`M6-025`/`M6-026`: the strategy stays legal and sane at the board's hard edges.

A near-quota barrier layout must still yield a legal, sensible evasive move, and a fully
enclosed Thief — where the only legal action is `STAY` — must still return that action
rather than raise, so capture resolves on the board and not in a crash.
"""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Action, Coordinate
from p2p_thief_agent.domain.movement import legal_actions
from p2p_thief_agent.strategy.belief_policy import choose_evasive_action

BOARD = Board(size=7)


def _peaked(row: int, col: int) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(1.0 if (r, c) == (row, col) else 0.0 for c in range(7)) for r in range(7))


def test_a_barrier_heavy_board_still_yields_a_legal_sane_move() -> None:
    """`M6-025`: 14 barriers (the Appendix F maximum) wall the Thief in, leaving an escape east."""
    barriers = frozenset(Coordinate(2, c) for c in range(7)) | frozenset(Coordinate(4, c) for c in range(7))
    assert len(barriers) == 14
    here = Coordinate(3, 3)
    action = choose_evasive_action(BOARD, here, _peaked(3, 0), barriers)  # Cop believed to the west
    assert action in legal_actions(BOARD, here, barriers)
    assert action is Action.EAST  # the sane flee from a western threat along the open corridor


def test_when_only_stay_is_legal_the_thief_still_returns_it() -> None:
    """`M6-026`: a corner with both neighbours barriered leaves only STAY — returned, not raised."""
    corner = Coordinate(0, 0)
    barriers = frozenset({Coordinate(0, 1), Coordinate(1, 0)})
    assert set(legal_actions(BOARD, corner, barriers)) == {Action.STAY}
    assert choose_evasive_action(BOARD, corner, _peaked(6, 6), barriers) is Action.STAY
