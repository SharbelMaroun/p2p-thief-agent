"""The proposed conformance behavior is reachable through the SDK boundary."""

from p2p_thief_agent import protocol, sdk

PROTOCOL_EXPORTS = (
    "PROFILE",
    "VERSION",
    "CanonicalizationError",
    "ConformanceError",
    "ConformanceSession",
    "NegotiationState",
    "NegotiatedOffer",
    "accept_offer",
    "agreed_configuration_sha256",
    "audit_sha256",
    "build_offer",
    "canonical_sha256",
    "canonicalize",
    "commitment_sha256",
    "loads",
    "new_nonce",
    "open_remote_session",
    "rejection",
    "source_sha256",
    "validate_offer",
    "verify_commitment",
)


def test_protocol_facade_and_sdk_export_every_public_symbol() -> None:
    for name in PROTOCOL_EXPORTS:
        assert name in protocol.__all__
        assert name in sdk.__all__
        assert getattr(sdk, name) is getattr(protocol, name)


def test_sdk_exposes_protocol_namespace() -> None:
    assert sdk.protocol is protocol
