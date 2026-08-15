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


def test_a_short_identity_is_recorded_at_the_wire_not_refused() -> None:
    """`C-047`, replacing the assertion this test made until 2026-08-15.

    It used to require `verify_peer` to RAISE on a short identity, and it passed
    continuously while encoding a rule no source supports. Whether an opponent may be
    refused for an incomplete identity is `U-024` -- explicitly **open**, not settled in
    our favour -- and the companion settled the send/receive split as "populate ours,
    tolerate theirs". Rule 24's sanction is the loss of a computational bonus, a cost we
    bear for what the opponent withheld; it is not a licence to void a game.

    A peer that carries its group id at the top level and sends no `identity` at all is
    real: group `yanell11` do, and the companion lost a live friendly to the mirror of
    this. This side would have lost sub-game 2 to this line.
    """
    bob = Handshake(terms=terms(), identity={"group_id": "bob"})
    alice = Handshake(terms=terms())
    alice.verify_peer(bob.signed())
    assert alice.peer_identity == {"group_id": "bob"}
    assert "llm_model" in alice.peer_identity_missing


def test_an_absent_identity_object_still_agrees() -> None:
    """The shape that actually broke us: no `identity` key on the message at all."""
    bob = Handshake(terms=terms(), identity={"group_id": "bob"})
    message = {k: v for k, v in bob.signed().items() if k != "identity"}
    alice = Handshake(terms=terms())
    alice.verify_peer(message)
    assert alice.peer_identity == {}
    assert alice.peer_identity_missing == list(MANDATED_IDENTITY_MEMBERS)


def test_the_terms_and_signature_are_still_enforced() -> None:
    """Tolerating identity must not have loosened what actually binds the agreement."""
    bob = Handshake(terms=terms(), identity={"group_id": "bob"})
    tampered = {**bob.signed(), "terms": {**terms(), "board_size": 9}}
    with pytest.raises(Exception):  # noqa: B017, PT011 - CryptoError, via the terms guard
        Handshake(terms=terms()).verify_peer(tampered)


def test_require_identity_is_still_strict_for_our_own_block() -> None:
    """The function is not deleted: it is simply no longer aimed at the opponent."""
    with pytest.raises(IdentityError, match="AE-24"):
        require_identity({"group_id": "us"}, whose="our own")
