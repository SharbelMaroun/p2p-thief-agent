"""Shared package metadata with no cross-peer runtime state."""

from p2p_thief_agent.shared.private_config import (
    PrivateConfigError,
    SharedConfigLeakError,
    assert_no_network_address,
    load_opponent_url,
    load_private_config,
    opponent_url,
)
from p2p_thief_agent.shared.version import __version__

__all__ = [
    "PrivateConfigError",
    "SharedConfigLeakError",
    "__version__",
    "assert_no_network_address",
    "load_opponent_url",
    "load_private_config",
    "opponent_url",
]
