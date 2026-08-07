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


# The seven members the book mandates in the pre-game exchange (`M5-014f`). `inst/:1278`:
# Step-0 collects the hardware specification and the language model version, and "also
# documents the code version, the group name, and the game number"; p.39/104 and p.78/183 add
# group identity with members, the repository URLs and the MCP addresses.
#
# Rule 24 is Mandatory and its sanction is denial of eligibility for computational bonuses,
# so an identity missing one of these is not merely untidy — it costs points, and it costs
# them *silently*, which is why the check is here rather than in a reviewer's head.
MANDATED_IDENTITY_MEMBERS = (
    "group_id", "group_name", "members", "repos", "mcp_servers", "llm_model", "spec",
)


class IdentityError(ValueError):
    """Raised when a peer identity omits something the book mandates."""


def require_identity(block: object, *, whose: str) -> dict:
    """Refuse an identity block missing a mandated member (`M5-014f`).

    Applied to **incoming** identities, which is where the gap was. `identity_block` already
    takes all seven as required arguments, so our own cannot be short — but an opponent's
    arrived as `message.get("identity", {})` and an empty dict was accepted in silence. The
    first sign would have been a declaration we could not complete, after the terms were
    signed.

    Refused rather than defaulted. A missing hardware spec and an unstated one are different
    claims, and only one of them can be put in a signed artifact.
    """
    if not isinstance(block, Mapping) or not block:
        raise IdentityError(
            f"{whose} identity is absent; the book mandates the pre-game exchange carry team "
            "identity, members, repository and MCP URLs, hardware and model [AE-24]")
    missing = [name for name in MANDATED_IDENTITY_MEMBERS if not block.get(name)]
    if missing:
        raise IdentityError(
            f"{whose} identity omits {', '.join(missing)}; the book mandates all of "
            f"{', '.join(MANDATED_IDENTITY_MEMBERS)} in the pre-game exchange [AE-24]")
    return dict(block)


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
        # `M5-014f`: validated, not merely captured. An opponent whose identity is short
        # cannot produce a complete declaration, and rule 24 charges us for that.
        self.peer_identity = require_identity(message.get("identity"), whose="the opponent")
