"""Zero-token template hints, natural-language only and within the word limit (`M6-004c/d`).

The verbal game is mandatory (`AE-26`) but must never require tokens: a whole series has to
be playable at zero cost (`AF-t21`), so the **default** hint provider is a template that
needs no model, no account, and no network. `validate_hint` is the gate every hint passes —
a hint must be non-empty natural language, within the agreed word limit (`hint_max_words`,
default 15 `[AF-t14]`), and must **not** encode coordinates: `AE-27` forbids a `"r,c"`
side-channel, so the verbal layer stays a channel a person could read, not a data bus.

Richer generation — the truth/bluff intent flag, an every-N-steps model provider — is
`M6-008`, which reuses this validator and this default provider.
"""

from __future__ import annotations

import re

# Appendix F table 14 default; the agreed `hint_max_words` overrides it at negotiation.
HINT_WORD_LIMIT = 15

# A numeric coordinate pair — the side-channel `AE-27` forbids. "(3, 4)" is caught too,
# since it contains "3, 4"; "r3c4" is the other common grid shorthand.
_COORDINATE = re.compile(r"\d+\s*,\s*\d+|\br\d+c\d+\b", re.IGNORECASE)

# Deterministic zero-token templates: natural-language taunts that reveal nothing, so the
# default reader (`decode_hint`) gets no directional cue and the hint costs the game nothing.
_TEMPLATES = (
    "You will not catch me this time, officer.",
    "I am always one step ahead of you.",
    "Keep guessing, you are colder than you think.",
    "The shadows here hide me well tonight.",
    "Chase all you like, the streets are mine.",
)


class HintError(ValueError):
    """Raised when a hint is empty, over the word limit, or encodes coordinates."""


def validate_hint(text: object, max_words: int = HINT_WORD_LIMIT) -> str:
    """Return the hint unchanged, or raise naming exactly why it is not a legal hint."""
    if not isinstance(text, str) or not text.strip():
        raise HintError("a hint must be non-empty natural-language text")
    word_count = len(text.split())
    if word_count > max_words:
        raise HintError(f"hint exceeds the {max_words}-word limit ({word_count} words)")
    if _COORDINATE.search(text):
        raise HintError("a hint must not encode coordinates (AE-27)")
    return text


def template_hint(step: int, max_words: int = HINT_WORD_LIMIT) -> str:
    """Return a validated zero-token natural-language hint for a step — no model, no network.

    Deterministic in ``step`` so a replay reproduces it, and validated at generation time so
    the word limit is enforced where the hint is made, not only where it is read (`M6-008c`).
    """
    return validate_hint(_TEMPLATES[step % len(_TEMPLATES)], max_words)
