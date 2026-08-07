"""The fixtures a rehearsed series is built from (`M7-018`).

Split from `rehearsal.py`, which drives the run. The seam is between *what a game is made
of* — identities, groups, real commitments, per-sub-game summaries — and *how a series is
played and reported*. Keeping them apart matters because the damage a test wants to observe
is injected here, in `steps_for`, while the pipeline that must survive it lives next door and
never learns which run it is in.

Nothing here is a test double except `RecordingTransport`. The commitments are taken with
this repository's own `commit_of`, so an audit run over them verifies something real rather
than agreeing with a fixture.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from p2p_thief_agent.protocol.crypto import commit_of
from p2p_thief_agent.reporting.naming import MatchIdentity
from p2p_thief_agent.state.scoring import Outcome

OUR_GROUP = "sharNamr"
OPPONENT = "rival"
COMMIT_HASH = "a" * 40
TOKEN_LIMIT = 200_000
HARDWARE = {"cpu_type": "x86_64", "cpu_freq_mhz": 3000, "cpu_cores": 8,
            "ram_gb": 16, "gpu_model": "none", "vram_gb": 0}
SECTIONS = {name: {"agreed": True} for name in
            ("board_and_agents", "world", "movement_and_barriers", "scoring", "pheromones",
             "network_and_league", "rate_limiter_gatekeeper")}


class RecordingTransport:
    """Stands in for Gmail. Records the call and opens nothing."""

    def __init__(self) -> None:
        self.sent: list[dict] = []

    def users(self):
        return self

    def messages(self):
        return self

    def send(self, *, userId: str, body: dict):  # noqa: N803 — the API's own parameter name
        self.sent.append({"userId": userId, "body": body})
        return self

    def execute(self):
        return {"id": f"rehearsal-{len(self.sent)}", "labelIds": ["SENT"]}


@dataclass(frozen=True)
class Rehearsal:
    """Everything one rehearsed series produced, for a test to assert against."""

    identity: MatchIdentity
    artifacts: dict[str, dict]
    written: dict[str, Path]
    settlement: dict
    tokens: dict[str, object]
    series_score: int
    transport: RecordingTransport


def group(gid: str) -> dict:
    return {"group_id": gid, "group_name": gid, "members": ["student-1", "student-2"],
            "repos": {"cop": f"https://github.com/{gid}/p2p-cop-agent",
                      "thief": f"https://github.com/{gid}/p2p-thief-agent"},
            "mcp_servers": {"peer": f"https://{gid}.example.com/mcp"},
            "llm_model": "rehearsal-local", "hardware_spec": HARDWARE, "signature": "sig"}


def steps_for(sub_game: int, *, tamper: bool = False) -> list[dict]:
    """Real commitments over real payloads, so the audit has something to verify.

    `tamper` rewrites the revealed move **after** the commitment was taken — the shape a
    falsified log actually has. Nothing about the record looks wrong on its own; only
    recomputing the digest shows the two disagree, which is what rule 19 calls a technical
    mismatch during the audit phase.
    """
    records = []
    for step in range(1, 4):
        payload = {"step": step, "move": "NESW"[step % 4], "intent": step % 2 == 0}
        nonce = f"{sub_game:016x}{step:016x}"
        digest = commit_of(payload, nonce)
        if tamper and step == 2:
            payload = {**payload, "move": "S" if payload["move"] != "S" else "N"}
        records.append({"payload": payload, "nonce": nonce, "commit": digest,
                        "hint": f"somewhere near step {step}"})
    return records


def summary_for(sub_game: int, outcome: Outcome, tokens: int) -> dict:
    """A finished sub-game's summary. `ended_at` is set because `build_log` refuses a log
    for a game still in play — every record carries its nonce (`AE-18`)."""
    return {"sub_game_number": sub_game, "group_id": OUR_GROUP, "role": "thief",
            "opponent_group_id": OPPONENT, "result": outcome.value, "winner_role": "thief",
            "steps": 3, "timezone": "Asia/Jerusalem",
            "started_at": "2026-08-07T10:00:00+03:00",
            "ended_at": "2026-08-07T10:45:00+03:00", "duration_seconds": 2700,
            "tokens_total": tokens, "audit": {"verified": True}}
