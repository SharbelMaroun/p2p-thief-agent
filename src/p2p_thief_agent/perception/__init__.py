"""Thief-local perception: scent physics and (later) belief (`M6`).

Pure, transport-free, and holding no Cop-private truth — this layer turns public
observations into the Thief's own view of the board (`SR-004`, `THIEF-001`).
"""

from p2p_thief_agent.perception.belief import (
    BeliefError,
    apply_evidence,
    normalize,
    uniform_belief,
)
from p2p_thief_agent.perception.consume import consume_hint
from p2p_thief_agent.perception.field import (
    blank_field,
    deposit,
    emit_at,
    scent_likelihood,
)
from p2p_thief_agent.perception.hint import decode_hint
from p2p_thief_agent.perception.observation import (
    ObservationError,
    encode_smell_grid,
    parse_smell_grid,
)
from p2p_thief_agent.perception.scent import (
    DECAY_RATE,
    DEFAULT_OUTER_RING_DELTA,
    EMISSION_CENTER,
    FIELD_SIZE,
    OUTER_RING_SQUARED_DISTANCE,
    ScentModelError,
    advance_field,
    emission_delta,
    emission_field,
    require_outer_ring,
    settle,
)
from p2p_thief_agent.perception.scent_lock import (
    SCENT_LOCK_FIELD,
    SCENT_OUTER_RING_FIELD,
    ScentLockError,
    assert_scent_locked,
    scent_lock_fields,
    scent_model_hash,
    scent_model_record,
    verify_peer_scent_lock,
)
from p2p_thief_agent.perception.trust import (
    NEUTRAL_TRUST,
    trust_weighted,
    update_trust,
)

__all__ = [
    "DECAY_RATE",
    "DEFAULT_OUTER_RING_DELTA",
    "OUTER_RING_SQUARED_DISTANCE",
    "ScentModelError",
    "EMISSION_CENTER",
    "FIELD_SIZE",
    "NEUTRAL_TRUST",
    "SCENT_LOCK_FIELD",
    "SCENT_OUTER_RING_FIELD",
    "BeliefError",
    "ObservationError",
    "ScentLockError",
    "advance_field",
    "apply_evidence",
    "assert_scent_locked",
    "blank_field",
    "consume_hint",
    "decode_hint",
    "deposit",
    "emission_delta",
    "emission_field",
    "require_outer_ring",
    "emit_at",
    "encode_smell_grid",
    "normalize",
    "parse_smell_grid",
    "scent_likelihood",
    "scent_model_hash",
    "scent_model_record",
    "scent_lock_fields",
    "settle",
    "trust_weighted",
    "uniform_belief",
    "update_trust",
    "verify_peer_scent_lock",
]
