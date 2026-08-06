"""A log as a stranger's toolchain would emit it — the fixture `M8-012` turns on.

Deliberately imports nothing from `p2p_thief_agent`. It hashes with a hand-written
expression and emits a differently-shaped document (an unknown `schema_version`, keys we
never write, `sub_game` instead of `sub_game_number`). If our canonical encoding,
separator, or argument order ever drifts, every test built on this fails — which is the
point, because at the audit table the opponent's encoder is the one that will not move.

Not a test module: pytest collects `test_*.py`, so this is imported, never run.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def foreign_writer(steps: int = 5, *, game: str = "rival-vs-us") -> dict:
    """Build a complete, honest, revealed log without touching any of our code."""
    records = []
    for step in range(1, steps + 1):
        nonce = f"{step:032x}"
        payload = {"intent": step % 2 == 0, "move": "NSEW"[step % 4], "step": step}
        canonical = json.dumps(
            payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        )
        records.append({
            "commit": hashlib.sha256(f"{canonical}|{nonce}".encode()).hexdigest(),
            "move": payload["move"], "nonce": nonce, "payload": payload,
            "sender": "police", "step": step,
            "their_own_extra_field": "a key we do not emit",
        })
    return {"_schema": "game-log", "schema_version": "9.9", "game_id": game,
            "sub_game": 2, "records": records, "sections_we_never_write": {"x": 1}}


def write_foreign_log(tmp_path: Path, document: dict, name: str = "log_rival_g02.json") -> Path:
    """Put the document on disk the way an opponent's repository would hand it to us."""
    path = tmp_path / name
    path.write_text(json.dumps(document), "utf-8")
    return path
