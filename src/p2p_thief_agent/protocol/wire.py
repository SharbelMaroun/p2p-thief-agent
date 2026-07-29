"""Simulator-conformant peer-to-peer wire messages (envelope-free).

Independently authored to match the reference simulator's `domain/protocol.py` wire
contract (`Game-P2P-Cop-Chase`) for cross-agent interoperability: the `TurnMessage` a
mover sends its opponent, the `ControlMessage` on the opt-in control channel, and the
end-of-game `AuditPayload`. No Option-B envelope wraps these -- the tool argument *is*
the message dict. True position/move/verdict are sealed in `commit` and revealed only at
the audit, so they never appear in the clear here.

`from_dict` mirrors the simulator's own strictness per type: turn and audit messages
reject unknown fields, while control messages ignore unrecognized keys.
"""

from __future__ import annotations

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


def _reject_unknown(data: dict, allowed: set[str], label: str) -> None:
    unknown = set(data) - allowed
    if unknown:
        raise WireError(f"{label} unknown fields: {sorted(unknown)}")


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
        _reject_unknown(record, {f.name for f in fields(cls)}, "TurnMessage")
        return cls(**record)


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

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: object) -> ControlMessage:
        record = _require_object(data, "ControlMessage")
        _require_fields(record, ("kind", "sender"), "ControlMessage")
        allowed = {f.name for f in fields(cls)}
        return cls(**{key: value for key, value in record.items() if key in allowed})


@dataclass(slots=True)
class AuditPayload:
    """End-of-game reveal: full sealed records for the opponent to re-verify."""

    sender: str
    records: list
    result_claim: str

    def __post_init__(self) -> None:
        if self.sender not in ROLES:
            raise WireError("AuditPayload.sender must be 'thief' or 'police'")
        if self.result_claim not in RESULT_CLAIMS:
            raise WireError("AuditPayload.result_claim must be capture/survival/timeout")
        if not isinstance(self.records, list):
            raise WireError("AuditPayload.records must be an array")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: object) -> AuditPayload:
        record = _require_object(data, "AuditPayload")
        _require_fields(record, ("sender", "records", "result_claim"), "AuditPayload")
        _reject_unknown(record, {f.name for f in fields(cls)}, "AuditPayload")
        return cls(**record)
