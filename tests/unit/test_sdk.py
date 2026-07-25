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
