"""`M1-015`: a neutral peer that shares no source file with any agent in this project.

This module imports **nothing** from `p2p_thief_agent` — only the standard library. It
re-derives canonicalization and the commit construction from
`docs/SIM_WIRE_PROTOCOL.md` rather than calling ours, so when our sealed message verifies
here it is two implementations agreeing, not one implementation agreeing with itself.
That is the whole point: a test that drives our own client against our own server shares
the constant that a typo would live in, and the typo cancels out on both sides.

**What it copies: nothing.** `M1-015` requires a stub "sharing no source file with any
peer repository", and `THIEF-002` forbids this repository any access to the companion
Cop repository. The behaviours below were established by asking the reference-code
notebook directly and are labelled with what was found, so a later reader can re-check
them rather than trusting this docstring.

Reference behaviours modelled here (asked 2026-08-06):

* **Invalid input raises; it is never acknowledged and dropped.** The reference's tool
  handlers construct protocol dataclasses whose `from_dict` raises on a missing or
  wrongly-typed field, and FastMCP returns that to the sender as an MCP error.
* **Unknown or extra fields are ignored**, not rejected — matching the `X-02` fix in
  both of our repositories.
* **Success payloads** are `{"status": "received"}` for the turn and control channels.
* **Step ordering is NOT gated at ingestion.** A duplicate or non-advancing step stays
  queued for the peer loop; the reference does not refuse it on arrival. `strict_ordering`
  below therefore defaults to **False** so the stub behaves like a real opponent. Turning
  it on is *our* strictness and is used only to prove our own refusal path (`M1-017`).

An honest limit, recorded because it bounds what this file can prove: the stub and the
agent it tests were written by the same team in the same session. "Independently
authored" holds at the level of source files, imports and re-derived constants — it does
not achieve the strongest form, a different author entirely. The book's own standard for
interoperability evidence is a `Verified OK` replay of a real match, and Appendix E
rule 52 permits warm-up games for exactly that. This suite is a floor, not that ceiling.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

# Re-derived from docs/SIM_WIRE_PROTOCOL.md, not imported from protocol/crypto.py.
SEPARATORS = (",", ":")


def canonical(value: Any) -> str:
    """Canonical JSON: sorted keys, no spaces, non-ASCII left raw."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=SEPARATORS)


def commit_of(payload: dict[str, Any], nonce: str) -> str:
    """`SHA256(canonical(payload) + "|" + nonce)` — the nonce sits *outside*, behind a bar."""
    return hashlib.sha256(f"{canonical(payload)}|{nonce}".encode()).hexdigest()


def config_sha256(terms: Any) -> str:
    return hashlib.sha256(canonical(terms).encode()).hexdigest()


class ConformanceError(RuntimeError):
    """Raised at the peer boundary. The reference raises rather than acking and dropping."""


TURN_REQUIRED = ("step", "sender", "hint", "smell_grid", "commit", "timestamp")
TURN_OPTIONAL = ("barrier_placed", "capture_claim", "claim_response", "win_claim")
CONTROL_REQUIRED = ("kind", "sender")
AUDIT_REQUIRED = ("sender", "records", "result_claim")
RESULT_CLAIMS = frozenset({"capture", "survival", "timeout"})
# The private inference a peer must never put on the wire (Appendix E rule 2, Prohibited,
# "immediate disqualification due to data leakage").
FORBIDDEN_ON_WIRE = ("belief", "certainty", "trust", "nonce", "heatmap", "posterior")


def _require(message: object, names: tuple[str, ...], what: str) -> dict:
    if not isinstance(message, dict):
        raise ConformanceError(f"{what} must be an object, got {type(message).__name__}")
    missing = [n for n in names if n not in message]
    if missing:
        raise ConformanceError(f"{what} is missing required field(s): {', '.join(missing)}")
    return message


class NeutralPeer:
    """A minimal opponent: validates, records, and answers exactly like the reference."""

    def __init__(self, terms: dict | None = None, *, strict_ordering: bool = False) -> None:
        self.terms = terms or {}
        self.strict_ordering = strict_ordering
        self.turns: list[dict] = []
        self.audits: list[dict] = []
        self.controls: list[dict] = []

    # -- negotiate ---------------------------------------------------------------
    def negotiate(self, message: object) -> dict:
        """Verify the peer signed **the same terms** we hold; refuse to play otherwise."""
        msg = _require(message, ("identity", "terms", "nonce", "signature"), "negotiate")
        if msg["terms"] != self.terms:
            raise ConformanceError("negotiated terms differ; refusing to play")
        if commit_of(msg["terms"], msg["nonce"]) != msg["signature"]:
            raise ConformanceError("signature does not reproduce over the agreed terms")
        nonce = "0" * 32
        return {
            "identity": {"group_id": "neutral-stub"},
            "terms": self.terms,
            "nonce": nonce,
            "signature": commit_of(self.terms, nonce),
            "config_sha256": config_sha256(self.terms),
        }

    # -- receive_turn ------------------------------------------------------------
    def receive_turn(self, message: object) -> dict:
        msg = _require(message, TURN_REQUIRED, "turn")
        if not isinstance(msg["step"], int) or isinstance(msg["step"], bool):
            raise ConformanceError("step must be an integer")
        if not isinstance(msg["smell_grid"], dict):
            raise ConformanceError("smell_grid must be an object of 'r,c' -> intensity")
        leaked = [k for k in FORBIDDEN_ON_WIRE if k in msg]
        if leaked:
            raise ConformanceError(f"turn carries private state: {', '.join(leaked)}")
        if self.strict_ordering and self.turns and msg["step"] <= self.turns[-1]["step"]:
            raise ConformanceError(f"step {msg['step']} does not advance")
        self.turns.append({k: msg[k] for k in (*TURN_REQUIRED, *TURN_OPTIONAL) if k in msg})
        return {"status": "received"}

    # -- submit_audit ------------------------------------------------------------
    def submit_audit(self, payload: object) -> dict:
        data = _require(payload, AUDIT_REQUIRED, "audit")
        if data["result_claim"] not in RESULT_CLAIMS:
            raise ConformanceError(f"result_claim must be one of {sorted(RESULT_CLAIMS)}")
        for i, record in enumerate(data["records"]):
            _require(record, ("payload", "nonce", "commit"), f"audit record {i}")
            if commit_of(record["payload"], record["nonce"]) != record["commit"]:
                raise ConformanceError(f"record {i} does not reproduce its commitment")
        self.audits.append(dict(data))
        return {"status": "received", "records": len(data["records"])}

    # -- receive_control ---------------------------------------------------------
    def receive_control(self, message: object) -> dict:
        msg = _require(message, CONTROL_REQUIRED, "control")
        self.controls.append(dict(msg))
        return {"status": "received"}


TOOLS = {
    "negotiate": "message",
    "receive_turn": "message",
    "submit_audit": "payload",
    "receive_control": "message",
}
