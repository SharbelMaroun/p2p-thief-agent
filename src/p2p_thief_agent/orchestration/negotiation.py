"""Sequence the pre-game negotiation, then open play (`M5-019f`).

Hosting (`adapters.serve_in_background`) and readiness (`services.readiness.wait_for_peer`)
get two peers up and reachable. This module is the *protocol* handshake that must finish
before the first move: the reference starts play "only after both verifications pass", so
a peer that opened without the opponent's counter-signature would be committing to a match
the other side never agreed to.

Transport-neutral by construction. It is handed a ``send_offer`` and a ``take_offer`` and
imports no FastMCP symbol, so the whole handshake runs over an in-memory pair in a unit
test and over a socket unchanged. ``send_offer`` is the opponent's ``negotiate`` tool;
``take_offer`` drains this peer's own agreements mailbox.

**The Thief opens.** Once both sides verify, this peer sends step 1 without waiting — a
Thief that waited would deadlock against a Cop correctly waiting for it. `run_autonomous_match`
is that composition: agree, then play through the gateway, bounded by the negotiated horizon.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from p2p_thief_agent.orchestration.polling import (
    DEFAULT_POLL_INTERVAL,
    Clock,
    Heartbeat,
    Sleep,
    TakeTurn,
    poll_for_turn,
)
from p2p_thief_agent.perception.scent import DEFAULT_OUTER_RING_DELTA
from p2p_thief_agent.perception.scent_lock import scent_lock_fields, scent_model_hash
from p2p_thief_agent.protocol.agreement import AgreementError, accept_offer
from p2p_thief_agent.protocol.crypto import CryptoError
from p2p_thief_agent.protocol.handshake import Handshake

# Send this peer's signed offer to the opponent (the opponent's `negotiate` tool).
SendOffer = Callable[[Mapping[str, object]], object]
# Play one sub-game bounded by the negotiated horizon, returning its outcome.
PlaySubGame = Callable[[int], object]


class NegotiationError(RuntimeError):
    """Raised when the pre-game agreement cannot be reached or the deadline passes."""


@dataclass(frozen=True, slots=True)
class AgreedMatch:
    """The verified pre-game agreement: the shared terms and the opponent's identity."""

    terms: dict
    peer_identity: dict


def negotiate_match(
    *,
    handshake: Handshake,
    my_terms: Mapping[str, object],
    send_offer: SendOffer,
    take_offer: TakeTurn,
    clock: Clock,
    sleep: Sleep,
    timeout: float,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    heartbeat: Heartbeat | None = None,
    scent_outer_ring: float = DEFAULT_OUTER_RING_DELTA,
) -> AgreedMatch:
    """Send our signed offer, await the opponent's, verify both ways, and agree.

    The verification is deliberately two-sided. `accept_offer` is the *policy* gate —
    Appendix F floors, required terms, the signature, and which term differs — and it is
    what names a refusal an opponent can act on. `Handshake.verify_peer` then binds the
    opponent's identity into this peer's handshake and re-confirms the signature covers
    *our* terms. Silence before the deadline is a refusal, not patience (`AE-6`).

    Our Appendix E rule 23 scent lock is **published** on the offer and **compared**
    against the opponent's when it sends one (`M6-005b`). It rides beside the signed
    terms rather than inside them so a peer that publishes no lock — the pinned
    simulator does not — is still playable, while a peer whose emission model differs
    from ours is refused before a first move exists.
    """
    send_offer({**handshake.signed(), **scent_lock_fields(scent_outer_ring)})
    offer = poll_for_turn(
        take_offer, clock=clock, sleep=sleep, timeout=timeout,
        poll_interval=poll_interval, heartbeat=heartbeat,
    )
    if offer is None:
        raise NegotiationError("opponent sent no signed offer before the deadline")
    try:
        agreed = accept_offer(
            offer, my_terms, expected_scent_lock=scent_model_hash(scent_outer_ring)
        )
        handshake.verify_peer(offer)
    except (AgreementError, CryptoError) as exc:
        raise NegotiationError(f"refused the match: {exc}") from exc
    return AgreedMatch(terms=agreed, peer_identity=dict(handshake.peer_identity))


def run_autonomous_match(
    *,
    handshake: Handshake,
    my_terms: Mapping[str, object],
    send_offer: SendOffer,
    take_offer: TakeTurn,
    play_sub_game: PlaySubGame,
    clock: Clock,
    sleep: Sleep,
    timeout: float,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    heartbeat: Heartbeat | None = None,
) -> tuple[AgreedMatch, object]:
    """Negotiate, then open play bounded by the negotiated horizon (`max_steps`).

    The two steps are one unit on purpose: play must never start before the agreement,
    and the horizon it runs to is the agreed one, not a local default. `play_sub_game`
    is the gateway's `play_sub_game` (the Thief opens inside it).
    """
    agreed = negotiate_match(
        handshake=handshake, my_terms=my_terms, send_offer=send_offer, take_offer=take_offer,
        clock=clock, sleep=sleep, timeout=timeout, poll_interval=poll_interval, heartbeat=heartbeat,
    )
    # `max_steps` is present and a valid int by construction: `accept_offer` enforces it
    # as a required term and an Appendix F `MINIMUM`, so no defensive re-check is needed.
    return agreed, play_sub_game(agreed.terms["max_steps"])
