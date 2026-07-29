"""Simulator-conformant peer-to-peer wire protocol.

Envelope-free message types, commit-reveal crypto, sealing helpers, and the signed-terms
handshake, all independently authored to match the reference simulator
(`Game-P2P-Cop-Chase`) for cross-agent interoperability. The superseded self-authored
Option-B conformance profile and its neutral stub are archived under
`archive/pre-sim-realign/`.
"""

from p2p_thief_agent.protocol.crypto import (
    NONCE_BYTES,
    CryptoError,
    audit_records,
    canonical_json,
    canonical_sha256,
    commit_of,
    new_nonce,
    seal,
    verify,
)
from p2p_thief_agent.protocol.handshake import (
    AGREEMENT_TERMS,
    REQUIRED_TERMS,
    Handshake,
    config_sha256,
    identity_block,
    missing_required_terms,
)
from p2p_thief_agent.protocol.sealing import (
    StepDecision,
    build_turn_message,
    sealed_spec_record,
    sealed_step_payload,
    sealed_step_record,
    state_str,
)
from p2p_thief_agent.protocol.wire import (
    CONTROL_KINDS,
    RESULT_CLAIMS,
    ROLES,
    AuditPayload,
    ControlMessage,
    TurnMessage,
    WireError,
)

__all__ = [
    "AGREEMENT_TERMS",
    "AuditPayload",
    "CONTROL_KINDS",
    "ControlMessage",
    "CryptoError",
    "Handshake",
    "NONCE_BYTES",
    "REQUIRED_TERMS",
    "RESULT_CLAIMS",
    "ROLES",
    "StepDecision",
    "TurnMessage",
    "WireError",
    "audit_records",
    "build_turn_message",
    "canonical_json",
    "canonical_sha256",
    "commit_of",
    "config_sha256",
    "identity_block",
    "missing_required_terms",
    "new_nonce",
    "seal",
    "sealed_spec_record",
    "sealed_step_payload",
    "sealed_step_record",
    "state_str",
    "verify",
]
