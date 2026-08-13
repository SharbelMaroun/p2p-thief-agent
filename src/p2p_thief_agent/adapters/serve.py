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
    audit_window: float = 60.0,
    series_game_id: str,
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
    from p2p_thief_agent.services.limits import call_timeout_sec  # noqa: PLC0415
    from p2p_thief_agent.services.readiness import turn_timeout, wait_for_peer  # noqa: PLC0415

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

    # Bound every outbound call (`M9-27`). Left unset the client waits forever, and two tries
    # plus a backoff quietly outlive the deadline we signed -- see `services.limits.call_timeout_sec`,
    # which lives there rather than beside `RetryPolicy` because `adapters` importing
    # `services.deadlines` is a subsystem link the orchestrator boundary forbids. It falls back
    # to Appendix F's defaults before a config is agreed, bounding the unnegotiated path too.
    client = FastMCPClient(peer_url, timeout=call_timeout_sec(game_config))
    threshold = survival_threshold
    agreement = None
    started_at = None
    if game_config is not None:
        # `M5-014f` on the playable path: agree before the first move. The companion
        # Cop refuses an unnegotiated game, and so does the book.
        from datetime import UTC, datetime  # noqa: PLC0415

        from p2p_thief_agent.adapters import negotiated  # noqa: PLC0415

        NegotiatedServeError = negotiated.NegotiatedServeError  # noqa: N806
        negotiated_agreement = negotiated.negotiated_agreement
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
    # `M5-010`, wired 2026-08-09: over a tunnel a single 502 is a blip, not a decision
    # (rules 6/7). `delivery.deliver` was built for exactly this and had no production
    # call site until now, so one transient fault on any turn ended the sub-game 0/0.
    # The audit must open with a sealed step-0 `system_spec` record; peers reject an audit
    # without it "at steps [0]" (agreed with uoh-ay26 2026-08-12). It rides the audit only,
    # never the log, and `build_step_zero` returns None rather than raising if it cannot.
    from p2p_thief_agent.adapters.step_zero import build_step_zero  # noqa: PLC0415
    from p2p_thief_agent.orchestration.delivery import retrying_deliver  # noqa: PLC0415
    from p2p_thief_agent.orchestration.polling import poll_for_turn  # noqa: PLC0415

    step_zero = build_step_zero(identity, game_config, sub_game)
    records: list[dict] = []
    result = run_sub_game_over_wire(
        machine=PhaseMachine(),
        transport=client,
        receive=lambda: poll_for_turn(
            lambda: _take(inboxes), clock=time.monotonic, sleep=sleep,
            timeout=turn_timeout(game_config, ready_timeout)),
        decide=decide,
        answer_claim=answer_claim,
        survival_threshold=threshold,
        records=records,
        deliver=retrying_deliver(game_config, sleep, clock=time.monotonic),
        step_zero=step_zero,
    )
    # Rule 36: the mutual audit is a condition of agreement, and an agreement needs two
    # peers present. Exiting here is what turned a clean 35-step survival into 0/0 against
    # `uoh-ay26` on 2026-08-11 — their `submit_audit` met a 502 and they recorded a
    # technical loss. See `post_match` for the whole account.
    from p2p_thief_agent.adapters.post_match import finalise  # noqa: PLC0415

    finalise(
        inboxes=inboxes, artifacts_dir=artifacts_dir, records=records, result=result,
        agreement=agreement, game_config=game_config, identity=identity,
        sub_game=sub_game, started_at=started_at, audit_window=audit_window,
        sleep=sleep, clock=time.monotonic, write_log=_write_log,
        series_game_id=series_game_id,
    )
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


def _write_log(directory: Path, records: list[dict], result: object,
               context: Mapping[str, object] | None = None) -> Path:
    """Write the finished log; the body lives in `adapters/match_log.py` (length gate)."""
    from p2p_thief_agent.adapters.match_log import write_match_log  # noqa: PLC0415

    return write_match_log(directory, records, result, context)


def resolve_peer(peer: str | None, private: Path | None) -> str:
    """Decide which address to dial; the body lives in `play_command` (length gate)."""
    from p2p_thief_agent.adapters.play_command import resolve_peer_address  # noqa: PLC0415

    return resolve_peer_address(peer, private)
