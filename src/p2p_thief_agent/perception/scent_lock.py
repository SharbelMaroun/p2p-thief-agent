"""Lock the scent model to a hash both peers must match before play (`M6-005`, `AE-23`).

Appendix E rule 23 makes a scent-model deviation cancel the game, so both peers must run
byte-identical emission and decay. The three FIXED parameters (centre, decay, field size)
are already compared as agreed terms — but the **formula** and the **radial emission
profile** are not on the wire, so two peers could share the parameters yet emit different
fields. This module canonicalises the whole model — formula, constants, field size, and the
full book-Figure-4 profile including the `U-025` provisional — into one record and hashes it
with the same `canonical_sha256` the config and commitments use, so the lock is
byte-comparable.

`with_scent_lock` stamps that hash into a match's agreed terms; from there the ordinary
agreement gate (`protocol/agreement.accept_offer`) compares it and refuses **by name** on
any mismatch, before the first move (`M6-005b`). The locked formula follows the corrected
reading — at ρ = 0.10 the factor `(1 − ρ)` *retains* 90% of prior scent; the book's p.43
"reduced by 90%" and p.46 saturation prose are arithmetic errors (`C-014`, `C-015`) and are
not implemented (`M6-005c`).
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_thief_agent.perception.scent import (
    _CONFIRMED_EMISSION,
    _PROVISIONAL_D2_5,
    DECAY_RATE,
    EMISSION_CENTER,
    FIELD_SIZE,
)
from p2p_thief_agent.protocol.crypto import canonical_sha256

# The agreed-terms key the lock rides in, so the config signature covers it.
SCENT_MODEL_TERM = "scent_model_hash"


def scent_model_record() -> dict:
    """Return the canonical description of the confirmed scent model (`M6-005a`).

    One record carries the formula, the FIXED constants, the field size, and the emission
    profile keyed by squared distance — including the `U-025` provisional, so a later ruling
    on those eight cells changes the lock and forces both peers to re-agree.
    """
    profile = {str(distance): value for distance, value in _CONFIRMED_EMISSION.items()}
    profile["5"] = _PROVISIONAL_D2_5
    return {
        "model": "multiplicative-decay",
        "update": "tau_next = max(0, (1 - decay_per_step) * tau + emission)",
        "center_intensity": EMISSION_CENTER,
        "decay_per_step": DECAY_RATE,
        "field_size": FIELD_SIZE,
        "emission_profile_by_squared_distance": profile,
    }


def scent_model_hash() -> str:
    """Return the SHA-256 lock over the canonical scent-model record."""
    return canonical_sha256(scent_model_record())


def with_scent_lock(terms: Mapping) -> dict:
    """Return the agreed terms with the scent-model lock stamped in (`M6-005b`).

    A peer running a different emission profile or formula produces a different hash, so the
    agreement gate names `scent_model_hash` as the differing term and refuses the match.
    """
    return {**dict(terms), SCENT_MODEL_TERM: scent_model_hash()}


class ScentLockError(ValueError):
    """Raised when the running scent model does not match the model locked at negotiation."""


def assert_scent_locked(agreed_hash: object) -> None:
    """Runtime check: the running scent model must still match the locked hash (`M6-022`).

    Recomputes the model hash from the code that will actually emit and observe, and compares
    it to the hash agreed at negotiation. Called at sub-game start (where the agreed terms
    hold `scent_model_hash`), so a code change that drifts this peer's physics from the agreed
    model fails loudly here rather than silently emitting fields the opponent's audit would
    reject (`AE-23`).
    """
    running = scent_model_hash()
    if running != agreed_hash:
        raise ScentLockError(
            f"running scent model {running} does not match the locked model {agreed_hash!r}"
        )
