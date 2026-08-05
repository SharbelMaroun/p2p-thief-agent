"""Final result artifact — the emailed report (`M7-002d`, `M7-002f`, `M7-002g`).

**`U-019`-PROVISIONAL** — the field set follows the observed template in
`docs/JSON_ARTIFACT_SCHEMAS.md`, authorised pending a `U-019` ruling. It carries the per-group
scores and the cumulative series result; the four repository links, two per group (`AE-49`);
and each sub-game's `github_commit` and `tokens` (`AE-53`, `AE-54`).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from p2p_thief_agent.reporting.declaration import SCHEMA_VERSION, _require
from p2p_thief_agent.reporting.naming import ArtifactError, MatchIdentity

_SUBGAME_KEYS = (
    "sub_game_number", "roles", "started_at", "ended_at", "result", "winner_group",
    "tie", "github_commit", "tokens", "score", "log_files", "audit",
)
_FINAL_KEYS = (
    "total_score", "sub_games_won", "ties", "winner_group", "series_tie", "tokens_total_series",
)


def _repository_links(groups: Sequence[Mapping]) -> list[str]:
    """Collect the four repository links — two per group (`M7-002f`, `AE-49`)."""
    links = [url for group in groups for url in dict(group.get("repos", {})).values() if url]
    if len(links) != 4:
        raise ArtifactError(f"result needs four repository links (two per group), got {len(links)}")
    return links


def build_result(
    *,
    identity: MatchIdentity,
    groups: Sequence[Mapping],
    sub_games: Sequence[Mapping],
    final_result: Mapping,
    timezone: str,
    mutual_agreement: Mapping,
) -> dict:
    """Assemble the final result artifact (`M7-002d`)."""
    if len(groups) != 2:
        raise ArtifactError("a result names exactly two groups")
    repository_links = _repository_links(groups)
    for sub_game in sub_games:
        _require(sub_game, _SUBGAME_KEYS, "result sub_game")  # commit + tokens per game (M7-002g)
    _require(final_result, _FINAL_KEYS, "final_result")
    return {
        "_schema": "result",
        "schema_version": SCHEMA_VERSION,
        "report_type": "final_result",
        "game_id": identity.game_id,
        "game_uid": identity.game_uid,
        "links": {"repositories": repository_links},
        "timezone": timezone,
        "groups": [dict(group) for group in groups],
        "num_sub_games": len(sub_games),
        "sub_games": [dict(sub_game) for sub_game in sub_games],
        "final_result": dict(final_result),
        "mutual_agreement": dict(mutual_agreement),
    }
