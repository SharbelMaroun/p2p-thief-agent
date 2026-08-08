"""`M6-014`: stored regression vectors guard the scent field against silent physics drift.

These are golden values, not derivations: if the emission profile, the decay factor, or the
board-level deposit ever changes, one of these breaks — so a physics change can never slip in
unnoticed. The confirmed model is book Appendix F table 16 + Figure 4, with `(1-ρ)=0.9`.
"""

import pytest

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.perception.field import blank_field, deposit
from p2p_thief_agent.perception.scent import emission_field, settle

BOARD = Board(size=7)

# The exact 5×5 emission field, all six radial classes from Figure 4.
# **Corrected 2026-08-08**: the diagonal is 0.42 and the mid-side 0.20, and the d²=5 ring
# is 0.14 rather than a negotiated residual. The old matrix was this curve shifted inward
# by one radial class -- it matched at the centre, the cross and the corners, which is why
# it looked right. Hand-derived from the class values and cross-checked against the code.
EXPECTED_EMISSION = (
    (0.04, 0.14, 0.20, 0.14, 0.04),
    (0.14, 0.42, 0.62, 0.42, 0.14),
    (0.20, 0.62, 0.90, 0.62, 0.20),
    (0.14, 0.42, 0.62, 0.42, 0.14),
    (0.04, 0.14, 0.20, 0.14, 0.04),
)

# Pure decay of a lone cell over five turns, settle(τ, 0): retains 90% each turn.
DECAY_SEQUENCE = [0.9, 0.81, 0.729, 0.6561, 0.59049]

# Repeated emission on one cell (STAY), settle(τ, 0.9): accumulates.
STAY_SEQUENCE = [0.9, 1.71, 2.439, 3.0951]


def test_the_emission_field_matches_the_stored_vector() -> None:
    assert emission_field() == EXPECTED_EMISSION


def test_pure_decay_matches_the_stored_sequence() -> None:
    tau = 0.9
    seen = [tau]
    for _ in range(4):
        tau = settle(tau, 0.0)
        seen.append(tau)
    assert seen == pytest.approx(DECAY_SEQUENCE)


def test_repeated_emission_on_one_cell_matches_the_stored_sequence() -> None:
    tau = 0.9
    seen = [tau]
    for _ in range(3):
        tau = settle(tau, 0.9)
        seen.append(tau)
    assert seen == pytest.approx(STAY_SEQUENCE)


def test_a_board_deposit_and_a_stay_match_the_stored_field() -> None:
    field = deposit(blank_field(BOARD), BOARD, Coordinate(3, 3))
    assert field[3][3] == 0.90  # centre emission on a blank field
    assert field[2][3] == 0.62  # orthogonal neighbour
    assert field[1][1] == 0.04  # the d²=8 corner of the window

    stayed = deposit(field, BOARD, Coordinate(3, 3))  # decay then re-emit on the same cell
    assert stayed[3][3] == pytest.approx(0.9 * 0.90 + 0.90)  # 1.71
    assert stayed[2][3] == pytest.approx(0.9 * 0.62 + 0.62)  # 1.178
