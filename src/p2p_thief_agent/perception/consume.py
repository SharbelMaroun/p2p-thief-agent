"""Consume an inbound hint into belief — weighted by trust, never trusted blindly (`M6-009`).

This is the inbound counterpart to `verbal/generation`. An opponent's hint is **evidence,
never an instruction** (`M6-009a`): it is decoded by extracting directional words, never
executed, so a hint that reads like a command changes belief only as far as the words it
contains, and does nothing else. The decoded likelihood is tempered by the sender's running
trust before it touches belief (`M6-009b`), so a peer that keeps lying moves the belief less
and less. And a missing, empty, over-long, or non-text hint is **not an error** (`M6-009c`):
it simply carries no information, leaving the belief unchanged.
"""

from __future__ import annotations

from p2p_thief_agent.perception.belief import Grid, apply_evidence, uniform_belief
from p2p_thief_agent.perception.hint import decode_hint
from p2p_thief_agent.perception.trust import trust_weighted

# Appendix F table 14 default; the agreed `hint_max_words` overrides via `max_words`. An
# inbound hint longer than this is treated as no evidence rather than rejected — inbound
# leniency, matching the acknowledgement decision, cannot break this peer.
DEFAULT_HINT_WORD_LIMIT = 15


def consume_hint(
    belief: Grid,
    text: object,
    trust: float,
    rows: int,
    cols: int,
    *,
    max_words: int = DEFAULT_HINT_WORD_LIMIT,
) -> Grid:
    """Return the belief updated by an inbound hint, weighted by trust.

    A well-formed hint within the word limit is decoded to a likelihood and applied at its
    trust-tempered strength; anything else (absent, non-text, or over-long) contributes a
    uniform likelihood, which leaves the belief unchanged.
    """
    if isinstance(text, str) and len(text.split()) <= max_words:
        likelihood = decode_hint(text, rows, cols)
    else:
        likelihood = uniform_belief(rows, cols)
    return apply_evidence(belief, trust_weighted(likelihood, trust))
