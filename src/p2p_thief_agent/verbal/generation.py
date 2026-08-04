"""Generate a hint each turn, with a truth/bluff intent the commitment seals (`M6-008`).

Reuses `verbal/hints` for validation and the zero-token template default, and adds the three
generation-side concerns:

- **the intent flag (`M6-008a`)** — every hint carries whether it is meant as truth or a
  bluff. The caller seals that flag inside the step commitment, so it cannot be revised after
  the fact: changing the intent changes the hash;
- **landmark hints (`M6-008e`)** — when a map area is agreed, the hint references a named
  landmark rather than coordinates; with no map area it falls back to a generic template;
- **the every-N-steps gate (`M6-008f`)** — an optional model provider is invoked only on
  every Nth step, so a paid model cannot run every turn. Whatever a provider returns is still
  validated, so a model that tries to encode coordinates or overrun the limit is refused
  (`M6-008c`, `M6-008d`).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from p2p_thief_agent.verbal.hints import (
    HINT_WORD_LIMIT,
    HintError,
    template_hint,
    validate_hint,
)

INTENTS = ("truth", "bluff")

# A model provider maps a step to a candidate hint string. Optional — the default path uses
# no provider and therefore no tokens.
Provider = Callable[[int], str]

_LANDMARK_PHRASES = (
    "Somewhere near the {place}, good luck to you.",
    "The {place} keeps my secrets well tonight.",
    "Try the {place}, or waste your evening.",
)


@dataclass(frozen=True, slots=True)
class Hint:
    """A generated hint and the intent the commitment will seal (`M6-008a`)."""

    text: str
    intent: str


def landmark_hint(step: int, map_area: Sequence[str], max_words: int = HINT_WORD_LIMIT) -> str:
    """Return a validated landmark hint for an agreed map area (`M6-008e`)."""
    place = map_area[step % len(map_area)]
    phrase = _LANDMARK_PHRASES[step % len(_LANDMARK_PHRASES)].format(place=place)
    return validate_hint(phrase, max_words)


def generate_hint(
    step: int,
    *,
    intent: str = "bluff",
    map_area: Sequence[str] | None = None,
    provider: Provider | None = None,
    every_n_steps: int = 1,
    max_words: int = HINT_WORD_LIMIT,
) -> Hint:
    """Produce this turn's hint and its sealed intent, token-free by default (`M6-008b`).

    The model ``provider``, when given, runs only on every ``every_n_steps``-th step; every
    other step — and every step at all when no provider is given — uses a landmark hint if a
    ``map_area`` is agreed, else a generic template. All paths are validated.
    """
    if intent not in INTENTS:
        raise HintError(f"intent must be one of {INTENTS}, got {intent!r}")
    if every_n_steps < 1:
        raise HintError(f"every_n_steps must be at least 1, got {every_n_steps}")
    if provider is not None and step % every_n_steps == 0:
        text = validate_hint(provider(step), max_words)
    elif map_area:
        text = landmark_hint(step, map_area, max_words)
    else:
        text = template_hint(step, max_words)
    return Hint(text=text, intent=intent)
