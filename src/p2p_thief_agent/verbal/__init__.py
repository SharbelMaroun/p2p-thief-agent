"""The verbal game: natural-language hints, token-free by default (`M6-004c/d`, `M6-008`).

Kept strictly apart from movement — a hint is never a coordinate channel (`AE-27`) and the
LLM never decides a move (`AE-25`). The default provider needs no model or network.
"""

from p2p_thief_agent.verbal.generation import (
    INTENTS,
    Hint,
    generate_hint,
    landmark_hint,
)
from p2p_thief_agent.verbal.hints import (
    HINT_WORD_LIMIT,
    HintError,
    template_hint,
    validate_hint,
)
from p2p_thief_agent.verbal.providers import (
    MODEL_MODE,
    TEMPLATE_MODE,
    gated_model_provider,
)

__all__ = [
    "HINT_WORD_LIMIT",
    "INTENTS",
    "MODEL_MODE",
    "TEMPLATE_MODE",
    "Hint",
    "HintError",
    "gated_model_provider",
    "generate_hint",
    "landmark_hint",
    "template_hint",
    "validate_hint",
]
