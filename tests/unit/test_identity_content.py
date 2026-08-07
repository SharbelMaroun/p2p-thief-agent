"""`M5-014f`: the pre-game exchange carries what the book mandates.

Split from `test_handshake.py`, which covers the signing mechanics. The seam is real: that
file asks *is this agreement authentic*, this asks *is it complete*. They are independent —
identity is deliberately **not** covered by the signature, because roles alternate across
sub-games, so a perfectly authentic handshake can still carry an identity that cannot
produce a declaration.

`inst/:1278`: Step-0 collects the hardware specification and the language model version, and
"also documents the code version, the group name, and the game number"; p.39/104 and p.78/183
add group identity with members, the repository URLs and the MCP addresses. Rule 24 is
Mandatory and its sanction is denial of eligibility for computational bonuses.

**The gap was inbound.** `identity_block` already takes all seven as required arguments, so
our own could not be short. An opponent's arrived as `message.get("identity", {})`, and an
empty dict was accepted in silence — the first sign would have been a declaration we could
not complete, after both sides had signed the terms.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.protocol.handshake import (
    MANDATED_IDENTITY_MEMBERS,
    Handshake,
    IdentityError,
    require_identity,
)
from tests.unit.test_handshake import terms

# --- M5-014f: the book's mandated pre-game content --------------------------------------


def _complete(**overrides) -> dict:
    block = {"group_id": "opp", "group_name": "Opponents", "members": ["s1"],
             "repos": {"cop": "https://x/c", "thief": "https://x/t"},
             "mcp_servers": {"peer": "https://x/mcp"},
             "llm_model": "template-free", "spec": {"os": "Windows 11"}}
    block.update(overrides)
    return block


def test_a_complete_peer_identity_is_accepted() -> None:
    assert require_identity(_complete(), whose="the opponent")["group_id"] == "opp"


@pytest.mark.parametrize("member", MANDATED_IDENTITY_MEMBERS)
def test_an_identity_missing_any_mandated_member_is_refused(member: str) -> None:
    """`inst/:1278` and p.39/104: the pre-game exchange carries team identity, members,
    repository and MCP URLs, hardware and model. Rule 24 is Mandatory and its sanction is
    denial of eligibility for computational bonuses — so a short identity costs points, and
    costs them silently."""
    with pytest.raises(IdentityError, match=member):
        require_identity(_complete(**{member: None}), whose="the opponent")


@pytest.mark.parametrize("empty", [{}, None, "", []])
def test_an_absent_identity_is_refused_rather_than_defaulted(empty: object) -> None:
    """**The gap this row names.** An opponent's identity arrived as
    `message.get("identity", {})` and an empty dict was accepted in silence. The first sign
    would have been a declaration we could not complete, after the terms were signed."""
    with pytest.raises(IdentityError, match="absent"):
        require_identity(empty, whose="the opponent")


def test_an_empty_value_counts_as_missing() -> None:
    """A present-but-empty member is not a declaration. An unstated hardware spec and a
    missing one are the same thing to a grader, and neither belongs in a signed artifact."""
    with pytest.raises(IdentityError, match="spec"):
        require_identity(_complete(spec={}), whose="the opponent")


def test_the_refusal_names_every_missing_member_at_once() -> None:
    """One round trip, one answer. Naming them one at a time turns a handshake into a
    conversation with an opponent who may not be watching their terminal."""
    with pytest.raises(IdentityError) as caught:
        require_identity({"group_id": "opp"}, whose="the opponent")
    for member in ("group_name", "members", "repos", "mcp_servers", "llm_model", "spec"):
        assert member in str(caught.value)


def test_a_short_identity_is_refused_at_the_wire_not_later() -> None:
    """Wired into `verify_peer`, so it stops the handshake rather than surfacing when the
    declaration is built and both sides have already signed the terms."""
    bob = Handshake(terms=terms(), identity={"group_id": "bob"})
    with pytest.raises(IdentityError, match="AE-24"):
        Handshake(terms=terms()).verify_peer(bob.signed())
