"""Launch a Thief peer and play one match over the wire (`M9-026`).

`M9-025` gave this repository a command line; it could start a mailbox and wait. Nobody ever
started a game, because *starting* one means negotiating terms first and there was no path
from the CLI to `run_autonomous_match`. Every piece already existed and was tested — the
mailbox, the client, the phase machine, the turn loop, the negotiation, the artifact
builders. What was missing is the thirty lines that hold them together, which is exactly the
shape `M9-025` had one layer up.

**This peer opens.** The book gives the Thief the first move of every turn cycle, so the
order below is not interchangeable: bind our own mailbox, wait until the opponent's answers,
*then* negotiate, then play. A Thief that opened before the opponent was listening would send
into a socket nobody is reading; one that waited for the opponent to move first would deadlock
against a Cop correctly waiting for us.

Nothing here decides anything. The decision function is injected, the transport is injected,
and the clock is injected — the same seams the tests already drive. This module only puts
them in the right order and in the right sequence.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from p2p_thief_agent.orchestration.phases import PhaseMachine
from p2p_thief_agent.orchestration.sub_game import run_sub_game_over_wire


class ServeError(RuntimeError):
    """Raised when a match cannot be started or cannot be played to a decision."""


@dataclass(frozen=True, slots=True)
class MatchOutcome:
    """What one served match produced, for the CLI to report and a test to assert."""

    outcome: object
    steps: int
    records: list[dict]


def serve_match(
    *,
    peer_url: str,
    port: int,
    host: str = "127.0.0.1",
    survival_threshold: int,
    decide: Callable[..., object],
    answer_claim: Callable[[object], bool] | None = None,
    ready_timeout: float = 30.0,
    sleep: Callable[[float], None] = time.sleep,
    artifacts_dir: Path | None = None,
    game_config: Mapping[str, object] | None = None,
    identity: Mapping[str, object] | None = None,
    sub_game: int = 1,
) -> MatchOutcome:
    """Bind, wait for the opponent, then play one sub-game to a decision.

    `ready_timeout` exists because two peers are started by two people who cannot press
    a key at the same instant: waiting is the normal case, and only running out of
    patience is an error.

    `answer_claim` may be omitted only when `decide` carries its own honest answerer
    (`make_decide` attaches one). The old `lambda _cell: False` default was a standing
    false denial of every correct capture — an audit-provable forgery `[AE-021]` — and
    no honest default exists without the position, so an absent answerer refuses to play.
    """
    if answer_claim is None:
        answer_claim = getattr(decide, "answer_claim", None)
    if answer_claim is None:
        raise ServeError(
            "serve_match needs an honest answer_claim: pass one, or use a decide "
            "factory that attaches its own (make_decide does)")
    from p2p_thief_agent.adapters.fastmcp_client import FastMCPClient  # noqa: PLC0415
    from p2p_thief_agent.adapters.fastmcp_server import PeerInboxes  # noqa: PLC0415
    from p2p_thief_agent.adapters.serving import (
        peer_answers,  # noqa: PLC0415
        serve_in_background,  # noqa: PLC0415
    )
    from p2p_thief_agent.services.readiness import wait_for_peer  # noqa: PLC0415

    inboxes = PeerInboxes()
    serve_in_background(inboxes, port=port, host=host)

    # `wait_for_peer` takes a probe rather than a URL, so it can be driven by a test
    # without opening a socket — the same injection the deadline and watchdog modules use.
    #
    # **The probe is `peer_answers`, not `port_answers` (corrected 2026-08-09).** The old
    # form TCP-connected to the host it parsed out of the URL — and defaulted to port 80
    # when an https URL named none. Through a tunnel that reaches a CDN edge which accepts
    # regardless of whether the opponent exists, so the wait passed instantly and the first
    # `negotiate` returned 502. Found in a live match attempt, not by any test.
    answered = wait_for_peer(
        lambda: peer_answers(peer_url),
        clock=time.monotonic, sleep=sleep, timeout=ready_timeout,
    )
    if not answered:
        raise ServeError(
            f"the opponent at {peer_url} never answered within {ready_timeout:g}s. Both peers "
            "must be running: start theirs, or check the address and port")

    client = FastMCPClient(peer_url)
    threshold = survival_threshold
    agreement = None
    started_at = None
    if game_config is not None:
        # `M5-014f` on the playable path: agree before the first move. The companion
        # Cop refuses an unnegotiated game, and so does the book.
        from datetime import UTC, datetime  # noqa: PLC0415

        from p2p_thief_agent.adapters.negotiated import (  # noqa: PLC0415
            NegotiatedServeError,
            negotiated_agreement,
        )

        if not identity:
            raise ServeError("negotiation needs this peer's identity; pass --private")
        try:
            agreement = negotiated_agreement(
                client=client, inboxes=inboxes, game_config=game_config,
                identity=identity, fallback_timeout=ready_timeout, sleep=sleep,
            )
        except NegotiatedServeError as exc:
            raise ServeError(str(exc)) from exc
        threshold = int(agreement.terms["max_steps"])
        started_at = datetime.now(UTC).isoformat()

    # `receive` owns the bounded waiting; the raw non-blocking take made the loop
    # check the inbox once, microseconds after its own send, and declare a live
    # opponent silent — the first two-process rehearsal died at step 1 on this.
    from p2p_thief_agent.orchestration.polling import poll_for_turn  # noqa: PLC0415

    records: list[dict] = []
    result = run_sub_game_over_wire(
        machine=PhaseMachine(),
        transport=client,
        receive=lambda: poll_for_turn(
            lambda: _take(inboxes), clock=time.monotonic, sleep=sleep,
            timeout=_turn_timeout(game_config, ready_timeout)),
        decide=decide,
        answer_claim=answer_claim,
        survival_threshold=threshold,
        records=records,
    )
    if artifacts_dir is not None:
        context = None
        if agreement is not None and game_config is not None and identity is not None:
            from p2p_thief_agent.protocol.crypto import canonical_sha256  # noqa: PLC0415

            sha = canonical_sha256(dict(game_config))
            context = {
                "game_id": f"game-{sha[:12]}", "game_uid": sha[:32], "sub_game": sub_game,
                "group_id": identity.get("group_id", "unknown"),
                "opponent_group_id": agreement.peer_identity.get("group_id", "unknown"),
                "config_sha256": sha, "confirmed": True, "started_at": started_at,
            }
        _write_log(artifacts_dir, records, result, context)
    return MatchOutcome(outcome=result.outcome, steps=result.steps, records=records)


def _turn_timeout(game_config: Mapping[str, object] | None, fallback: float) -> float:
    """The per-turn wait budget: the shared file's response timeout, or the fallback."""
    league = (game_config or {}).get("network_and_league")
    if isinstance(league, Mapping):
        return float(league.get("response_timeout_sec", fallback))
    return float(fallback)


def _take(inboxes: object) -> Mapping[str, object] | None:  # noqa: D401
    """Take the next inbound turn, or `None` if the opponent has not sent one yet.

    Returning `None` rather than blocking keeps the turn loop in charge of waiting. The loop
    already owns the deadline and the watchdog; a blocking read here would take that decision
    away from the component the rules hold responsible for it.
    """
    from p2p_thief_agent.adapters.fastmcp_server import take_turn  # noqa: PLC0415
    from p2p_thief_agent.peer import InboundPeer  # noqa: PLC0415

    return take_turn(inboxes, InboundPeer())


def _write_log(directory: Path, records: list[dict], result: object,
               context: Mapping[str, object] | None = None) -> Path:
    """Write the finished log; the body lives in `adapters/match_log.py` (length gate)."""
    from p2p_thief_agent.adapters.match_log import write_match_log  # noqa: PLC0415

    return write_match_log(directory, records, result, context)


def resolve_peer(peer: str | None, private: Path | None) -> str:
    """Decide which address to dial; the body lives in `play_command` (length gate)."""
    from p2p_thief_agent.adapters.play_command import resolve_peer_address  # noqa: PLC0415

    return resolve_peer_address(peer, private)
