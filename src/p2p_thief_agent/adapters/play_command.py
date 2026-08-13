"""The `serve --peer` command body: resolve, optionally negotiate, play (`M9-026`).

Extracted from `cli.py` when the negotiated path (`M5-014f`) pushed the CLI past the
file-length gate. The CLI keeps parsing and dispatch; this module owns the one
user-facing flow that actually plays a match, so its messages are worded for the
operator at the terminal, not for a log file.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from p2p_thief_agent.shared.series_identity import series_game_id_from_private


def _audit_window(private: Path | None) -> float:
    """How long to stay reachable for the opponent's audit, from the private TOML.

    Never raises: a missing or unreadable private file falls back to the default window
    rather than refusing to play. The window is generous by design — see `post_match`.
    """
    from p2p_thief_agent.adapters.post_match import (  # noqa: PLC0415
        DEFAULT_AUDIT_WINDOW,
        audit_window_seconds,
    )

    if private is None:
        return DEFAULT_AUDIT_WINDOW
    try:
        from p2p_thief_agent.shared.private_config import load_private_config  # noqa: PLC0415

        return audit_window_seconds(load_private_config(private))
    except Exception:  # noqa: BLE001 - a config problem must not cost the audit window
        return DEFAULT_AUDIT_WINDOW


def _connect_budget(private: Path | None) -> float:
    """How long to wait for the opponent to answer, from the private TOML.

    The Cop has read ``[network].connect_timeout_seconds`` since M9; this side silently
    kept `serve_match`'s 30-second default, and that asymmetry ended the first amireman
    smoke at the role swap: their Police server was still rebinding for sub-game 2 when
    our 30 seconds ran out, and the whole series quit as "match did not start". Same
    never-raise contract as `_audit_window` — a config problem must not shrink the wait.
    """
    from p2p_thief_agent.services.readiness import (  # noqa: PLC0415
        DEFAULT_CONNECT_TIMEOUT,
        timeouts_from_private_config,
    )

    if private is None:
        return DEFAULT_CONNECT_TIMEOUT
    try:
        from p2p_thief_agent.shared.private_config import load_private_config  # noqa: PLC0415

        return timeouts_from_private_config(load_private_config(private))[0]
    except Exception:  # noqa: BLE001 - a config problem must not shrink the wait
        return DEFAULT_CONNECT_TIMEOUT


def _strategy(private: Path | None) -> dict:
    """Per-opponent strategy flags from the private TOML's ``[strategy]`` table.

    Private on purpose: these describe the OPPONENT's protocol profile (e.g. amireman's
    Cop claims its own cell every turn, so ``claim_reveals_cop`` turns that claim into
    pursuer intel), and never enter the signed terms. Same never-raise contract as the
    other private readers — a config problem costs the flag, not the match.
    """
    if private is None:
        return {}
    try:
        from p2p_thief_agent.shared.private_config import load_private_config  # noqa: PLC0415

        section = load_private_config(private).get("strategy")
        return dict(section) if isinstance(section, dict) else {}
    except Exception:  # noqa: BLE001 - a config problem must not cost the match
        return {}


def resolve_peer_address(peer: str | None, private: Path | None) -> str:
    """Decide which address to dial, from a flag or the private config (`M5-005`).

    Two sources on purpose: a flag while developing on one machine, a private TOML
    for league play, where the address is a tunnel URL and the token that created it
    must stay out of every shared file (book §2.4, `[AE-10]`). An explicit `--peer`
    wins over the file — the operator typing an address means that address.
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
        # Our own advertised address fails loudly now if missing or loopback, rather
        # than after both sides have signed the terms.
        public_url(config)
    except PrivateConfigError as exc:
        raise ValueError(str(exc)) from exc
    return dialling


def play(args: argparse.Namespace) -> int:
    """Play one match against the opponent named by `--peer` (or the private config).

    Separate from listening on purpose: a peer that always played would race an
    opponent still binding its port; one that never played is what the CLI was until
    `M9-026`.
    """
    from p2p_thief_agent.adapters.serve import (  # noqa: PLC0415
        ServeError,
        resolve_peer,
        serve_match,
    )
    from p2p_thief_agent.orchestration.thief_policy import make_decide  # noqa: PLC0415

    try:
        peer = resolve_peer(args.peer, args.private)
    except ValueError as exc:
        print(f"private config problem: {exc}")
        return 2
    if not peer:
        print("no opponent address: pass --peer URL, or --private with "
              "[network].opponent_url")
        return 2

    game_config = identity = None
    if args.game:
        from p2p_thief_agent.adapters.negotiated import (  # noqa: PLC0415
            NegotiatedServeError,
            load_negotiation_inputs,
        )

        try:
            game_config, identity = load_negotiation_inputs(
                args.game, args.private, f"http://{args.host}:{args.port}/mcp", peer)
        except NegotiatedServeError as exc:
            print(str(exc))
            return 2

    # Armed before the mailbox takes its first call, so the wire log covers negotiation —
    # the phase that failed opaquely against `uoh-ay26` on 2026-08-11.
    from p2p_thief_agent.services import wire_log  # noqa: PLC0415

    if wire_log.enable(Path(args.artifacts or ".") / "logs"):
        print(f"wire log: {wire_log.target()}")
    print(f"Thief on http://{args.host}:{args.port}, playing {peer} ...")
    # The decide callable carries its honest claim-answerer: both close over the same
    # position, so the answer given on the wire and the answer that ends our loop can
    # never disagree — the mismatch the audit would score as a forgery `[AE-021]`.
    decide = make_decide(
        threshold=args.threshold,
        claim_reveals_cop=bool(_strategy(args.private).get("claim_reveals_cop")),
    )
    try:
        result = serve_match(
            peer_url=peer, port=args.port, host=args.host,
            survival_threshold=args.threshold, decide=decide,
            answer_claim=decide.answer_claim,
            artifacts_dir=args.artifacts,
            game_config=game_config, identity=identity,
            sub_game=getattr(args, "sub_game", 1),
            ready_timeout=_connect_budget(args.private),
            audit_window=_audit_window(args.private),
            series_game_id=series_game_id_from_private(args.private),
        )
    except ServeError as exc:
        print(f"match did not start: {exc}")
        return 2
    print(f"match finished: {result.outcome} after {result.steps} step(s)")
    if args.artifacts:
        print(f"log written to {args.artifacts}")
    return 0
