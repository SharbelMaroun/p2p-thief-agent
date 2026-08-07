"""Smoke tests for the command-line adapter: it answers without starting anything.

These three predate the runtime and were written against the scaffold. One of them asserted
the literal phrase "no peer runtime is implemented" — it was **pinning the absence**, and
`M9-025` made it false on 2026-08-07. Rewritten rather than deleted, because the property it
was really protecting still matters and is easy to lose: *invoking the CLI with no subcommand
must answer and start nothing.*

The behavioural detail of `serve`, `replay` and `verify` lives in
`tests/unit/test_cli_runtime.py`. These stay at the level of "the entry point is wired and
harmless when asked a question".
"""

import pytest

from p2p_thief_agent.cli import main
from p2p_thief_agent.shared import __version__


def test_cli_prints_help_without_starting_a_runtime(capsys: pytest.CaptureFixture[str]) -> None:
    """A bare invocation is a question, not an instruction to bind a port."""
    assert main([]) == 0
    output = capsys.readouterr().out
    assert "usage: p2p-thief" in output
    for subcommand in ("serve", "replay", "verify"):
        assert subcommand in output, f"{subcommand} is no longer advertised in help"


def test_cli_reports_package_version(capsys: pytest.CaptureFixture[str]) -> None:
    """The version flag reads the sole shared version source."""
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])

    assert exit_info.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_cli_rejects_unknown_options() -> None:
    """A malformed command fails clearly instead of starting anything."""
    with pytest.raises(SystemExit) as exit_info:
        main(["--unknown"])

    assert exit_info.value.code == 2
