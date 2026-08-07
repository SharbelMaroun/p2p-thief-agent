"""Which code played this game, resolved rather than assumed (`M9-010b`, rule 53).

`shared/git_info.running_git_commit()` has existed since `M4-006a` and fail-closes properly
— and **nothing outside the tests called it**. The resolver was correct and unreachable,
which is the same defect the reference implementation has in a more visible form: there,
`_subgame_entry` hard-codes `github_commit` to the string `"unknown"` for both sides, so the
field is emitted, is present in every artifact, and identifies nothing.

Rule 53 is Mandatory. A declaration that names the group, the hardware and the model but not
the code cannot be reproduced by anyone, and the failure is silent — the artifact validates,
the key is there, and only someone actually trying to re-run the match discovers it points
nowhere.

**A dirty working tree is reported, not hidden.** `git rev-parse HEAD` answers happily while
uncommitted changes sit on disk, so the hash can be a truthful answer to the wrong question:
the code that ran was not the code at that commit. `describe_provenance` records both, so an
auditor sees the difference instead of inferring it.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable

from p2p_thief_agent.shared.git_info import GitInfoError, running_git_commit


def _run_status() -> str:
    """Porcelain status: empty output means a clean tree."""
    completed = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                               text=True, check=True)
    return completed.stdout


def working_tree_is_clean(runner: Callable[[], str] = _run_status) -> bool:
    """Whether the tree matches HEAD. Injected, like every other external call here."""
    try:
        return not runner().strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise GitInfoError(f"could not read the working tree state: {exc}") from exc


def describe_provenance(
    *,
    commit_runner: Callable[[], str] | None = None,
    status_runner: Callable[[], str] | None = None,
) -> dict[str, object]:
    """The provenance block for an artifact: the commit, and whether it is the whole truth.

    Raises rather than returning a placeholder. `"unknown"` in this field is worse than a
    crash: it satisfies every shape check, travels into an emitted artifact, and is only
    discovered by the person who needed it.
    """
    commit = (running_git_commit(commit_runner) if commit_runner
              else running_git_commit())
    clean = (working_tree_is_clean(status_runner) if status_runner
             else working_tree_is_clean())
    return {"github_commit": commit, "working_tree_clean": clean}


def require_reproducible(provenance: dict[str, object]) -> None:
    """Refuse a provenance block that cannot identify what ran (`M9-010b`).

    Called before a **counted** game, not before a rehearsal: playing from a dirty tree is
    fine while practising and is a broken audit trail once the game counts, because the
    recorded commit does not contain the code that played.
    """
    commit = provenance.get("github_commit")
    if not isinstance(commit, str) or len(commit) != 40:
        raise GitInfoError(
            f"provenance carries no resolved commit ({commit!r}); rule 53 requires the "
            "commit hash of the code that played [AE-53]")
    if provenance.get("working_tree_clean") is not True:
        raise GitInfoError(
            f"the working tree has uncommitted changes, so commit {commit[:12]} does not "
            "contain the code about to play; commit or stash before a counted game [AE-53]")
