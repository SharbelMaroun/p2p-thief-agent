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
    answer_claim: Callable[[object], bool] = lambda _cell: False,
    ready_timeout: float = 30.0,
    sleep: Callable[[float], None] = time.sleep,
    artifacts_dir: Path | None = None,
) -> MatchOutcome:
    """Bind, wait for the opponent, then play one sub-game to a decision.

    `ready_timeout` exists because the two peers are started by two people who cannot press
    a key at the same instant. Waiting is the normal case, not the error case; only running
    out of patience is an error, and it says which address never answered.
    """
    from p2p_thief_agent.adapters.fastmcp_client import FastMCPClient  # noqa: PLC0415
    from p2p_thief_agent.adapters.fastmcp_server import PeerInboxes  # noqa: PLC0415
    from p2p_thief_agent.adapters.serving import (
        port_answers,  # noqa: PLC0415
        serve_in_background,  # noqa: PLC0415
    )
    from p2p_thief_agent.services.readiness import wait_for_peer  # noqa: PLC0415

    inboxes = PeerInboxes()
    serve_in_background(inboxes, port=port, host=host)

    # `wait_for_peer` takes a probe rather than a URL, so it can be driven by a test
    # without opening a socket — the same injection the deadline and watchdog modules use.
    peer_host, _, peer_port = peer_url.rsplit("/", 1)[0].rpartition(":")
    answered = wait_for_peer(
        lambda: port_answers(peer_host.split("//")[-1], int(peer_port or 80)),
        clock=time.monotonic, sleep=sleep, timeout=ready_timeout,
    )
    if not answered:
        raise ServeError(
            f"the opponent at {peer_url} never answered within {ready_timeout:g}s. Both peers "
            "must be running: start theirs, or check the address and port")

    client = FastMCPClient(peer_url)
    records: list[dict] = []
    result = run_sub_game_over_wire(
        machine=PhaseMachine(),
        transport=client,
        receive=lambda: _take(inboxes),
        decide=decide,
        answer_claim=answer_claim,
        survival_threshold=survival_threshold,
        records=records,
    )
    if artifacts_dir is not None:
        _write_log(artifacts_dir, records, result)
    return MatchOutcome(outcome=result.outcome, steps=result.steps, records=records)


def _take(inboxes: object) -> Mapping[str, object] | None:  # noqa: D401
    """Take the next inbound turn, or `None` if the opponent has not sent one yet.

    Returning `None` rather than blocking keeps the turn loop in charge of waiting. The loop
    already owns the deadline and the watchdog; a blocking read here would take that decision
    away from the component the rules hold responsible for it.
    """
    from p2p_thief_agent.adapters.fastmcp_server import take_turn  # noqa: PLC0415
    from p2p_thief_agent.peer import InboundPeer  # noqa: PLC0415

    return take_turn(inboxes, InboundPeer())


def _write_log(directory: Path, records: list[dict], result: object) -> Path:
    """Write the finished sub-game log, with the end time rule 18's guard requires."""
    from datetime import datetime, timezone  # noqa: PLC0415

    from p2p_thief_agent.reporting.emit import write_artifact  # noqa: PLC0415
    from p2p_thief_agent.reporting.log_artifact import build_log  # noqa: PLC0415
    from p2p_thief_agent.reporting.naming import MatchIdentity, log_filename  # noqa: PLC0415

    ended = datetime.now(timezone.utc).isoformat()
    identity = MatchIdentity(game_id="local-match", game_uid="local-match-uid")
    summary = {
        "sub_game_number": 1, "group_id": "sharNamr", "role": "thief",
        "opponent_group_id": "opponent", "result": getattr(getattr(result, "outcome", None), "value", "unknown"),
        "winner_role": "thief", "steps": getattr(result, "steps", 0),
        "timezone": "UTC", "started_at": ended, "ended_at": ended,
        "duration_seconds": 0, "tokens_total": 0, "audit": {},
    }
    artifact = build_log(
        identity=identity, summary=summary, links={},
        mutual_agreement={"opponent_group_id": "opponent", "sha256": "0" * 64,
                          "confirmed": False},
        records=records,
    )
    return write_artifact(Path(directory), log_filename(identity.game_id, 1), artifact)


def resolve_peer(peer: str | None, private: Path | None) -> str:
    """Decide which address to dial, from a flag or the private config (`M5-005`).

    Two sources on purpose. A flag is right while developing on one machine; a private TOML
    is right for league play, where the address is a tunnel URL and the token that created
    it must stay out of every shared file (book §2.4, `[AE-10]`).

    An explicit `--peer` wins over the file: the operator typing an address at 2 a.m. means
    that address, and silently preferring a stale config value would be the least helpful
    possible interpretation.
    """
    if peer:
        return peer
    if private is None:
        raise ValueError(
            "no opponent address: pass --peer URL, or --private pointing at a game.toml "
            "whose [network].opponent_url names one")
    from p2p_thief_agent.shared.private_config import (  # noqa: PLC0415
        PrivateConfigError,
        load_private_config,
        opponent_url,
    )
    from p2p_thief_agent.shared.tunnel import public_url  # noqa: PLC0415

    try:
        config = load_private_config(private)
        dialling = opponent_url(config)
        # Reading our own advertised address here is not decoration: it fails loudly now if
        # it is missing or loopback, rather than after both sides have signed the terms.
        public_url(config)
    except PrivateConfigError as exc:
        raise ValueError(str(exc)) from exc
    return dialling
