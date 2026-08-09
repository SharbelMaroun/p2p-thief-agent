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

from p2p_thief_agent.adapters.fastmcp_client import TransportError
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
from p2p_thief_agent.services.deadlines import DeadlineError

# Send this peer's signed offer to the opponent (the opponent's `negotiate` tool).
SendOffer = Callable[[Mapping[str, object]], object]
# Play one sub-game bounded by the negotiated horizon, returning its outcome.
PlaySubGame = Callable[[int], object]
# Put the offer on the wire. Injected for the same reason `turn_loop.Deliver` is: the
# caller owns the agreed retry budget, and this module stays policy-neutral.
DeliverOffer = Callable[[SendOffer, Mapping[str, object]], object]


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
    deliver_offer: DeliverOffer | None = None,
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

    **The offer send is retried** when ``deliver_offer`` is supplied (2026-08-09). It was
    one bare attempt, and a transient tunnel fault there raised a raw ``TransportError``
    straight out through `serve_match` — the shape `PROMPT_LOG.md` records for the first
    real match attempt. Fixing the readiness probe made that rarer without making the one
    attempt after it survivable; a tunnel edge can still blip once after the peer is up.
    """
    offer_message = {**handshake.signed(), **scent_lock_fields(scent_outer_ring)}
    try:
        # No `deliver_offer` means one bare attempt — right for an in-memory double,
        # wrong for a tunnel, which is why the live paths always supply one.
        deliver_offer(send_offer, offer_message) if deliver_offer else send_offer(offer_message)
    except (TransportError, DeadlineError) as exc:
        raise NegotiationError(f"our offer could not be delivered: {exc}") from exc
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


def negotiate_for_serve(
    *,
    client: object,
    inboxes: object,
    terms: Mapping[str, object],
    identity: Mapping[str, object],
    timeout: float,
    clock: Clock,
    sleep: Sleep,
    deliver_offer: DeliverOffer | None = None,
) -> AgreedMatch:
    """Run the pre-game handshake over the live mailbox pair for the serve path.

    `M5-019f` built this sequencing and only the tests ever called it — the CLI's
    match path went straight to the turn loop, which composes with nothing: the
    companion Cop (and the book — play starts "only after both verifications pass")
    refuses to play unnegotiated. Found 2026-08-08 preparing the first two-process
    rehearsal of the real policies; this is the missing thirty lines.

    ``deliver_offer`` carries the agreed bounded retry for the offer send; without it a
    single transient tunnel fault refuses the match outright (see `negotiate_match`).
    """
    import queue  # noqa: PLC0415

    from p2p_thief_agent.protocol.handshake import Handshake  # noqa: PLC0415

    def take_offer():
        try:
            return inboxes.agreements.get_nowait()
        except queue.Empty:
            return None

    handshake = Handshake(terms=dict(terms), identity=dict(identity))
    return negotiate_match(
        handshake=handshake, my_terms=dict(terms), send_offer=client.negotiate,
        take_offer=take_offer, clock=clock, sleep=sleep, timeout=timeout,
        deliver_offer=deliver_offer,
    )


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
    and the horizon is the agreed one, not a local default. `play_sub_game` is the
    gateway's (the Thief opens inside it).
    """
    agreed = negotiate_match(
        handshake=handshake, my_terms=my_terms, send_offer=send_offer, take_offer=take_offer,
        clock=clock, sleep=sleep, timeout=timeout, poll_interval=poll_interval, heartbeat=heartbeat,
    )
    # `max_steps` is present and a valid int by construction: `accept_offer` enforces it
    # as a required term and an Appendix F `MINIMUM`, so no defensive re-check is needed.
    return agreed, play_sub_game(agreed.terms["max_steps"])
