"""`M6-006b` regression, 2026-08-09: a foreign fixed-size scent window must not freeze
this Thief the way it froze the companion Cop repository.

The companion Cop repository's smell-grid parser rejected the whole grid when a peer's
fixed-size 5x5 window carried any off-board cell -- and a fixed-size window from a peer
near an edge or corner always does. This peer's own `cop_start` is `[0, 0]`
(`config/match_friendly_amireman.json`), a corner, so the same shape of defect here would
blind this Thief from turn 1 of every real match. `parse_smell_grid` now drops only the
impossible cells instead of the whole grid; these tests prove that fix end to end through
the live `decide` loop, using a foreign encoder that this repository's own tests never
otherwise construct (every other test builds its opponent windows via this repo's own
`encode_smell_grid`, which never emits an off-board key in the first place).
"""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.orchestration.thief_policy import make_decide
from p2p_thief_agent.perception.scent import emission_delta

BOARD = Board(size=7)


def foreign_fixed_window(step: int, cop_cell: Coordinate) -> dict:
    """A *different* (equally valid) encoder's turn: the locked emission stamp sent as a
    fixed-size 5x5 window in absolute board coordinates that "includes zero cells rather
    than omitting them" -- unlike this repo's own clipped encoder, this necessarily
    carries an off-board cell whenever `cop_cell` sits outside the board's central 3x3.
    Uses the real locked physics (`emission_delta`), not a placeholder constant, so the
    emitter decoder gets a genuine signal to match."""
    r0, c0 = cop_cell.row, cop_cell.col
    window = {
        f"{r0 + dr},{c0 + dc}": emission_delta(dr, dc)
        for dr in range(-2, 3) for dc in range(-2, 3)
        if emission_delta(dr, dc) > 0
    }
    return {"step": step, "sender": "police", "hint": "closing in", "smell_grid": window,
            "commit": "0" * 64, "timestamp": f"t{step}"}


def test_a_foreign_fixed_size_window_from_the_corner_is_not_discarded_wholesale() -> None:
    """A peer sending a fixed-size window necessarily carries an off-board cell from
    turn 1 against our real `cop_start`. The dropped-cell count must be nonzero *and*
    visible -- not just silently absorbed."""
    decide = make_decide(start=(3, 3), cop_start=(0, 0))
    decide(foreign_fixed_window(1, Coordinate(0, 0)), 1)
    assert decide.dropped_off_board() > 0, "a corner window must carry an off-board cell"


def test_belief_tracks_a_foreign_encoded_opponent_instead_of_freezing() -> None:
    """The decisive regression: under the old whole-grid rejection, a fixed-size window
    at *any* off-centre cell always raised, so belief never updated and stayed pinned at
    the turn-1 `cop_start` for the rest of the match no matter what the Cop did next. Two
    runs that differ only in the Cop's single legal turn-2 step (stay at (0,0), vs. the
    one legal move south to (1,0)) must now produce different *believed* Cop cells --
    proof the on-board remainder of a foreign window is actually being decoded, not
    discarded.

    Asserted on the believed cell, not the chosen action: the action is a coarse,
    five-valued projection of belief, and (0,0) vs. (1,0) are close enough that fleeing
    either from this Thief's position can legitimately pick the same direction even
    though the underlying belief genuinely moved -- that collapse is expected, not a bug,
    so it is not what this test is checking.

    (A larger, illegal jump between turns -- more than one cell -- can leave consecutive
    windows with no overlapping on-board cell at all, which `emitter_likelihood`
    deliberately treats as inconclusive and falls back to uniform; a real opponent's turn
    never produces such a jump, so that is a documented safety branch, not a gap here.)
    """
    stayed = make_decide(start=(3, 3), cop_start=(0, 0))
    stayed(foreign_fixed_window(1, Coordinate(0, 0)), 1)
    stayed(foreign_fixed_window(2, Coordinate(0, 0)), 2)

    moved = make_decide(start=(3, 3), cop_start=(0, 0))
    moved(foreign_fixed_window(1, Coordinate(0, 0)), 1)
    moved(foreign_fixed_window(2, Coordinate(1, 0)), 2)

    assert stayed.believed_cop_cell() != moved.believed_cop_cell(), (
        "a Cop that stayed at (0,0) and one that stepped to (1,0) must not leave the "
        "same believed cell -- if they do, belief is frozen and every foreign-encoded "
        "turn after the first is being silently discarded"
    )


def test_a_wholly_off_board_message_still_degrades_to_no_evidence_safely() -> None:
    """A message whose entire window is off-board (not just partly, as a corner window
    is) still resolves cleanly: `observed` is empty, the carried belief is kept, and the
    turn produces an ordinary legal move -- never an exception reaching the caller."""
    decide = make_decide(start=(3, 3), cop_start=(0, 0))
    message = {"step": 1, "sender": "police", "hint": "x",
               "smell_grid": {"-5,-5": 0.9, "-4,-5": 0.9},
               "commit": "0" * 64, "timestamp": "t1"}
    _, sealed = decide(message, 1)
    assert decide.dropped_off_board() == 2
    assert isinstance(sealed["payload"]["position"], list)
