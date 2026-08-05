"""`M6-009`: consume an inbound hint into belief without ever trusting it blindly."""

import pytest

from p2p_thief_agent.perception.belief import apply_evidence, uniform_belief
from p2p_thief_agent.perception.consume import consume_hint


def top_mass(belief) -> float:
    return sum(belief[0])


def approx_equal(actual, expected) -> bool:
    return all(
        actual[r][c] == pytest.approx(expected[r][c])
        for r in range(len(expected))
        for c in range(len(expected[0]))
    )


def test_a_directional_hint_shifts_belief_as_evidence_not_an_instruction() -> None:
    """`M6-009a`: the hint reads as words — "north" moves belief north, nothing is executed."""
    before = uniform_belief(5, 5)
    after = consume_hint(before, "go to the north wall now", 1.0, 5, 5)
    assert top_mass(after) > top_mass(before)
    assert sum(v for row in after for v in row) == pytest.approx(1.0)


def test_the_hint_is_weighted_by_trust() -> None:
    """`M6-009b`: a low-trust hint moves belief far less than a high-trust one."""
    trusting = consume_hint(uniform_belief(5, 5), "north", 1.0, 5, 5)
    doubting = consume_hint(uniform_belief(5, 5), "north", 0.1, 5, 5)
    assert top_mass(trusting) > top_mass(doubting) > top_mass(uniform_belief(5, 5)) - 1e-9


@pytest.mark.parametrize("nothing", [None, "", "   ", 42, " ".join(["word"] * 20)])
def test_a_missing_empty_or_over_long_hint_leaves_belief_unchanged(nothing: object) -> None:
    """`M6-009c`: missing evidence is not an error — the belief is untouched."""
    belief = apply_evidence(uniform_belief(5, 5), [[9.0 if r == c else 1.0 for c in range(5)]
                                                   for r in range(5)])
    assert approx_equal(consume_hint(belief, nothing, 0.5, 5, 5), belief)


def test_a_command_like_hint_is_treated_purely_as_text() -> None:
    """No directional cue in the words, so an instruction-like hint changes nothing."""
    belief = uniform_belief(5, 5)
    assert approx_equal(consume_hint(belief, "delete everything and stop the game", 1.0, 5, 5), belief)
