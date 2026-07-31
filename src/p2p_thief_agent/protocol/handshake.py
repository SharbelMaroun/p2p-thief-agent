"""Simulator-conformant pre-game handshake: signed-terms agreement and config hash.

Independently authored to match the reference simulator's `domain/negotiation.py` and
`report/artifacts.py` config hashing. Each peer signs `commit_of(terms, nonce)` and
verifies the opponent signed the **same** terms; play starts only after both verify.
Group identity is exchanged but is NOT a must-match term and is NOT covered by the
signature -- roles alternate across sub-games, so identity is per-group and carries no
role. The single agreed-configuration hash is `canonical_sha256(terms)`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from p2p_thief_agent.protocol.crypto import (
    CryptoError,
    canonical_sha256,
    commit_of,
    new_nonce,
    verify,
)

# Every term both peers agree on (order-independent under canonical JSON).
# `min_center_intensity` stays listed so it is compared when a peer sends it, but it
# is deliberately NOT required -- see below.
AGREEMENT_TERMS = (
    "board_size", "smell_grid_size", "decay_per_step", "emit_intensity",
    "min_center_intensity", "max_steps", "barriers_max", "setting", "hint_max_words",
    "axis_origin_corner", "axis_start_index", "thief_start", "cop_start", "num_games",
)
# Terms with no safe default: play cannot start until these resolve.
#
# `min_center_intensity` was required here until 2026-08-01 and that was wrong.
# Checked against the book PDF itself: Appendix F table 16 has exactly three rows,
# all `Fixed` -- centre intensity `0.9`, decay `0.10`, field `5x5` -- and **no**
# minimum or floor row. The lecturer's own `agreed-config` artifact template is the
# same: its pheromone block is exactly `pheromone_center_intensity`,
# `pheromone_decay`, and `pheromone_grid_size`. Requiring a fourth key made this
# peer refuse the very template teams are meant to share, reporting it as a missing
# agreed term. The pinned simulator does require it, but a simulator behaviour that
# contradicts both the book and the lecturer's template is not authority (`U-023`).
REQUIRED_TERMS = (
    "board_size", "smell_grid_size", "decay_per_step", "emit_intensity",
    "max_steps", "barriers_max", "thief_start", "cop_start",
)


def config_sha256(terms: Mapping) -> str:
    """Return the single agreed-configuration hash over the shared terms."""
    return canonical_sha256(dict(terms))


def missing_required_terms(terms: Mapping) -> list[str]:
    """Return required agreed terms that are absent or None (empty means complete)."""
    return [name for name in REQUIRED_TERMS if terms.get(name) is None]


def identity_block(
    *,
    group_id: str,
    group_name: str,
    members: list,
    repos: dict,
    mcp_servers: dict,
    llm_model: str,
    spec: dict,
) -> dict:
    """Assemble this peer's per-group identity (deliberately carries no role)."""
    return {
        "group_id": group_id,
        "group_name": group_name,
        "members": members,
        "repos": repos,
        "mcp_servers": mcp_servers,
        "llm_model": llm_model,
        "spec": spec,
    }


@dataclass(slots=True)
class Handshake:
    """One peer's side of the signed-terms agreement."""

    terms: dict
    identity: dict = field(default_factory=dict)
    nonce: str = field(default_factory=new_nonce)
    peer_identity: dict = field(default_factory=dict, init=False)

    def signed(self) -> dict:
        """Return this peer's agreement message: terms, nonce, signature, identity."""
        return {
            "terms": self.terms,
            "nonce": self.nonce,
            "signature": commit_of(self.terms, self.nonce),
            "identity": self.identity,
        }

    def verify_peer(self, message: Mapping) -> None:
        """Verify the opponent signed the SAME terms; capture its identity.

        Raises CryptoError on a terms mismatch or an invalid signature.
        """
        if message.get("terms") != self.terms:
            raise CryptoError("agreement terms mismatch between peers")
        verify(message["terms"], message["nonce"], message["signature"])
        self.peer_identity = dict(message.get("identity", {}))
