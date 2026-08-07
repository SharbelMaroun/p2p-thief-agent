"""Does the submission tag point at the commit that was reviewed (`M9-019`)?

Rule 41 wants an annotated `v1.0-submission` tag on the accepted submission commit — "not at
a later commit written after the deadline". The failure it guards is ordinary and hard to
see: you tag, then fix one more thing, then push. The tag still exists, the repository still
looks tidy, and it now names a commit that is not the one anybody reviewed.

Four things are checked, and the order is deliberate — each answers a different question a
grader could ask.

1. **The tag exists**, and is **annotated** rather than lightweight. An annotated tag carries
   its own author, date and message; a lightweight one is a bare pointer with no record of
   who made it or when, which is exactly the provenance the rule is asking for.
2. **It points at a commit reachable from the branch**, so it is part of the history that was
   pushed rather than an orphan.
3. **Nothing was committed after it** on that branch. This is the real check: a tag one commit
   behind the tip is the shape the mistake actually takes.
4. **The working tree is clean**, because a tag names a commit and a commit does not contain
   uncommitted work.

It cannot run before you tag, and that is fine — it prints what is missing and exits 1, which
is the right answer to "have I submitted correctly" when the answer is "not yet".
"""

from __future__ import annotations

import subprocess
import sys

TAG = "v1.0-submission"


def _git(*args: str) -> tuple[int, str]:
    done = subprocess.run(["git", *args], capture_output=True, text=True, errors="replace")
    return done.returncode, (done.stdout + done.stderr).strip()


def tag_exists(tag: str = TAG) -> bool:
    return _git("rev-parse", "--verify", f"refs/tags/{tag}")[0] == 0


def is_annotated(tag: str = TAG) -> bool:
    """An annotated tag is its own object; a lightweight one dereferences to the commit."""
    code, kind = _git("cat-file", "-t", tag)
    return code == 0 and kind.strip() == "tag"


def commits_after(tag: str = TAG, branch: str = "HEAD") -> list[str]:
    """Commits on `branch` that came after the tag — the check that earns its keep."""
    code, out = _git("rev-list", f"{tag}..{branch}", "--oneline")
    return [line for line in out.splitlines() if line.strip()] if code == 0 else []


def main() -> int:
    """Report whether the tag is submittable, naming the remedy for each failure."""
    if not tag_exists():
        print(f"no {TAG} tag yet. Create it when the submission commit is reviewed:\n"
              f"  git tag -a {TAG} -m 'Final submission: Police-Thief P2P, group sharNamr'\n"
              f"  git push origin {TAG}")
        return 1

    problems: list[str] = []
    if not is_annotated():
        problems.append(
            f"{TAG} is lightweight, not annotated. An annotated tag carries its own author, "
            f"date and message — the provenance rule 41 is asking for. Re-make it with "
            f"`git tag -f -a {TAG} -m '...'` [AE-41]")

    later = commits_after()
    if later:
        problems.append(
            f"{len(later)} commit(s) were made after {TAG}, so it no longer names the "
            f"reviewed state. Most recent: {later[0]}. Either move the tag deliberately and "
            "say so, or submit the tagged commit [AE-41]")

    dirty = _git("status", "--porcelain")[1]
    if dirty:
        problems.append(
            "the working tree has uncommitted changes; a tag names a commit, and a commit "
            "does not contain work that was never committed")

    if problems:
        print(f"{TAG} is not submittable:")
        print(*(f"  - {problem}" for problem in problems), sep="\n")
        return 1

    print(f"{TAG} OK: annotated, on the branch, nothing committed after it, tree clean.")
    print(_git("show", "--no-patch", "--format=%H %ad %s", TAG)[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
