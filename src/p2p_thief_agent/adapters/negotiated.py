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

import contextlib
import json
from collections.abc import Callable, Mapping
from pathlib import Path
from time import monotonic

from p2p_thief_agent.orchestration.negotiation import NegotiationError, negotiate_for_serve
from p2p_thief_agent.protocol.terms_projection import terms_from_shared_config
from p2p_thief_agent.shared.git_info import GitInfoError, running_git_commit
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

    ``git_commit_hash`` is attached when resolvable, as a **peer accommodation**, not
    a book member (`C-030`). The book homes the commit hash in the sealed Step-0
    declaration and the emailed `github_commit` (rules 24/53, `inst/:1295`), and the
    reference's wire identity carries no code version at all -- but group `uoh-ay26`'s
    `mutual_sign_off` reads `identity.git_commit_hash` and quietly voids the mutual
    result when it is absent, which would fail the reference itself. Identity is
    unsigned and role-free, so the extra member costs nothing. Best-effort on purpose:
    the mandated home keeps its fail-closed resolver (`shared/git_info.py`), while an
    optional duplicate must not refuse a match that Step-0 would attest correctly.
    """
    if private_path is None:
        raise NegotiatedServeError(
            "--game needs --private: negotiation must carry this peer's identity")
    game_config = json.loads(Path(game_path).read_text("utf-8"))
    identity = identity_from_private(load_private_config(private_path), own_url, peer_url)
    # Optional duplicate; Step-0 remains the mandated, fail-closed home.
    with contextlib.suppress(GitInfoError):
        identity["git_commit_hash"] = running_git_commit()
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
    # The offer wait is PRE-game patience, so the connect budget is its floor. Capping it
    # at `response_timeout_sec` (30) ended the second amireman smoke at the role swap:
    # their sub-game-2 negotiate had landed on our game-1 agent's audit window and was
    # gone, and 30 seconds was not enough for their server to rebind and try again. The
    # in-game timer starts governing once play does, not before the opponent exists.
    timeout = max(
        float(league.get("response_timeout_sec", fallback_timeout)
              if isinstance(league, Mapping) else fallback_timeout),
        fallback_timeout,
    )
    deliver_offer = retrying_deliver(game_config, sleep, clock=monotonic)

    try:
        return negotiate_for_serve(
            client=client, inboxes=inboxes,
            terms=terms_from_shared_config(game_config), identity=identity,
            timeout=timeout, clock=monotonic, sleep=sleep, deliver_offer=deliver_offer,
        )
    except NegotiationError as exc:
        raise NegotiatedServeError(f"the match was refused before play: {exc}") from exc
