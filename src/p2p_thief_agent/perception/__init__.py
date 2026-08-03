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
from p2p_thief_agent.perception.observation import (
    ObservationError,
    encode_smell_grid,
    parse_smell_grid,
)
from p2p_thief_agent.perception.scent import (
    DECAY_RATE,
    EMISSION_CENTER,
    FIELD_SIZE,
    advance_field,
    emission_delta,
    emission_field,
    settle,
)

__all__ = [
    "DECAY_RATE",
    "EMISSION_CENTER",
    "FIELD_SIZE",
    "BeliefError",
    "ObservationError",
    "advance_field",
    "apply_evidence",
    "emission_delta",
    "emission_field",
    "encode_smell_grid",
    "normalize",
    "parse_smell_grid",
    "settle",
    "uniform_belief",
]
