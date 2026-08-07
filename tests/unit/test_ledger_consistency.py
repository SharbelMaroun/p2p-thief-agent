"""`G-010`..`G-014`: the planning documents agree with each other, and stay agreeing.

Each of those rows says "keep X consistent", and nothing was keeping them. The invariants
span documents, which is why they broke quietly: `DOCS_COMPLETENESS.md` was 29 rows behind —
last reviewed while this was still an M1 scaffold — and `TODO.md` cited three `U-nnn` numbers
this repository's register never carried. Every line in both files was individually correct.
No single-file review catches that.

The tests run the real checks against the real repository rather than fixtures. A fixture
proves the parser works on data written to suit it; only this repository can show the
documents are consistent right now.
"""

from __future__ import annotations

from scripts.check_ledger_consistency import (
    check_adrs_have_status,
    check_docs_completeness,
    check_plan_matches_todo,
    check_requirements_have_tests,
    check_task_ids_are_unique,
    check_unknowns_are_registered,
    main,
    milestone_states,
    open_milestones,
)


def test_this_repository_is_consistent() -> None:
    """The gate. Its message names the file and the fix, because whoever reads a failure
    here is usually not whoever wrote the inconsistency."""
    assert main() == 0


def test_a_milestone_is_never_done_here_and_open_there() -> None:
    assert check_plan_matches_todo() == []


def test_every_document_is_listed_with_a_status() -> None:
    assert check_docs_completeness() == []


def test_no_task_cites_an_unregistered_unknown() -> None:
    """**The break this found.** `M9-020b` claims to list every unresolved unknown while
    citing `U-033`/`U-034`, which resolved in the companion repository and nowhere here — so
    a reader of *this* repository followed a reference to nothing."""
    assert check_unknowns_are_registered() == []


def test_the_remaining_two_checks_are_clean() -> None:
    assert check_requirements_have_tests() == []
    assert check_adrs_have_status() == []


def test_the_parse_is_not_vacuous() -> None:
    """Both sides of the comparison must find rows: two empty sets agree with each other."""
    assert len(milestone_states()) >= 1
    assert len(open_milestones()) >= 1

def test_every_milestone_in_the_todo_is_found_in_the_plan() -> None:
    """**The gap this closes.** The plan parser silently dropped two milestones whose state
    cell carried trailing prose after the state word: unmatched meant unchecked, so those
    milestones were never compared at all and the run still reported OK. A checker that
    quietly covers less than it claims is worse than one that fails.
    """
    import re

    from scripts.check_ledger_consistency import read

    in_todo = set(re.findall(r"^\| (M[0-9.]+)-[\w.]+ \|", read("TODO.md"), flags=re.M))
    missing = sorted(in_todo - set(milestone_states()))
    assert not missing, f"PLAN.md states were not parsed for {missing}"

def test_no_task_id_is_used_twice() -> None:
    """**Found by hand, then made permanent.** `M7-22e` named both a closed row and an open
    one, and the open row's status and priority columns were swapped so it read `P1` where
    the status belongs. Anything citing that ID resolved to whichever row the reader found
    first — and the closed one is the one that looks finished."""
    assert check_task_ids_are_unique() == []
