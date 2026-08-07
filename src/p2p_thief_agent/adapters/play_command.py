"""The `serve --peer` command body: resolve, optionally negotiate, play (`M9-026`).

Extracted from `cli.py` when the negotiated path (`M5-014f`) pushed the CLI past the
file-length gate. The CLI keeps parsing and dispatch; this module owns the one
user-facing flow that actually plays a match, so its messages are worded for the
operator at the terminal, not for a log file.
"""

from __future__ import annotations

import argparse
from pathlib import Path


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

    print(f"Thief on http://{args.host}:{args.port}, playing {peer} ...")
    # The decide callable carries its honest claim-answerer: both close over the same
    # position, so the answer given on the wire and the answer that ends our loop can
    # never disagree — the mismatch the audit would score as a forgery `[AE-021]`.
    decide = make_decide(threshold=args.threshold)
    try:
        result = serve_match(
            peer_url=peer, port=args.port, host=args.host,
            survival_threshold=args.threshold, decide=decide,
            answer_claim=decide.answer_claim,
            artifacts_dir=args.artifacts,
            game_config=game_config, identity=identity,
        )
    except ServeError as exc:
        print(f"match did not start: {exc}")
        return 2
    print(f"match finished: {result.outcome} after {result.steps} step(s)")
    if args.artifacts:
        print(f"log written to {args.artifacts}")
    return 0
