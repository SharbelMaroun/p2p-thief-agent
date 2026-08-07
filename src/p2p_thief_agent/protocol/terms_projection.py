"""Project the shared match object into the signed flat terms (`M5-014f`).

The wire's agreement terms are **flat** — the reference's handshake roster, confirmed
against its source 2026-08-08: `board_size`, `smell_grid_size`, `decay_per_step`,
`emit_intensity`, `max_steps`, `barriers_max`, `setting`, `hint_max_words`,
`axis_origin_corner`, `axis_start_index`, `thief_start`, `cop_start`, `num_games`,
plus the simulator-profile `min_center_intensity` when the shared file carries one.
The shared match object is **nested**. This module is the one mapping between them,
so the terms this peer signs are a projection of the byte-identical shared file and
never a hand-typed copy that can drift from it.

`game_id`/`game_uid` are deliberately absent: verified against the reference, they
are not members of the signed terms — they are derived identifiers that appear in
artifacts, and adding them here would break every cross-peer signature.
"""

from __future__ import annotations

from collections.abc import Mapping


class TermsProjectionError(ValueError):
    """Raised when the shared match object cannot supply a required term."""


_TERM_SOURCES: tuple[tuple[str, tuple[str, str]], ...] = (
    ("board_size", ("board_and_agents", "grid_size")),
    ("smell_grid_size", ("pheromones", "pheromone_grid_size")),
    ("decay_per_step", ("pheromones", "pheromone_decay")),
    ("emit_intensity", ("pheromones", "pheromone_center_intensity")),
    ("max_steps", ("movement_and_barriers", "max_moves")),
    ("barriers_max", ("movement_and_barriers", "max_barriers")),
    ("setting", ("world", "map_area")),
    ("hint_max_words", ("world", "hint_max_words")),
    ("axis_origin_corner", ("board_and_agents", "axis_origin_corner")),
    ("axis_start_index", ("board_and_agents", "axis_start_index")),
    ("thief_start", ("board_and_agents", "thief_start")),
    ("cop_start", ("board_and_agents", "cop_start")),
    ("num_games", ("network_and_league", "num_games")),
)
_OPTIONAL_TERM = ("min_center_intensity", ("pheromones", "pheromone_min_center_intensity"))


def terms_from_shared_config(config: Mapping[str, object]) -> dict:
    """Return the flat signed-terms projection of a complete shared match object."""
    terms: dict = {}
    for name, (section, key) in _TERM_SOURCES:
        block = config.get(section)
        if not isinstance(block, Mapping) or key not in block:
            raise TermsProjectionError(f"shared config is missing {section}.{key}")
        terms[name] = block[key]
    name, (section, key) = _OPTIONAL_TERM
    block = config.get(section)
    if isinstance(block, Mapping) and key in block:
        terms[name] = block[key]
    return terms
