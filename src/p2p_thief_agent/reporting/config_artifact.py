"""Agreed per-sub-game configuration artifact (`M7-002b`).

**`U-019`-PROVISIONAL** — the section layout follows the observed template in
`docs/JSON_ARTIFACT_SCHEMAS.md`, authorised pending a `U-019` ruling. It carries the
quantitative parameters (in their sections) plus the identity and the `config_sha256` lock.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from p2p_thief_agent.orchestration.series import NUM_SUB_GAMES
from p2p_thief_agent.protocol.crypto import canonical_sha256
from p2p_thief_agent.reporting.declaration import SCHEMA_VERSION, _require
from p2p_thief_agent.reporting.naming import ArtifactError, MatchIdentity

_SECTIONS = (
    "board_and_agents", "world", "movement_and_barriers", "scoring", "pheromones",
    "network_and_league", "rate_limiter_gatekeeper",
)


def build_config(
    *,
    identity: MatchIdentity,
    sub_game_number: int,
    agreed_between: Sequence[str],
    sections: Mapping[str, Mapping],
    links: Mapping,
    config_name: str,
) -> dict:
    """Assemble the agreed config artifact and lock its quantitative content (`M7-002b`)."""
    if not 1 <= sub_game_number <= NUM_SUB_GAMES:
        raise ArtifactError(f"sub_game_number must be in 1..{NUM_SUB_GAMES}, got {sub_game_number}")
    if len(agreed_between) != 2:
        raise ArtifactError("agreed_between must list exactly two group identifiers")
    _require(sections, _SECTIONS, "config sections")
    content = {name: dict(sections[name]) for name in _SECTIONS}
    return {
        "_schema": "config",
        "schema_version": SCHEMA_VERSION,
        "_note": "U-019 provisional: shape follows the documented, unauthenticated template",
        "agreed_between": list(agreed_between),
        **content,
        "game_id": identity.game_id,
        "game_uid": identity.game_uid,
        "sub_game_number": sub_game_number,
        "links": dict(links),
        "config_name": config_name,
        "config_sha256": canonical_sha256(content),  # the lock over the quantitative content
    }
