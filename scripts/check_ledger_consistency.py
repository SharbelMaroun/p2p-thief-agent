"""Hold the planning documents to each other (`G-010`..`G-014`).

Five ledger files describe the same project from different angles, and each of the `G-1x`
rows says "keep X consistent". Nothing was keeping them: a milestone finished in `TODO.md`
stayed `DEFERRED` in `PLAN.md`, and both read as current because each file is internally
coherent. The contradiction is only visible from outside, which is why it survived so long.

This is the same argument as `scripts/check_file_lengths.py`. A standing invariant that is
re-checked by hand is not an invariant; it is a hope with a row number.

Six checks. Five map to a `G` row; the sixth, unique task IDs, was added after a
duplicate was found by hand:

* `G-010` every document in `docs/` appears in `DOCS_COMPLETENESS.md` with a status
* `G-011` a milestone may not read `DONE` in `PLAN.md` while `TODO.md` still has open rows
  for it, or the reverse
* `G-012` a requirements row naming a test names one that exists
* `G-013` every `U-nnn` cited in `TODO.md` is registered, and every registered one says what
  it blocks
* `G-014` every ADR carries a status, and a superseded decision says so rather than being
  quietly rewritten

Exit 1 on any finding, so it can join the other gates in CI.

**The parsers are this repository's, not the Cop's.** The companion runs the same five
checks, but its `PLAN.md` puts the milestone state in column two and this one puts it in
column four, and its TODO rows carry a priority column that these do not. Sharing the code
would mean sharing a parser that is wrong for one of them; rule 2 forbids sharing runtime
state between the peers in any case, so each keeps its own.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"
OPEN_STATES = ("PENDING", "DEFERRED", "IN PROGRESS", "BLOCKED")
# Documents that exist to record a moment, not the current state. Listing a dated handoff or
# a one-off audit in a completeness table would mean re-dating it forever.
HISTORICAL = ("COORDINATOR_VERDICT", "STAGE_C_ACCEPTANCE", "GATE_RESOLUTION_REVIEW",
              "M1_VERIFICATION", "M2_DOMAIN", "M3_LOCAL_STATE")


def read(name: str) -> str:
    path = DOCS / name
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def check_docs_completeness() -> list[str]:
    """`G-010`. Every document present is listed, and every listed one has a status."""
    listed = read("DOCS_COMPLETENESS.md")
    findings = []
    for path in sorted(DOCS.glob("*.md")):
        if any(mark in path.name for mark in HISTORICAL) or path.name == "DOCS_COMPLETENESS.md":
            continue
        if path.name not in listed:
            findings.append(f"G-010: docs/{path.name} exists but DOCS_COMPLETENESS.md "
                            "does not list it")
    for row in re.findall(r"^\| `([^`]+)` \| *([^|]*)\| *([^|]*)\|", listed, flags=re.M):
        name, present, status = (cell.strip() for cell in row)
        if not status:
            findings.append(f"G-010: {name} is listed with no content status")
        if present.lower() == "yes" and not (DOCS.parent / name).exists():
            findings.append(f"G-010: {name} is listed as present but is not in the tree")
    return findings


def milestone_states() -> dict[str, str]:
    """Milestone → state as `PLAN.md` reports it."""
    rows = re.findall(r"^\| (M[0-9.]+) \|[^|]*\|[^|]*\| *`?([A-Z][A-Z ]*)",
                      read("PLAN.md"), flags=re.M)
    return {milestone: state.strip() for milestone, state in rows}


def open_milestones() -> set[str]:
    """Milestones with at least one row still open in `TODO.md`.

    A row counts as closed only if its state *begins* `DONE` or `SUPERSEDED`; anything else
    is open. The first version matched uppercase words instead, and silently skipped
    `M5-07c`, whose state is the sentence "BLOCKED — all code DONE; needs hardware + M8
    evidence". Unmatched meant uncounted, so the milestone read as finished — a checker
    failing open on the one row shaped unlike the others, which is the shape they take.
    """
    todo, still_open = read("TODO.md"), set()
    for milestone, state in re.findall(r"^\| (M[0-9.]+)-[\w.]+ \|[^|]*\| *([^|]*?) *\|",
                                       todo, flags=re.M):
        if not state.startswith(("DONE", "SUPERSEDED")):
            still_open.add(milestone)
    return still_open


def check_plan_matches_todo() -> list[str]:
    """`G-011`. The two files disagree in both directions, and both matter.

    A milestone `DONE` in the plan with open tasks overstates progress. One `DEFERRED` in
    the plan with every task closed understates it — which sounds harmless until a grader
    reads the plan and stops looking.
    """
    open_now, findings = open_milestones(), []
    for milestone, state in milestone_states().items():
        if state == "SUPERSEDED":
            continue
        if state == "DONE" and milestone in open_now:
            findings.append(f"G-011: PLAN.md calls {milestone} DONE, TODO.md still has open rows")
        if state in OPEN_STATES and milestone not in open_now:
            findings.append(f"G-011: PLAN.md calls {milestone} {state}, but every TODO.md row "
                            "for it is closed")
    return findings


def check_task_ids_are_unique() -> list[str]:
    """`G-011`. Two rows sharing an ID make the ledger unciteable.

    Found 2026-08-07: `M7-22e` named both a closed row and an open one, and the open row
    had its status and priority columns swapped, so it read as `P1` in the status position.
    A commit message, a conflict record or another task citing that ID resolves to whichever
    row the reader happens to find — and the closed one is the one that looks finished.
    """
    seen, findings = {}, []
    for task, state in re.findall(r"^\| ([MGX][\w.-]+) \|[^|]*\| *([^|]*?) *\|",
                                  read("TODO.md"), flags=re.M):
        if task in seen:
            findings.append(f"G-011: task id {task} is used twice "
                            f"({seen[task]!r} and {state[:20]!r})")
        seen[task] = state
    return findings


def check_requirements_have_tests() -> list[str]:
    """`G-012`. A row pointing at a test file must point at one that is there."""
    root, findings = DOCS.parent, []
    for name in re.findall(r"`(test_[\w./-]+\.py)`", read("REQUIREMENTS_LEDGER.md")):
        if not list(root.rglob(Path(name).name)):
            findings.append(f"G-012: REQUIREMENTS_LEDGER.md cites {name}, which does not exist")
    return findings


def check_unknowns_are_registered() -> list[str]:
    """`G-013`. Both directions: no dangling citation, no unknown that blocks nothing."""
    unknowns, todo, findings = read("UNKNOWN_REQUIREMENTS.md"), read("TODO.md"), []
    registered = set(re.findall(r"\b(U-\d{3})\b", unknowns))
    for cited in sorted(set(re.findall(r"\b(U-\d{3})\b", todo)) - registered):
        findings.append(f"G-013: TODO.md cites {cited}, which UNKNOWN_REQUIREMENTS.md "
                        "does not register")
    for row in re.findall(r"^\| (U-\d{3}) \|[^|]*\| *([^|]*)\|", unknowns, flags=re.M):
        if not row[1].strip():
            findings.append(f"G-013: {row[0]} does not say what it blocks")
    return findings


def check_adrs_have_status() -> list[str]:
    """`G-014`. A decision that changed is marked superseded, never silently edited."""
    findings = []
    for adr in sorted((DOCS / "adr").glob("0*.md")):
        text = adr.read_text(encoding="utf-8")
        if not re.search(r"^\s*(?:[-*>#\s]*)?\**Status\**\s*[:|]", text, flags=re.M | re.I):
            findings.append(f"G-014: {adr.name} carries no Status line")
        elif re.search(r"supersed", text, flags=re.I) and not re.search(
                r"Status\**\s*[:|]\s*\**\s*(?:Superseded|Accepted|Amended)", text, flags=re.I):
            findings.append(f"G-014: {adr.name} discusses supersession but its status does "
                            "not record one")
    return findings


def main() -> int:
    """Run every check and report each finding on its own line."""
    findings = (check_docs_completeness() + check_plan_matches_todo()
                + check_task_ids_are_unique()
                + check_requirements_have_tests() + check_unknowns_are_registered()
                + check_adrs_have_status())
    if findings:
        print(f"{len(findings)} ledger inconsistenc{'y' if len(findings) == 1 else 'ies'}:")
        print(*(f"  - {finding}" for finding in findings), sep="\n")
        return 1
    print("Ledger consistency OK: docs listed, plan matches TODO, unknowns registered, "
          "ADRs statused.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
