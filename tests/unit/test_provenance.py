"""`M9-010b`: the commit hash identifies the code that actually played.

The defect this closes is a shape worth naming. `running_git_commit()` was written for
`M4-006a`, fail-closes correctly, and **was called only from its own tests** — a correct
resolver that no production path reached. The reference implementation has the same defect
more visibly: it hard-codes `github_commit` to `"unknown"`, so the field is emitted, present
and identifying nothing.

Both failures are silent. The artifact validates, the key is there, and only the person
trying to re-run the match finds out. Rule 53 is Mandatory.

The second half is the one that is easy to miss: `git rev-parse HEAD` answers happily with
uncommitted changes on disk, so a resolved hash can be a truthful answer to the wrong
question. The code that ran was not the code at that commit.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.reporting.provenance import (
    describe_provenance,
    require_reproducible,
    working_tree_is_clean,
)
from p2p_thief_agent.shared.git_info import GitInfoError

SHA = "0123456789abcdef0123456789abcdef01234567"


def provenance(sha: str = SHA, status: str = "") -> dict:
    return describe_provenance(commit_runner=lambda: sha + "\n",
                               status_runner=lambda: status)


# --- resolving, not assuming ------------------------------------------------------------------


def test_the_commit_is_resolved_from_git() -> None:
    assert provenance()["github_commit"] == SHA


def test_a_clean_tree_is_reported_as_clean() -> None:
    assert provenance()["working_tree_clean"] is True


def test_a_dirty_tree_is_reported_rather_than_hidden() -> None:
    """`git rev-parse HEAD` answers happily either way, so without this the hash is a
    truthful answer to the wrong question."""
    assert provenance(status=" M src/thing.py\n")["working_tree_clean"] is False


def test_an_unresolvable_commit_raises_instead_of_returning_a_placeholder() -> None:
    """**The reference emits `"unknown"` here.** A placeholder satisfies every shape check,
    travels into the artifact, and is discovered by the one person who needed it."""
    with pytest.raises(GitInfoError):
        describe_provenance(commit_runner=lambda: "unknown", status_runner=lambda: "")


def test_a_git_failure_is_reported_as_a_git_error() -> None:
    def broken() -> str:
        raise OSError("git not found")

    with pytest.raises(GitInfoError, match="working tree state"):
        working_tree_is_clean(runner=broken)


# --- what a counted game requires --------------------------------------------------------------


def test_a_clean_resolved_provenance_is_accepted() -> None:
    require_reproducible(provenance())


def test_a_dirty_tree_is_refused_before_a_counted_game() -> None:
    """Fine while rehearsing, a broken audit trail once the game counts: the recorded
    commit does not contain the code that played."""
    with pytest.raises(GitInfoError, match="uncommitted changes"):
        require_reproducible(provenance(status="?? new_file.py\n"))


@pytest.mark.parametrize("bad", ["unknown", "", "abc123", SHA[:12], None, 42])
def test_anything_short_of_a_full_sha_is_refused(bad: object) -> None:
    """An abbreviated hash is ambiguous across a repository's lifetime, and `"unknown"` is
    the exact placeholder the reference ships."""
    with pytest.raises(GitInfoError, match="AE-53"):
        require_reproducible({"github_commit": bad, "working_tree_clean": True})


def test_a_missing_cleanliness_flag_is_not_read_as_clean() -> None:
    """`.get` returning `None` must not pass. An absent flag means nobody checked, which is
    not the same claim as a clean tree."""
    with pytest.raises(GitInfoError, match="uncommitted changes"):
        require_reproducible({"github_commit": SHA})


def test_the_real_repository_resolves_its_own_commit() -> None:
    """One test against real Git, so the injected-runner tests cannot all pass while the
    actual command is wrong."""
    resolved = describe_provenance()
    assert len(resolved["github_commit"]) == 40
    assert isinstance(resolved["working_tree_clean"], bool)
