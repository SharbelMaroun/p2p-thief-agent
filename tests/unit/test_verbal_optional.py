"""`M6-013`: the verbal layer is strictly optional — a whole series plays at zero tokens.

Disabling every provider must still produce a complete, legal game. Here a full series
(six sub-games of the negotiated step limit) runs the whole loop — generate a hint, consume
it into belief, choose a legal move — with no provider ever given, so no token is spent
(`AF-t21`). The provider-outage fallback is proven in `test_generation.py`.
"""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.domain.movement import legal_actions
from p2p_thief_agent.perception.belief import uniform_belief
from p2p_thief_agent.perception.consume import consume_hint
from p2p_thief_agent.perception.trust import NEUTRAL_TRUST
from p2p_thief_agent.strategy.belief_policy import choose_evasive_action
from p2p_thief_agent.verbal.generation import generate_hint
from p2p_thief_agent.verbal.hints import validate_hint

BOARD = Board(size=7)
HERE = Coordinate(3, 3)


def test_a_full_series_plays_a_complete_legal_game_at_zero_tokens() -> None:
    """`M6-013a`: six sub-games of 35 steps, no provider — every turn is legal and token-free."""
    legal = legal_actions(BOARD, HERE, frozenset())
    belief = uniform_belief(7, 7)
    for step in range(6 * 35):
        hint = generate_hint(step)  # no provider: the template path only, zero tokens
        assert validate_hint(hint.text) == hint.text
        assert hint.intent in ("truth", "bluff")
        belief = consume_hint(belief, hint.text, NEUTRAL_TRUST, 7, 7)
        assert choose_evasive_action(BOARD, HERE, belief) in legal
