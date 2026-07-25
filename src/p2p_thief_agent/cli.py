"""Command-line entry point for the behavior-free package scaffold."""

from argparse import ArgumentParser
from collections.abc import Sequence

from p2p_thief_agent.shared import __version__


def build_parser() -> ArgumentParser:
    """Build the scaffold-only command-line parser."""
    parser = ArgumentParser(
        prog="p2p-thief",
        description="Inspect the P2P Thief package scaffold; no peer runtime is implemented.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Print scaffold help without starting game or network behavior."""
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0
