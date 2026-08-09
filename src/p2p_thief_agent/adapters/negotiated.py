"""The negotiated serve path: its inputs, and the pre-play handshake (`M5-014f`).

`M5-019f` built the negotiation sequencing and only the tests ever called it — the
CLI's match path went straight to the turn loop, which composes with nothing: the
companion Cop refuses to play unnegotiated, and so does the book ("play starts only
after both verifications pass"). Found 2026-08-08 preparing the first two-process
rehearsal of the real policies. This module is the missing seam: load the shared
match object and this peer's identity, run the signed-terms handshake over the live
mailbox pair, and hand back the negotiated horizon that governs play.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from pathlib import Path
from time import monotonic

from p2p_thief_agent.orchestration.negotiation import NegotiationError, negotiate_for_serve
from p2p_thief_agent.protocol.terms_projection import terms_from_shared_config
from p2p_thief_agent.shared.private_config import identity_from_private, load_private_config


class NegotiatedServeError(RuntimeError):
    """Raised when the negotiated path cannot assemble its inputs or agree terms."""


def load_negotiation_inputs(
    game_path: str | Path,
    private_path: str | Path | None,
    own_url: str,
    peer_url: str,
) -> tuple[dict, dict]:
    """Return (shared game config, our identity) for a negotiated match.

    The identity comes from the private TOML because rule 24 mandates the exchange
    carry the group, members, repositories, MCP addresses, model, and hardware —
    which is exactly the material that must never live in the shared file.
    """
    if private_path is None:
        raise NegotiatedServeError(
            "--game needs --private: negotiation must carry this peer's identity")
    game_config = json.loads(Path(game_path).read_text("utf-8"))
    identity = identity_from_private(load_private_config(private_path), own_url, peer_url)
    return game_config, identity


def negotiated_agreement(
    *,
    client: object,
    inboxes: object,
    game_config: Mapping[str, object],
    identity: Mapping[str, object],
    fallback_timeout: float,
    sleep: Callable[[float], None],
):
    """Agree the match over the live pair and return the whole `AgreedMatch`.

    The caller reads the negotiated horizon from ``terms["max_steps"]`` and the
    opponent's identity for the artifacts — a counted game's log must name the real
    opponent and the real config lock, not placeholders. The response timeout comes
    from the shared file's own ``network_and_league.response_timeout_sec`` — the same
    clock both sides read — falling back to the caller's readiness budget.

    The offer send carries the **signed** bounded retry (2026-08-09). Without it one
    transient tunnel fault raised a raw `TransportError` straight out of `serve_match`,
    which is the failure `PROMPT_LOG.md` records for the first real match attempt.
    """
    from p2p_thief_agent.orchestration.delivery import retrying_deliver  # noqa: PLC0415

    league = game_config.get("network_and_league")
    timeout = float(league.get("response_timeout_sec", fallback_timeout)
                    if isinstance(league, Mapping) else fallback_timeout)
    deliver_offer = retrying_deliver(game_config, sleep, clock=monotonic)

    try:
        return negotiate_for_serve(
            client=client, inboxes=inboxes,
            terms=terms_from_shared_config(game_config), identity=identity,
            timeout=timeout, clock=monotonic, sleep=sleep, deliver_offer=deliver_offer,
        )
    except NegotiationError as exc:
        raise NegotiatedServeError(f"the match was refused before play: {exc}") from exc
