"""Smoke tests for the scaffold command-line adapter."""

import pytest

from p2p_thief_agent.cli import main
from p2p_thief_agent.shared import __version__


def test_cli_prints_help_without_starting_runtime(capsys: pytest.CaptureFixture[str]) -> None:
    """The default command reports scaffold help and exits successfully."""
    assert main([]) == 0
    output = capsys.readouterr().out
    assert "no peer runtime is implemented" in output


def test_cli_reports_package_version(capsys: pytest.CaptureFixture[str]) -> None:
    """The version flag reads the sole shared version source."""
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])

    assert exit_info.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_cli_rejects_unknown_options() -> None:
    """Malformed scaffold commands fail clearly instead of starting anything."""
    with pytest.raises(SystemExit) as exit_info:
        main(["--unknown"])

    assert exit_info.value.code == 2
