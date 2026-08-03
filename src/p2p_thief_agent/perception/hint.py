"""Decode a natural-language hint into belief-space evidence (`M6-003e`).

The opponent's hint is free text that may be truthful or a bluff. We read it as a claim
about **where the Cop is or is heading**, and decode it into a likelihood over the grid.

Two rules are load-bearing. It is **deterministic pure Python**, so the belief it feeds may
drive the move without the LLM ever touching a movement decision (`AE-25`). And it uses
only common **directional vocabulary** — never an agreed `"r,c"` coordinate protocol
(`AE-27`): a hint decodes through the same words a person would use, so no side-channel
coordinate scheme is possible.

A hint with no recognised cue, or an empty/absent one, yields a **uniform** likelihood —
missing evidence is not an error (`M6-003c`, `M6-009c`).
"""

from __future__ import annotations

import re

from p2p_thief_agent.perception.belief import BeliefError, Grid, normalize, uniform_belief

_WORD = re.compile(r"[a-z]+")


def _north(row: int, _col: int, rows: int, _cols: int) -> float:
    return float(rows - row)  # largest at row 0 (the top)


def _south(row: int, _col: int, _rows: int, _cols: int) -> float:
    return float(row + 1)


def _east(_row: int, col: int, _rows: int, _cols: int) -> float:
    return float(col + 1)


def _west(_row: int, col: int, _rows: int, cols: int) -> float:
    return float(cols - col)


def _center(row: int, col: int, rows: int, cols: int) -> float:
    return 1.0 / (1.0 + abs(row - (rows - 1) / 2) + abs(col - (cols - 1) / 2))


def _corner(row: int, col: int, rows: int, cols: int) -> float:
    return 1.0 / (1.0 + min(row, rows - 1 - row) + min(col, cols - 1 - col))


# Common directional vocabulary → a per-cell gradient. Synonyms share a function, and a
# `set` of the matched functions dedupes them so "north"/"up"/"top" count once.
_CUES = {
    "north": _north, "up": _north, "top": _north, "upper": _north, "above": _north,
    "south": _south, "down": _south, "bottom": _south, "lower": _south, "below": _south,
    "east": _east, "right": _east,
    "west": _west, "left": _west,
    "center": _center, "centre": _center, "middle": _center, "central": _center,
    "corner": _corner, "corners": _corner,
}


def decode_hint(text: object, rows: int, cols: int) -> Grid:
    """Turn a free-text hint into a likelihood over the `rows×cols` grid.

    Recognised directional cues multiply into a gradient that is then normalised; an
    unrecognised, empty, or non-string hint decodes to a uniform likelihood, so a missing
    or opaque hint simply carries no information rather than raising.
    """
    if rows < 1 or cols < 1:
        raise BeliefError(f"belief grid must be at least 1x1, got {rows}x{cols}")
    words = set(_WORD.findall(text.lower())) if isinstance(text, str) else set()
    gradients = {_CUES[word] for word in words if word in _CUES}
    if not gradients:
        return uniform_belief(rows, cols)
    weights = [
        [_weight(gradients, row, col, rows, cols) for col in range(cols)]
        for row in range(rows)
    ]
    return normalize(weights)


def _weight(gradients: set, row: int, col: int, rows: int, cols: int) -> float:
    product = 1.0
    for gradient in gradients:
        product *= gradient(row, col, rows, cols)
    return product
