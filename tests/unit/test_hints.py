"""`M6-004c`/`M6-004d`: natural-language-only hints, within the word limit, zero tokens."""

import pytest

from p2p_thief_agent.verbal.hints import (
    HINT_WORD_LIMIT,
    HintError,
    template_hint,
    validate_hint,
)


def test_a_plain_natural_language_hint_passes() -> None:
    assert validate_hint("I am heading somewhere you will never look") == (
        "I am heading somewhere you will never look"
    )


def test_a_hint_over_the_word_limit_is_rejected() -> None:
    too_long = " ".join(["word"] * (HINT_WORD_LIMIT + 1))
    with pytest.raises(HintError, match="word limit"):
        validate_hint(too_long)


@pytest.mark.parametrize("coded", ["I am at 3,4", "meet me (2, 5) soon", "grid r3c4 now"])
def test_a_hint_encoding_coordinates_is_rejected(coded: str) -> None:
    """`AE-27`: the verbal channel must not carry a coordinate protocol."""
    with pytest.raises(HintError, match="coordinates"):
        validate_hint(coded)


@pytest.mark.parametrize("empty", ["", "   ", None, 7])
def test_an_empty_or_non_text_hint_is_rejected(empty: object) -> None:
    with pytest.raises(HintError, match="natural-language"):
        validate_hint(empty)


def test_the_template_provider_yields_a_legal_hint_at_zero_tokens() -> None:
    """`M6-004d`: the default provider needs no model — every template is a valid hint."""
    for step in range(10):
        hint = template_hint(step)
        assert validate_hint(hint) == hint
        assert len(hint.split()) <= HINT_WORD_LIMIT


def test_the_template_provider_is_deterministic_in_the_step() -> None:
    assert template_hint(3) == template_hint(3)


def test_generation_enforces_the_word_limit() -> None:
    """`M6-008c`: the limit is enforced where the hint is made, not only where it is read."""
    with pytest.raises(HintError, match="word limit"):
        template_hint(0, max_words=2)
