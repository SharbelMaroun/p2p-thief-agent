"""Persist the opponent's verified audit beside our own log (companion `C-051`).

Their audit is the only record of where their agent actually was, and it arrives
cryptographically bound: every revealed payload must reproduce the commitment it was
sealed under, or `submit_audit` refuses it. By the time it reaches this module it has
already passed that check.

**Why keeping it is not optional.** Until 2026-08-15 both peers verified an opponent's
audit and discarded it, recording that it passed and nothing about what it said. Playing
`yanell11` that day their Cop claimed a capture at ``[0,5]`` while our own sealed record
put us at ``[0,4]``; their revealed positions would have settled it outright, and they had
passed through our verifier minutes earlier. We had to ask the opponent for evidence we
had held in memory and dropped.

Appendix E rule 19 is an iron rule with no appeal, and a technical dispute is decided on
what each side can produce. A peer that keeps only verdicts is a peer that must take its
opponent's word -- which is precisely the posture Zero-Trust exists to avoid.

Written as its own artifact rather than folded into the log, because the log is *ours*:
it carries what we sealed and is what an opponent audits. Mixing their revealed records
into it would blur whose claim is whose at exactly the moment that distinction matters.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path


def retain_opponent_audit(
    directory: Path | None,
    *,
    game_id: str,
    sub_game: int,
    audits: Sequence[dict],
    opponent_group_id: str = "",
) -> None:
    """Write the opponent's audit, reporting rather than raising on failure.

    The guard belongs with the writer rather than at the call site: this is secondary
    evidence, and the log **is** the game. The same lesson was learned live on
    2026-08-13, when a pre-game artifact raised before the log was written and a played,
    audited sub-game left no record on our side at all. Evidence that fails to save must
    never take the record of the game down with it.
    """
    if directory is None:
        return
    try:
        written = write_opponent_audit(
            directory, game_id=game_id, sub_game=sub_game, audits=audits,
            opponent_group_id=opponent_group_id,
        )
    except Exception as exc:  # noqa: BLE001 - secondary evidence, never fatal
        print(f"opponent audit not retained (log already written): {exc}")
        return
    if written is not None:
        print(f"opponent audit retained: {written.name}")


def write_opponent_audit(
    directory: Path,
    *,
    game_id: str,
    sub_game: int,
    audits: Sequence[dict],
    opponent_group_id: str = "",
) -> Path | None:
    """Write the opponent's verified audit payloads; return the path, or None if none.

    Returning ``None`` on an empty list is deliberate: a sub-game whose opponent never
    audited is a real and different situation from one that did, and writing an empty file
    would make the two indistinguishable on disk.
    """
    if not audits:
        return None
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"opponent_audit_{game_id}_g{sub_game:02d}.json"
    document = {
        "_schema": "opponent-audit",
        "game_id": game_id,
        "sub_game_number": sub_game,
        "opponent_group_id": opponent_group_id,
        "_note": (
            "The opponent's revealed audit payloads, exactly as received, after our "
            "verifier confirmed every commitment reproduces. Retained as evidence: "
            "these records fix where their agent actually was, which a capture claim "
            "alone does not (C-051)."
        ),
        "audits": [dict(audit) for audit in audits],
    }
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
