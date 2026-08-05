"""Lock the scent model to a hash both peers must match before play (`M6-005`, `AE-23`).

Appendix E rule 23 verbatim: *"Lock the cryptographic hash of the scent model before the
start of the game. Sanction: Deviation from the formula cancels the game."* The book's
boxed section (PDF p.31, `inst/police_thief_p2p_Summary.md:1043-1048`) gives the method:
the parties agree the emission and decay model, verify they **interpret it identically**
against a concrete numerical example, then lock the agreement with a SHA-256 hash so any
later deviation is immediately detectable. It also *recommends* — not mandates —
exchanging the scent mechanism's source code.

The three FIXED parameters (centre, decay, field size) are already compared as agreed
terms, and comparing them is **not enough**: two peers can hold identical constants and
still emit different fields, because the **formula** and the **radial profile** never
cross the wire on their own. That is exactly where `U-025` sits — the eight cells at
squared distance 5 have no book value, so absent a lock each peer picks one privately.

So the whole model — formula, constants, field size, and the complete 25-cell profile
including the negotiated ring — canonicalises into one record and hashes with the same
`canonical_sha256` the config and commitments use.

**The record shape is the interop contract.** Its member names are what let two
independently written peers reach the same digest; changing a key is a contract
revision, not a refactor.

**Tolerate omission, refuse a mismatch.** We always publish our lock. A peer that
publishes none is still played: the pinned simulator carries no standalone scent hash,
folding its pheromone terms into `config_sha256` instead, so requiring one would refuse
every simulator-built classmate — and rule 23 sanctions a *deviation*, not a silence. A
peer that publishes a **different** lock is refused before the first move, because that
is the deviation rule 23 cancels the game for.

The locked formula follows the corrected reading — at ρ = 0.10 the factor `(1 − ρ)`
*retains* 90% of prior scent; the book's p.43 "reduced by 90%" and p.46 saturation prose
are arithmetic errors (`C-014`, `C-015`) and are not implemented (`M6-005c`).
"""

from __future__ import annotations

from p2p_thief_agent.perception.scent import (
    _CONFIRMED_EMISSION,
    DECAY_RATE,
    DEFAULT_OUTER_RING_DELTA,
    EMISSION_CENTER,
    FIELD_SIZE,
    OUTER_RING_SQUARED_DISTANCE,
    require_outer_ring,
)
from p2p_thief_agent.protocol.crypto import canonical_sha256

# Negotiation-message members the lock rides in. They sit **outside** the signed terms,
# for the same reason `config_sha256` does: a peer publishing no lock must stay playable.
SCENT_LOCK_FIELD = "scent_model_hash"
SCENT_OUTER_RING_FIELD = "scent_outer_ring_delta"


class ScentLockError(ValueError):
    """Raised when a peer's scent model does not match the model we locked (`AE-23`)."""


def scent_model_record(outer_ring: float = DEFAULT_OUTER_RING_DELTA) -> dict:
    """Return the canonical description of the scent model this peer will run.

    Keyed by squared distance rather than by cell offset: the model is radially
    symmetric, and a per-offset record would let two peers agree on the physics yet
    disagree on the digest purely through how they spell a key.
    """
    profile = {str(distance): value for distance, value in _CONFIRMED_EMISSION.items()}
    profile[str(OUTER_RING_SQUARED_DISTANCE)] = require_outer_ring(outer_ring)
    return {
        "model": "multiplicative-decay",
        "update": "tau_next = max(0, (1 - decay_per_step) * tau + emission)",
        "center_intensity": EMISSION_CENTER,
        "decay_per_step": DECAY_RATE,
        "field_size": FIELD_SIZE,
        "emission_profile_by_squared_distance": profile,
    }


def scent_model_hash(outer_ring: float = DEFAULT_OUTER_RING_DELTA) -> str:
    """Return the SHA-256 lock over the canonical scent-model record."""
    return canonical_sha256(scent_model_record(outer_ring))


def scent_lock_fields(outer_ring: float = DEFAULT_OUTER_RING_DELTA) -> dict:
    """Return the negotiation-message members that publish our lock (`M6-005b`)."""
    return {
        SCENT_LOCK_FIELD: scent_model_hash(outer_ring),
        SCENT_OUTER_RING_FIELD: require_outer_ring(outer_ring),
    }


def verify_peer_scent_lock(
    offered: object,
    *,
    outer_ring: float = DEFAULT_OUTER_RING_DELTA,
) -> None:
    """Accept an absent lock; refuse one that disagrees with ours (`AE-23`).

    `None` is silence, not deviation — and the reference implementation is silent here.
    A present-but-different lock means the two peers would emit different fields from
    the same cell, which rule 23 cancels the game for, so it is caught before the first
    move rather than at the audit.
    """
    if offered is None:
        return
    expected = scent_model_hash(outer_ring)
    if offered != expected:
        raise ScentLockError(
            f"scent model lock mismatch: peer carries {offered!r}, expected {expected!r}; "
            "Appendix E rule 23 cancels a game on an emission-model deviation"
        )


def assert_scent_locked(
    agreed_hash: object,
    *,
    outer_ring: float = DEFAULT_OUTER_RING_DELTA,
) -> None:
    """Runtime check: the model about to run still matches what was locked (`M6-022`).

    Recomputed from the code that will actually emit and observe, so a later edit that
    drifts this peer's physics from the agreed model fails loudly here instead of
    silently emitting fields the opponent's audit would reject.
    """
    running = scent_model_hash(outer_ring)
    if running != agreed_hash:
        raise ScentLockError(
            f"running scent model {running} does not match the locked model {agreed_hash!r}"
        )
