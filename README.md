# P2P Thief Agent

Independently installable Thief-side package for the “Distributed Cops-and-Robbers over
a Peer-to-Peer Network” university project.

Companion Cop repository:
<https://github.com/SharbelMaroun/p2p-cop-agent>

## Milestone status

M0 and M2 are `DONE`. M1 is `IN PROGRESS` at the Thief-authored conformance
profile. M3–M9 are `PENDING` and proceed sequentially; unresolved choices are raised
explicitly rather than classified as blockers.

Version `1.00` began as an M0–M1 documentation and package scaffold. The inspected
baseline (`119fa911d5b1a5aecdaa9531d0912e5c6f9ab32f`) contained no Python package,
tests, `pyproject.toml`, or lockfile; that milestone added those engineering
foundations.

The M2 core domain — coordinates, board geometry, legal movement, barrier rules, and
capture conditions — is now implemented behind the public SDK under the 2026-07-28
coordinator authorization for contract-independent domain work. It uses only Appendix
E/F `CONFIRMED` rules, takes every board and position input explicitly, and depends on
no shared-contract byte, MCP endpoint, or Cop-owned file. See
[M2_DOMAIN.md](docs/M2_DOMAIN.md).

The repository still deliberately implements no live peer runtime, commit-reveal state
machine, LLM, Gmail, GUI, or replay behavior.

Earlier Cop-bundle reviews are retained as historical audit evidence only. No
peer-owned file was integrated, and those bundles are not inputs to the current
Thief-authored conformance workflow. The dated findings remain in
[COORDINATOR_VERDICT_2026-07-28.md](docs/COORDINATOR_VERDICT_2026-07-28.md) and
[CONTRACT_REVIEW.md](docs/CONTRACT_REVIEW.md).

On 2026-07-28 the copy model was **superseded**. Under `THIEF-002` this repository has
no access to the companion Cop repository and must play unknown classmate opponents, so
byte-parity with one peer would prove nothing about interoperability. M1 is now a
conformance gate: the Thief authors its own wire profile from book-confirmed rules and
Option-B choices, and proves it bidirectionally against a neutral stub opponent sharing
no source file with any peer. See
[CONTRACT_HANDOFF_CHECKLIST.md](docs/CONTRACT_HANDOFF_CHECKLIST.md).

## Install and inspect

Python 3.10 or newer and
[uv](https://docs.astral.sh/uv/) are required.

```text
uv sync --frozen
uv run p2p-thief --help
```

The command exposes scaffold metadata and help only. It does not start a peer or a
game.

## Quality gates

```text
uv run ruff check .
uv run pytest --cov --cov-branch --cov-fail-under=85
uv run python scripts/check_file_lengths.py
uv run python scripts/check_secrets.py
uv run python scripts/check_shared_contracts.py
```

The conformance checker remains fail-closed at `PENDING` until an exact accepted
profile revision is recorded. This is honest incomplete evidence, not a blocker on
profile or conformance work.

## Confirmed boundaries

- Cop and Thief are separate processes and repositories with no shared memory, database,
  runtime filesystem, or private truth (`SR-001`, `SR-004`, `THIEF-001`).
- This repository is developed with no read and no write access to the companion Cop
  repository, and must interoperate with an **unknown** opponent (`THIEF-002`). League
  play is against classmates, so matching one companion repository is evidence about
  that repository only. Interoperability is demonstrated against a neutral stub sharing
  no files with either side.
- Legal moves are north, south, east, west, and stay; diagonals are illegal
  (`AF-015`).
- Barrier placement is disclosed; a barrier on the Thief’s current cell and a trapped
  Thief are captures (`AE-015`, `AE-046`).
- SHA-256 commit-reveal, secret nonces until reveal, explicit state machines,
  illegal-transition rejection, deadlines, watchdogs, and public tunneling are required
  (`AE-004`, `AE-006`, `AE-010`, `AE-017`).
- Live GUI information is local truth only (`AE-008`).
- Appendix F values are recorded as `AF-013`–`AF-022`; artifact-example key-set
  observations are recorded as `JS-001`–`JS-003`, with provenance still unresolved.
- Deterministic movement is the project default. Appendix E rule 25 is a
  recommendation, not an automatic mandatory sanction (`AE-025`).

See the [requirements ledger](docs/REQUIREMENTS_LEDGER.md), [verified parameter
baseline](docs/PARAMETERS_BASELINE.md), [JSON artifact evidence](docs/JSON_ARTIFACT_SCHEMAS.md),
[book/template reconciliation](docs/BOOK_TEMPLATE_RECONCILIATION.md),
[proposed gate-resolution review](docs/GATE_RESOLUTION_REVIEW.md),
[unknowns](docs/UNKNOWN_REQUIREMENTS.md), [conflicts](docs/SPECIFICATION_CONFLICTS.md),
[repository audit](docs/REPOSITORY_AUDIT.md), [independent contract
review](docs/CONTRACT_REVIEW.md), [contract handoff
checklist](docs/CONTRACT_HANDOFF_CHECKLIST.md), and
[M1 verification record](docs/M1_VERIFICATION.md).

## Architecture boundary

All future business behavior must be reachable through the public SDK. CLI, GUI, MCP
transport, and external integrations may adapt inputs and outputs but may not contain or
duplicate business logic. The present package exposes the implemented M2 domain and
deterministic baseline through the SDK; protocol, orchestration, service, and UI
packages remain explicit boundaries for their later milestones.

Historical configurations remain quarantined under `config/drafts/`; runtime code must
not load them. Local private TOML and real `.env` files are ignored.

## License and provenance

The [MIT license](LICENSE) covers team-authored material where legally valid.
Lecturer-provided documents and simulator code are not automatically relicensed. No
lecturer simulator runtime code is included in this scaffold.
