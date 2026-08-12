"""Write the finished local-match log artifact (`M9-026`).

Extracted from `serve.py` at the file-length gate. One integrity rule lives here and
is the reason the module carries a test hook rather than prose only: the winner
follows the outcome. This used to hard-code `"winner_role": "thief"`, which wrote a
false claim into a signed artifact whenever we were captured — and an artifact that
lies is the one thing rule 19's audit exists to catch, including ours.
"""

from __future__ import annotations

from datetime import UTC
from pathlib import Path

# Outcome value -> the role the scoring table pays as the winner of that outcome.
WINNER_BY_OUTCOME = {"survival": "thief", "capture": "police"}


def write_match_log(directory: Path, records: list[dict], result: object,
                    context: dict | None = None) -> Path:
    """Write the finished sub-game log, with the end time rule 18's guard requires.

    ``context`` carries what negotiation actually established — the derived game
    identity, our and the opponent's group ids, the config lock, the true start time
    and sub-game number. A negotiated match writes those; only an un-negotiated local
    drill falls back to the clearly-labelled placeholders, because a counted game's
    artifact naming a placeholder opponent is a false record wearing a valid schema.
    """
    from datetime import datetime  # noqa: PLC0415

    from p2p_thief_agent.reporting.emit import write_artifact  # noqa: PLC0415
    from p2p_thief_agent.reporting.log_artifact import build_log  # noqa: PLC0415
    from p2p_thief_agent.reporting.naming import MatchIdentity, log_filename  # noqa: PLC0415

    context = context or {}
    ended = datetime.now(UTC).isoformat()
    identity = MatchIdentity(game_id=context.get("game_id", "local-match"),
                             game_uid=context.get("game_uid", "local-match-uid"))
    sub_game = int(context.get("sub_game", 1))
    outcome = getattr(getattr(result, "outcome", None), "value", "unknown")
    summary = {
        "sub_game_number": sub_game,
        "group_id": context.get("group_id", "sharNamr"), "role": "thief",
        "opponent_group_id": context.get("opponent_group_id", "opponent"),
        "result": outcome,
        "winner_role": WINNER_BY_OUTCOME.get(outcome, "unknown"),
        "steps": getattr(result, "steps", 0),
        "timezone": "UTC", "started_at": context.get("started_at") or ended,
        "ended_at": ended,
        "duration_seconds": 0, "tokens_total": 0, "audit": {},
        # Rule 53 per game, per team (inst/:1295): recorded at write time so the
        # series report can carry it without reconstruction (companion C-043).
        "github_commit": dict(context.get("github_commit") or {}),
    }
    artifact = build_log(
        identity=identity, summary=summary, links={},
        mutual_agreement={
            "opponent_group_id": context.get("opponent_group_id", "opponent"),
            "sha256": context.get("config_sha256", "0" * 64),
            "confirmed": bool(context.get("confirmed", False)),
        },
        records=records,
    )
    return write_artifact(Path(directory), log_filename(identity.game_id, sub_game), artifact)
