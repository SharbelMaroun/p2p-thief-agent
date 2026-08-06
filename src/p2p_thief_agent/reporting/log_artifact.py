"""Per-sub-game log artifact (`M7-002c`).

**`U-019`-PROVISIONAL** — the field set follows the observed template in
`docs/JSON_ARTIFACT_SCHEMAS.md`, authorised pending a `U-019` ruling. It carries the
step-by-step commit-reveal records — each with its `payload`, `nonce`, and `commit` — so a
third party can recompute every commitment (`M7-022`).

**Why the end time is checked before anything is assembled** (`M7-022b`). Every record here
carries its nonce, and rule 18 keeps nonces secret until the end of the game — sanction
"disqualification due to the possibility of a dictionary attack". A finished log is
byte-identical whether it was written at the end or leaked at step one, so no later check
can tell the difference. Refusing to *build* the artifact while the summary has no
`ended_at` is the only place the rule can be enforced at all.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from p2p_thief_agent.reporting.declaration import SCHEMA_VERSION, _require
from p2p_thief_agent.reporting.naming import ArtifactError, MatchIdentity

_SUMMARY_KEYS = (
    "sub_game_number", "group_id", "role", "opponent_group_id", "result", "winner_role",
    "steps", "timezone", "started_at", "ended_at", "duration_seconds", "tokens_total", "audit",
)
_RECORD_KEYS = ("payload", "nonce", "commit")
_MUTUAL_KEYS = ("opponent_group_id", "sha256", "confirmed")


def build_log(
    *,
    identity: MatchIdentity,
    summary: Mapping,
    records: Sequence[Mapping],
    mutual_agreement: Mapping,
    links: Mapping,
) -> dict:
    """Assemble the per-sub-game log artifact (`M7-002c`)."""
    _require(summary, _SUMMARY_KEYS, "log summary")
    if not summary.get("ended_at"):
        raise ArtifactError(
            "a log summary with no end time describes a game still in play, and every "
            "record here carries its nonce; rule 18 keeps nonces secret until the end of "
            "the game, so this artifact must not be built yet [AE-18]")
    if not records:
        raise ArtifactError("a game log must carry at least one step record")
    for record in records:
        _require(record, _RECORD_KEYS, "log record")
    _require(mutual_agreement, _MUTUAL_KEYS, "mutual_agreement")
    return {
        "_schema": "log",
        "schema_version": SCHEMA_VERSION,
        "game_id": identity.game_id,
        "game_uid": identity.game_uid,
        "links": dict(links),
        "summary": dict(summary),
        "records": [dict(record) for record in records],
        "mutual_agreement": dict(mutual_agreement),
    }
