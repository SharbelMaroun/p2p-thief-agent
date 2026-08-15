"""Simulator-conformant peer-to-peer wire messages (envelope-free).

Independently authored to match the reference simulator's `domain/protocol.py` wire
contract (`Game-P2P-Cop-Chase`) for cross-agent interoperability: the `TurnMessage` a
mover sends its opponent, the `ControlMessage` on the opt-in control channel, and the
end-of-game `AuditPayload`. No Option-B envelope wraps these -- the tool argument *is*
the message dict. True position/move/verdict are sealed in `commit` and revealed only at
the audit, so they never appear in the clear here.

**Unknown fields are ignored on every message type (corrected 2026-08-06).** This module
previously rejected them on turn and audit messages, on the stated grounds that it
"mirrors the simulator's own strictness per type". That was wrong twice over. Asked
directly, the reference **ignores extra or unknown fields** when building `TurnMessage`,
`ControlMessage` *and* `AuditPayload` -- the strictness it does have is about **missing
required** fields, which still raise. And the rejection was silently fatal for us: a
refused turn is consumed and skipped by the poller, so a peer sending one unmodelled key
made this agent go quiet until the deadline, reading as a dropped network connection
rather than as our own refusal, and costing a technical loss.

It also disagreed with the companion Cop peer, whose schema tolerates extra members. Two
implementations from one team behaving differently on the same message is the defect,
independently of which behaviour is right.

Being liberal here cannot break us -- it only ever accepts more -- while being strict can
lose a decided game. That is the same "strict in what we send, generous in what we
accept" rule already applied to acknowledgements. Missing *required* fields and invalid
*values* are still refused, because those we genuinely cannot act on.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, fields

ROLES = ("thief", "police")
RESULT_CLAIMS = ("capture", "survival", "timeout")
CONTROL_KINDS = ("enable", "status", "restart", "quit")


class WireError(ValueError):
    """Raised when a wire message is missing a field or carries an invalid value."""


def _require_object(data: object, label: str) -> dict:
    if not isinstance(data, dict):
        raise WireError(f"{label} must be an object")
    return data


def _require_fields(data: dict, names: tuple[str, ...], label: str) -> None:
    missing = [name for name in names if name not in data]
    if missing:
        raise WireError(f"{label} missing fields: {sorted(missing)}")


def _known_only(data: dict, allowed: set[str]) -> dict:
    """Return only the fields this message models, dropping any extras.

    Tolerating an unmodelled key costs nothing: it cannot reach any behaviour, because
    the dataclass never sees it. Refusing one costs a game.
    """
    return {key: value for key, value in data.items() if key in allowed}


@dataclass(slots=True)
class TurnMessage:
    """One peer's public turn: hint, scent, and the sealed commit (no cleartext truth)."""

    step: int
    sender: str
    hint: str
    smell_grid: dict
    commit: str
    timestamp: str
    barrier_placed: list | None = None
    capture_claim: list | None = None
    claim_response: dict | None = None
    win_claim: dict | None = None

    def __post_init__(self) -> None:
        if self.sender not in ROLES:
            raise WireError("TurnMessage.sender must be 'thief' or 'police'")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: object) -> TurnMessage:
        record = _require_object(data, "TurnMessage")
        _require_fields(
            record, ("step", "sender", "hint", "smell_grid", "commit", "timestamp"), "TurnMessage"
        )
        return cls(**_known_only(record, {f.name for f in fields(cls)}))


@dataclass(slots=True)
class ControlMessage:
    """Opt-in control-channel signal; not part of the sealed game record."""

    kind: str
    sender: str
    sub_game_number: int = 1
    status: str = ""
    step_budget: float = 0.0
    payload: dict | None = None

    def __post_init__(self) -> None:
        if self.sender not in ROLES:
            raise WireError("ControlMessage.sender must be 'thief' or 'police'")
        # `CONTROL_KINDS` was declared and never enforced — found 2026-08-07 by `M8-004a`'s
        # field sweep. An unrecognised kind reached the phase machine as a string nobody
        # handled, and rule 5 (Mandatory) makes an illegal state transition "a logical
        # error leading to loss". `TurnMessage` validated its `sender` from the start; this
        # class simply never got the matching check.
        if self.kind not in CONTROL_KINDS:
            raise WireError(
                f"ControlMessage.kind must be one of {CONTROL_KINDS}, got {self.kind!r}")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: object) -> ControlMessage:
        record = _require_object(data, "ControlMessage")
        _require_fields(record, ("kind", "sender"), "ControlMessage")
        return cls(**_known_only(record, {f.name for f in fields(cls)}))


@dataclass(slots=True)
class AuditPayload:
    """End-of-game reveal: full sealed records for the opponent to re-verify."""

    sender: str
    records: list
    result_claim: str | dict

    def __post_init__(self) -> None:
        if self.sender not in ROLES:
            raise WireError("AuditPayload.sender must be 'thief' or 'police'")
        # A STRUCTURED claim is tolerated (`C-048`). Group `yanell11` send
        # `{"type": "technical_loss", "violator": ..., "how": ...}` -- an object, not one
        # of our enum strings -- and refusing it meant we rejected the very message that
        # told us why they were refusing us. Our own report then disagreed with theirs,
        # which is rule 35's conflicting-report 0/0 arriving on top of whatever the
        # original dispute was. The object form is READ, never emitted: we still send a
        # plain string, and a claim of any shape is an assertion to be judged on evidence,
        # never believed. Fourth tolerance of this family after `C-033`/`C-037` and the
        # companion's identity refusal.
        claim = self.result_claim
        if isinstance(claim, Mapping):
            if not str(claim.get("type") or "").strip():
                raise WireError("a structured result_claim must carry a non-empty 'type'")
        elif claim == "series_consensus":
            # companion C-040: uoh-ay26's post-series SHA exchange -- an empty-record
            # envelope, never a game outcome. A non-empty record list under that claim is
            # still malformed, because a consensus that smuggles records is not one.
            if self.records:
                raise WireError("series_consensus must carry no records")
        elif claim not in RESULT_CLAIMS:
            raise WireError(
                "AuditPayload.result_claim must be capture/survival/timeout, "
                "series_consensus, or an object carrying a 'type'")
        if not isinstance(self.records, list):
            raise WireError("AuditPayload.records must be an array")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: object) -> AuditPayload:
        record = _require_object(data, "AuditPayload")
        _require_fields(record, ("sender", "records", "result_claim"), "AuditPayload")
        return cls(**_known_only(record, {f.name for f in fields(cls)}))
