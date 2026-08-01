"""Resolve the exact running Git commit for the Step-0 attestation (`M4-006a`, `AE-53`).

Appendix E rule 53 requires each game to record the exact Git commit that ran it, and
rule 24 seals that value pre-game. This resolver supplies it. The command is injected
(``runner``), the same discipline the deadline and watchdog modules use for time, so a
known SHA can be driven in a test without spawning Git.

Fail-closed: a commit that is wrong, empty, or unresolvable would make the per-game
commit hash meaningless, so anything but a clean 40-character lowercase hex SHA raises
rather than being sealed as if it were real.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable

_SHA = re.compile(r"[0-9a-f]{40}")


class GitInfoError(RuntimeError):
    """Raised when the running Git commit cannot be resolved to a clean SHA."""


def _run_git() -> str:
    """Return the raw output of ``git rev-parse HEAD`` (the running commit)."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def running_git_commit(runner: Callable[[], str] = _run_git) -> str:
    """Return the 40-hex SHA of the current HEAD, or raise ``GitInfoError``."""
    try:
        value = runner().strip().lower()
    except (OSError, subprocess.SubprocessError) as exc:
        raise GitInfoError(f"could not resolve the running git commit: {exc}") from exc
    if not _SHA.fullmatch(value):
        raise GitInfoError(f"unexpected git commit format: {value!r}")
    return value
