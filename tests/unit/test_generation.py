"""`M6-008`: hint generation — intent flag, template default, landmarks, model gating."""

import pytest

from p2p_thief_agent.protocol.crypto import commit_of
from p2p_thief_agent.verbal.generation import generate_hint, landmark_hint
from p2p_thief_agent.verbal.hints import HINT_WORD_LIMIT, HintError

MAP_AREA = ["old bridge", "market square", "harbour gate"]


def test_the_default_path_is_a_validated_zero_token_template() -> None:
    """`M6-008b`/`M6-008c`: no provider, no tokens, and within the word limit."""
    hint = generate_hint(0)
    assert hint.intent == "bluff"
    assert 0 < len(hint.text.split()) <= HINT_WORD_LIMIT


def test_the_intent_flag_is_carried_and_validated() -> None:
    assert generate_hint(1, intent="truth").intent == "truth"
    with pytest.raises(HintError, match="intent must be"):
        generate_hint(1, intent="honest")


def test_the_intent_is_sealed_in_the_commitment() -> None:
    """`M6-008a`: the intent rides inside the sealed payload, so it cannot be revised."""
    truthful = {"step": 1, "hint": "keep guessing", "intent": "truth"}
    bluffing = {**truthful, "intent": "bluff"}
    nonce = "a" * 32
    assert commit_of(truthful, nonce) != commit_of(bluffing, nonce)


def test_a_landmark_hint_is_used_when_a_map_area_is_agreed() -> None:
    """`M6-008e`: the hint names a landmark, never a coordinate."""
    hint = generate_hint(0, map_area=MAP_AREA)
    assert "old bridge" in hint.text
    assert len(hint.text.split()) <= HINT_WORD_LIMIT


def test_generic_templates_are_used_when_no_map_area_is_agreed() -> None:
    empty = generate_hint(0, map_area=[])
    assert empty.text == generate_hint(0).text  # falls back to the generic template


def test_a_model_provider_runs_only_every_n_steps() -> None:
    """`M6-008f`: a paid model cannot run every turn — the gate bounds consumption."""
    calls: list[int] = []

    def provider(step: int) -> str:
        calls.append(step)
        return "the night is long and cold"

    for step in range(6):
        generate_hint(step, provider=provider, every_n_steps=3)
    assert calls == [0, 3]  # only every third step reached the model


def test_a_provider_that_encodes_coordinates_is_refused() -> None:
    """`M6-008d`: validation applies to a model's output too, not only the template."""
    with pytest.raises(HintError, match="coordinates"):
        generate_hint(0, provider=lambda _s: "meet me at 3,4", every_n_steps=1)


def test_a_non_positive_step_interval_is_rejected() -> None:
    with pytest.raises(HintError, match="every_n_steps"):
        generate_hint(0, every_n_steps=0)


def test_a_landmark_hint_stays_within_the_word_limit() -> None:
    assert len(landmark_hint(2, MAP_AREA).split()) <= HINT_WORD_LIMIT
