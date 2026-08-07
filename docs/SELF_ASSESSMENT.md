# Code-quality self-assessment

Covers `M9-009`, `M9-009a`, `M9-009b`, `M9-022`.

Scored against the submission guidelines' own requirements. **The score is only worth
something if it can go down**, so the section that matters is the second one — what is not
met, and why. A self-assessment claiming full marks everywhere tells a grader nothing they
could not have assumed.

Scale: **2** = met with evidence a third party can check · **1** = partially met · **0** = not met.

## Scored against the guidelines — `M9-009a`

| # | Guidelines requirement | Score | Evidence, and the reservation |
| --- | --- | :---: | --- |
| 1 | `docs/PRD.md` present and complete | 2 | Plus a PRD per mechanism (§2.3): commit-reveal, p2p_mcp, gatekeeper_reporting, strategy, scent_belief, gui, replay |
| 2 | `docs/PLAN.md` with architecture and ADRs | 1 | Present with ADRs, **but the C4 and UML diagrams §2.2 asks for are prose and tables, not diagrams** |
| 3 | `docs/TODO.md` with priorities, status, DoD | 2 | Every row carries a definition of done and an evidence string; 78 M9 rows tracked individually |
| 4 | Comments explain the *why*, not the *what* | 2 | Enforced by review rather than a tool. Module docstrings carry the rule and its sanction, not a restatement of the code |
| 5 | Docstrings on every module and function | 2 | Ruff `D` rules in the pinned select set; zero findings |
| 6 | Automated tests with meaningful coverage | 2 | 1428 tests, 99.26% branch against an 85% floor. Guards are proven to bite by injecting the defect they catch |
| 7 | Linting at zero findings | 2 | `ruff check .` clean; the select set is pinned, not default |
| 8 | Reproducible install | 2 | `uv.lock`, `uv sync --frozen`, verified from a clean clone by `scripts/verify_clean_clone.py` |
| 9 | CI runs every gate on every push | 2 | `.github/workflows/ci.yml`. **Was 1 until 2026-08-07** — the history scanner existed and CI never ran it |
| 10 | No secrets in the repository | 2 | Scanner over the working tree *and* every blob in history; 1744 objects, 0 findings; `.gitignore` covers every credential path |
| 11 | Standard project structure | 2 | `src/` layout, `docs/`, `scripts/`, `tests/{unit,integration,conformance}` |
| 12 | Maintainability — modular, analysable | 1 | 150-line cap holds, but **some splits were made to satisfy the cap rather than for cohesion** |
| 13 | Portability | 1 | Frozen install verified from a clean clone, **Windows only — never run on Linux or macOS** |
| 14 | Prompt-engineering log | 2 | `docs/PROMPT_LOG.md`, updated per significant batch |
| 15 | Performance evidence | 1 | Benchmarks and a research report exist; **no profiling against an adversarial peer** |

**Total: 26 / 30.**

## What is not met, and why — `M9-009b`

**Diagrams (#2, scored 1).** Guidelines §2.2 asks for C4 model diagrams, UML for complex
processes, and deployment diagrams. `docs/PLAN.md` describes the architecture in prose and
tables. The information is there and the *form* the guidelines asked for is not. Honest reason:
diagrams were never prioritised over behaviour, and saying "the content is equivalent" would
be deciding on the grader's behalf what the requirement meant.

**Cohesion versus the line cap (#12, scored 1).** The 150-line rule is a real quality gate and
it has a real cost. Several modules in this batch were split at the point the counter
complained rather than at the point the concept changed — `test_evidence.py` became three
files partly for that reason. Where a split produced a genuinely better seam it is noted in
the module docstring; where it did not, the docstring says which file it was cut from.

**Portability (#13, scored 1).** Everything runs on Windows 11 and has never run anywhere
else. `uv.lock` and the clean-clone check make a Linux run *likely* to work; likely is not
evidence. `M9-013a` stays open, and no claim of cross-platform support appears in the README.

**Performance (#15, scored 1).** `docs/RESEARCH-REPORT-Performance-Analysis.md` reports real
measurements over real runs, but every one is against our own peer or a synthetic opponent. An
adversarial classmate could produce latency and queue behaviour none of it predicts.

**Related open weakness, not on the guidelines list.** `M6-015c`: our evasion metric counts
total survival steps while Appendix F pays only for reaching the threshold or being captured.
Over 24 perimeter openings the ranking reverses. The row is open and the report discloses it.

## What the score does not cover

Two of the strongest properties in this repository have no line above, because the guidelines
do not ask for them:

* **Guards are proven to bite.** Caching a replay verdict fails 5 navigation tests; renaming a
  frozen wire method fails 2 conformance tests; the `ended_at` guard broke 13 fixtures when
  added. A test that passes both with and without the code it guards is decoration.
* **Refusals carry the rule and its sanction.** An operator reading `[AE-38]` learns that a
  false game count disqualifies the project, rather than learning that a number did not match.

## Final self-assessed score — `M9-022`

**26 / 30 (87%).** Four requirements at partial credit, none at zero. The two that would cost
most to fix late are portability and diagrams; both are recorded here rather than discovered
by a grader.
