"""Tests for the public Thief SDK boundary."""

from dataclasses import FrozenInstanceError

import pytest

from p2p_thief_agent import ThiefSdk, __version__


def test_sdk_exposes_scaffold_identity() -> None:
    """The public SDK exposes role and package version metadata."""
    sdk = ThiefSdk()

    assert sdk.role == "thief"
    assert sdk.version == __version__


def test_sdk_identity_is_immutable() -> None:
    """External adapters cannot rewrite the SDK's role identity."""
    sdk = ThiefSdk()

    with pytest.raises(FrozenInstanceError):
        sdk.role = "cop"  # type: ignore[misc]


def test_sdk_reaches_commit_seal_verify_audit_and_handshake() -> None:
    """`M4-008`: the protocol surface is reachable through the SDK, not via internals."""
    from p2p_thief_agent import sdk

    for name in ("commit_of", "seal", "verify", "audit_records", "Handshake"):
        assert hasattr(sdk, name), f"SDK must expose {name}"
