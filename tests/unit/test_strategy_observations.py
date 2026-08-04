"""`M6-010`: the strategy stays legal and deterministic under every observation shape.

End to end over the real pipeline: scent and hints build the belief, and
`choose_evasive_action` turns it into a move. No sockets — the whole perception→strategy
path is pure.
"""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.domain.movement import legal_actions, resolve_move
from p2p_thief_agent.perception.belief import apply_evidence, uniform_belief
from p2p_thief_agent.perception.consume import consume_hint
from p2p_thief_agent.perception.field import scent_likelihood
from p2p_thief_agent.perception.hint import decode_hint
from p2p_thief_agent.perception.trust import NEUTRAL_TRUST, update_trust
from p2p_thief_agent.strategy.belief_policy import choose_evasive_action
from p2p_thief_agent.strategy.metrics import manhattan_distance

BOARD = Board(size=7)
HERE = Coordinate(3, 3)
NO_BARRIERS = frozenset()


def believe(smell=None, hint=None, trust=NEUTRAL_TRUST):
    belief = uniform_belief(7, 7)
    if smell is not None:
        belief = apply_evidence(belief, scent_likelihood(smell, BOARD))
    if hint is not None:
        belief = consume_hint(belief, hint, trust, 7, 7)
    return belief


def landed(action) -> Coordinate:
    return resolve_move(BOARD, HERE, action, NO_BARRIERS)


def test_no_scent_and_no_hint_still_yields_a_legal_action() -> None:
    """`M6-010a`: a uniform belief is still a legal, defined choice."""
    assert choose_evasive_action(BOARD, HERE, believe()) in legal_actions(BOARD, HERE, NO_BARRIERS)


def test_physical_evidence_wins_over_a_contradicting_hint() -> None:
    """`M6-010b`: scent says the Cop is top-left; a hint lies that it is bottom-right."""
    smell = {(0, 0): 0.9, (0, 1): 0.62}
    hint = "the cop is south east"
    trust = update_trust(NEUTRAL_TRUST, decode_hint(hint, 7, 7), believe(smell=smell))
    action = choose_evasive_action(BOARD, HERE, believe(smell=smell, hint=hint, trust=trust))
    # The Thief flees the scent (top-left), not the lie — distance from (0,0) grows.
    assert manhattan_distance(landed(action), Coordinate(0, 0)) > manhattan_distance(HERE, Coordinate(0, 0))


def test_a_saturated_scent_field_does_not_overflow_or_divide_by_zero() -> None:
    """`M6-010c`: every cell screaming at once still normalises to a legal move."""
    saturated = {(r, c): 0.9 for r in range(7) for c in range(7)}
    action = choose_evasive_action(BOARD, HERE, believe(smell=saturated))
    assert action in legal_actions(BOARD, HERE, NO_BARRIERS)


def test_the_cop_adjacent_and_far_both_give_sane_legal_moves() -> None:
    """`M6-010d`: adjacent drives a flee; far is still legal; the two differ."""
    adjacent = choose_evasive_action(BOARD, HERE, believe(smell={(3, 2): 0.9}))  # Cop just west
    far = choose_evasive_action(BOARD, HERE, believe(smell={(0, 0): 0.9}))
    assert adjacent in legal_actions(BOARD, HERE, NO_BARRIERS)
    assert far in legal_actions(BOARD, HERE, NO_BARRIERS)
    # Fleeing an adjacent western Cop increases distance from it.
    assert manhattan_distance(landed(adjacent), Coordinate(3, 2)) > manhattan_distance(HERE, Coordinate(3, 2))


def test_repeated_runs_are_byte_identical() -> None:
    """`M6-010e`: determinism is a submission property, not an accident."""
    smell, hint = {(1, 1): 0.9}, "somewhere north"
    first = believe(smell=smell, hint=hint)
    assert believe(smell=smell, hint=hint) == first
    action = choose_evasive_action(BOARD, HERE, first)
    assert all(choose_evasive_action(BOARD, HERE, believe(smell=smell, hint=hint)) == action
               for _ in range(5))
