"""Pre-game Step-0 attestation ordering (`M4-006c`, `AE-024`).

Appendix E rule 24 requires the host / code / token attestation to be sealed **before
the first move**. This guard makes that ordering checkable: given a peer's ordered
sealed records, it refuses any move (step >= 1) that appears before the step-0
``system_spec`` record. A move that slips ahead of the attestation is the exact defect
the rule exists to catch, so it raises rather than passing quietly.

The check is pure and transport-free — it reads the sealed ledger this peer already
keeps, so it works over any carrier and in a replay.
"""

from __future__ import annotations

from collections.abc import Iterable


class AttestationError(RuntimeError):
    """Raised when a move is sealed before the step-0 attestation (`AE-024`)."""


def is_attestation(record: dict) -> bool:
    """Return whether a sealed record is the step-0 system-spec attestation."""
    payload = record.get("payload", {})
    return payload.get("step") == 0 and payload.get("type") == "system_spec"


def require_pregame_attestation(records: Iterable[dict]) -> None:
    """Raise unless the step-0 attestation precedes every sealed move.

    Records are read in order. The first attestation flips the gate open; a move seen
    before that raises ``AttestationError`` naming the offending step.
    """
    attested = False
    for record in records:
        if is_attestation(record):
            attested = True
            continue
        step = record.get("payload", {}).get("step")
        if isinstance(step, int) and not isinstance(step, bool) and step >= 1 and not attested:
            raise AttestationError(
                f"step {step} sealed before the step-0 attestation (AE-024)"
            )
