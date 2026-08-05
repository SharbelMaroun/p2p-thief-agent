"""`M6-007`: the scent model is symmetric and involuntary, and only the opponent's field
is read as evidence.
"""

import inspect
from pathlib import Path

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.perception.belief import uniform_belief
from p2p_thief_agent.perception.field import (
    blank_field,
    deposit,
    emit_at,
    scent_likelihood,
)
from p2p_thief_agent.perception.scent import advance_field

BOARD = Board(size=7)
HERE = Coordinate(3, 3)


def test_emission_is_centred_on_the_agents_cell() -> None:
    field = emit_at(BOARD, HERE)
    assert field[3][3] == 0.90
    assert field[2][3] == 0.62  # orthogonal neighbour


def test_the_window_is_clipped_at_the_board_edge() -> None:
    """A corner agent still emits — the off-board part of the 5×5 is simply dropped."""
    field = emit_at(BOARD, Coordinate(0, 0))
    assert field[0][0] == 0.90
    assert sum(v for row in field for v in row) > 0


def test_staying_still_still_deposits_scent() -> None:
    """`M6-007a`: a STAY lands on the same cell and emits again, above decay alone."""
    once = deposit(blank_field(BOARD), BOARD, HERE)
    stayed = deposit(once, BOARD, HERE)
    decayed_only = advance_field(once, blank_field(BOARD))
    assert stayed[3][3] > decayed_only[3][3]


def test_emission_cannot_be_conditioned_or_suppressed() -> None:
    """`M6-007c`: no action to branch on and no flag to skip — emission is unconditional."""
    assert set(inspect.signature(deposit).parameters) == {"field", "board", "cell"}
    assert set(inspect.signature(emit_at).parameters) == {"board", "cell"}
    assert any(v > 0 for row in emit_at(BOARD, HERE) for v in row)


def test_scent_likelihood_concentrates_where_the_opponent_field_points() -> None:
    likelihood = scent_likelihood({(3, 3): 0.9, (1, 1): 0.2}, BOARD)
    assert likelihood[3][3] > likelihood[1][1] > likelihood[0][0]


def test_an_empty_observation_is_uniform_evidence() -> None:
    assert scent_likelihood({}, BOARD) == uniform_belief(7, 7)


def test_an_off_board_observed_cell_is_ignored() -> None:
    """Defence in depth: an out-of-range cell contributes nothing rather than crashing."""
    likelihood = scent_likelihood({(99, 99): 0.5, (3, 3): 0.9}, BOARD)
    assert likelihood[3][3] > 0
    assert sum(v for row in likelihood for v in row) > 0


def test_the_belief_modules_never_read_own_emission() -> None:
    """`M6-007b`: the belief update consumes only the opponent's observed field.

    The own-emission functions (`emit_at`, `deposit`) are the outbound path; a guard proves
    the belief/hint/trust modules never import or call them, so own scent cannot become
    evidence.
    """
    perception = Path(__file__).resolve().parents[2] / "src" / "p2p_thief_agent" / "perception"
    for module in ("belief.py", "hint.py", "trust.py"):
        text = (perception / module).read_text(encoding="utf-8")
        assert "emit_at" not in text and "deposit" not in text, module
