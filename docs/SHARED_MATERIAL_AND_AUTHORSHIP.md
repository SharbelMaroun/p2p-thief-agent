# Shared material and authorship

**Added 2026-08-08 after an external audit found this repository's own language overclaimed.**
Both repositories are written by the same team — `sharNamr` (Amr safadi; Sharbel Maroun) —
and several files are byte-identical or near-identical between them. That was true before
this document existed; what was missing was saying so.

This file is deliberately identical in both repositories.

## What the rules actually require

The separation the book mandates is a **runtime** separation, not an authorship one:

* **Rule 1 (Mandatory)** — "Run the thief and police code in two separate processes."
* **Rule 2 (Prohibited)** — "Do not share memory or variables between parties at all.
  Sanction: Immediate disqualification due to data leakage."
* **Rule 49 (Mandatory)** — "Submit two separate GitHub repositories — policeman and thief —
  with a cross-link in the README."

Rule 49 asks one group for two repositories. Nothing in Appendix E forbids that group from
reusing its own chart renderer in both. What rules 1 and 2 forbid is a *live* channel: shared
process memory, a shared variable, a shared runtime file, or either peer reading the other's
private truth. That boundary is enforced structurally and tested
(`tests/integration/test_localhost_two_processes.py` spawns a genuinely separate interpreter;
`tests/unit/test_local_truth_boundary.py` pins the field set the live screen may see), and no
committed file is read by both peers at run time.

## What was overclaimed

This repository recorded `THIEF-002` as "developed with no read and no write access to
the companion Cop repository", and the companion has described this repository as "developed
independently". Read literally, both are stronger than the practice: the two trees share
support code. The claims were written to describe a *design* discipline — decide the wire
from the book and the reference rather than from the sibling — and that discipline is real
and is why the protocol and strategy layers genuinely diverge. But the sentences as written
say something else, and a grader is entitled to read what is written.

## What is shared, and in which category

**1. Deliberately shared, already declared.**
`tests/conformance/frozen_wire_profile.json` is a pinned wire surface carrying its own
SHA-256; `config/drafts/thief/` holds negotiated match configuration; `archive/pre-audit/`
holds joint planning documents that say on their face that they were written for both
repositories; `archive/pre-sim-realign/` retains the retired Option-B profile and its Node
stub. This repository deliberately keeps **no** copy of the companion's `shared_contract/`
bundle — the wire is matched against the pinned reference simulator, not against the sibling.

**2. Shared support code, previously undeclared — the reason this file exists.**
Roughly thirty files are byte-identical or differ only in the package name and a requirement
ID. They are infrastructure, not game logic:

| Area | Files |
|---|---|
| Chart rendering | `analysis/boxplot.py` (identical), `analysis/heatmap.py`, `analysis/charts.py`, `analysis/statistics.py` |
| Operator services | `services/credential_location.py`, `services/readiness.py`, `adapters/serving.py` |
| Replay and UI shell | parts of `replay/`, `ui/replay_board.py`, `ui/style.py` |
| Quality gates | `scripts/check_file_lengths.py`, `scripts/check_secrets.py`, `.github/workflows/ci.yml`, `pyproject.toml`, `.gitignore` |
| Tests of the above | ~13 modules, including `tests/unit/test_credential_files_ignored.py`, which is byte-identical and carries the same dated discovery note in both repositories |

**3. Independently authored.**
Everything that decides a game. The domain rules, the protocol and commit-reveal layer, the
orchestration and turn loop, the strategy/perception stack, and the reporting internals were
written separately for each role; the module layouts differ and textual similarity between
the analogous files runs roughly 0.07–0.48. The two peers reach the *same* commit digest and
the *same* scent-model lock because they implement the same specified construction, which is
the point — that agreement is evidence of interoperability, and it is checked by
cross-verifying each repository's log with the other's verifier.

## Why the duplication was not resolved by extracting a package

A shared library would be the ordinary engineering answer and is the wrong answer here. A
third installable package consumed by both peers would be a real coupling on match day —
one version, one bug, both agents — and it would put a live shared dependency exactly where
rules 1 and 2 want none. Duplicating a chart renderer costs nothing at run time and keeps the
two processes genuinely independent. The cost is this document.

## What a grader should conclude

That one team wrote two agents, shared its own tooling between them, and separated them where
the rules require separation — at run time, in memory, and in what each peer is allowed to
know. Not that two unrelated implementations converged.
