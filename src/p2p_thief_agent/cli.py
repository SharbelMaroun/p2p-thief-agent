"""Command-line entry point for the Thief peer (`M9-025`).

Until 2026-08-07 this was a scaffold: `--help`, `--version`, and a description that said
"no peer runtime is implemented". Everything underneath was finished and exercised — a
six-sub-game series runs in `tests/integration/`, two OS processes play over localhost, the
replay verifier re-checks a stored match — but **a grader who cloned the repository could not
start anything.** The gap was the wiring, not the behaviour.

Three subcommands, each a thin adapter over code that already existed:

* `serve` — start this peer's mailbox and wait for an opponent (`adapters/serving.py`).
* `replay` — re-verify a stored log and print the banner (`replay/`). This is rule 20's
  threshold condition and the source of the mandatory `Verified OK` screenshot.
* `verify` — the gate form of `replay`: no output but a verdict, and a **non-zero exit** on
  `TAMPERED`, so it can sit in a pipeline.

**`build_parser` imports no transport.** Every runtime import is inside the function that
needs it, so `--version` and `--help` work on a machine where FastMCP is not installed and
cannot fail for a reason that has nothing to do with what was asked. The companion Cop
repository settled on the same rule independently; it is one of the few places both CLIs
agree exactly.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from p2p_thief_agent.shared import __version__

DEFAULT_PORT = 8801
_DESCRIPTION = (
    "Thief peer command line. `serve` starts this peer's mailbox and waits for an "
    "opponent; `replay` re-verifies a stored match log and prints its banner; `verify` is "
    "the same check with an exit code instead of output."
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser. Imports nothing from `adapters/` — see the module docstring."""
    parser = argparse.ArgumentParser(prog="p2p-thief", description=_DESCRIPTION)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command")

    serve = sub.add_parser("serve", help="start this peer's mailbox and await an opponent")
    serve.add_argument("--port", type=int, default=DEFAULT_PORT,
                       help=f"port to bind the inbound mailbox (default {DEFAULT_PORT})")
    serve.add_argument("--host", default="127.0.0.1",
                       help="bind address; defaults to loopback rather than 0.0.0.0")
    serve.add_argument("--name", default="p2p-thief", help="server name reported to the peer")

    for name, help_text in (("replay", "re-verify a stored log and print its banner"),
                            ("verify", "re-verify a stored log; exit non-zero if tampered")):
        node = sub.add_parser(name, help=help_text)
        node.add_argument("--log", required=True, type=Path,
                          help="path to a log artifact, including an opponent's")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Dispatch a subcommand, or print help when none is given."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "serve":
        return _serve(args)
    if args.command in {"replay", "verify"}:
        return _replay(args.log, quiet=args.command == "verify")
    parser.print_help()
    return 0


def _replay(log_path: Path, *, quiet: bool) -> int:
    """Re-verify one stored log. Rule 20's threshold condition, from a terminal.

    Loads **by path**, which is rule 36's mutual-audit posture: an opponent hands over a
    file, not a Python object, so this works unchanged on their log and on ours.
    """
    from p2p_thief_agent.replay.load import LogNotReplayableError, load_log  # noqa: PLC0415
    from p2p_thief_agent.replay.verify import Verdict, verify_records  # noqa: PLC0415

    # Checked before loading, because `load_log` raises `LogNotReplayableError` for an
    # absent file as well as for an in-play one — and those need different reactions. "Not
    # replayable" here means a log whose nonces are still withheld under rule 18: a
    # legitimate mid-game state that the operator should wait out. A path that does not
    # exist is a typo. Reporting the second as the first sends someone to read the rules
    # when they should be reading their shell history.
    if not log_path.is_file():
        print(f"could not read {log_path}: no such file")
        return 2
    try:
        log = load_log(log_path)
    except LogNotReplayableError as exc:
        # Refused, not accused. A log without nonces is incomplete, not forged, and rule
        # 19's sanction lands on whoever is accused of forging.
        print(f"not replayable: {exc}")
        return 2
    except (OSError, ValueError) as exc:
        print(f"could not read {log_path}: {exc}")
        return 2

    verdict = verify_records(log.records)
    if not quiet:
        print(verdict.banner)
    return 0 if verdict.verdict is Verdict.VERIFIED_OK else 1


def _serve(args: argparse.Namespace) -> int:
    """Start the inbound mailbox and hold the process open until interrupted.

    Serving and *playing* are separate on purpose. This peer opens every turn cycle (the
    book gives the Thief the first move), so a launcher that immediately started playing
    would race an opponent still binding its own port. `services/readiness` exists for that
    handshake; until an opponent address is negotiated there is nothing to open against.
    """
    from p2p_thief_agent.adapters.fastmcp_server import PeerInboxes  # noqa: PLC0415
    from p2p_thief_agent.adapters.serving import ServingError, serve_in_background  # noqa: PLC0415

    inboxes = PeerInboxes()
    try:
        serve_in_background(inboxes, port=args.port, host=args.host, name=args.name)
    except ServingError as exc:
        print(f"could not start the mailbox: {exc}")
        return 2

    print(f"Thief mailbox listening on http://{args.host}:{args.port} (Ctrl-C to stop)")
    print("Waiting for an opponent. Queue depth is bounded — a flooded inbox refuses "
          "rather than growing [AE-29].")
    try:
        _block_until_interrupted()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


def _block_until_interrupted() -> None:
    """Park the main thread. Extracted so a test can drive `_serve` without blocking."""
    import threading  # noqa: PLC0415

    threading.Event().wait()
