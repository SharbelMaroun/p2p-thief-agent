# Plan

Status: M0 documentation reconciliation; M1 contract-and-scaffold parity gate pending.

At baseline `119fa911d5b1a5aecdaa9531d0912e5c6f9ab32f`, implementation had not
begun: there were no Python files, tests, `pyproject.toml`, or `uv.lock`.

## Layer plan

```text
CLI / future GUI / future MCP adapters
                 |
             public SDK
                 |
domain + orchestration + services + strategy
                 |
 future protocol/config/external adapters
```

The M1 source tree establishes these boundaries without runtime behavior. Every future
external entry point delegates through the SDK (`PS-007`); Cop and Thief remain
independently installable with no runtime filesystem dependency (`SR-004`,
`THIEF-001`).

## Gated milestones

| Gate | Scope | Entry condition | Exit evidence |
|---|---|---|---|
| M0 | Evidence and branch reconciliation | Verified `origin/main` and branch topology | Five-conflict table, preserved `AF`/`JS` evidence |
| M1 | First implementation gate: package scaffold plus contract parity | M0 complete; Cop proposal may proceed in parallel | Frozen uv install, SDK/CLI tests and quality gates **and** accepted bytes copied verbatim with matching hashes |
| M2 | Thief domain foundation | Entire M1 gate passed | Immutable coordinates/actions/grid, legal movement and capture rules with unit tests |
| M3 | Local Thief state and strategy | M2 passed | Local history, known barriers, deterministic survival policy with tests |
| M4+ | Protocol and integrations | Relevant ADRs accepted and unknowns closed | Separate gated FastMCP, crypto, scent, GUI/replay, LLM and reporting increments |

An unknown blocks only the affected gate. Package and documentation work is not
blanket-blocked by unresolved runtime protocol fields.

## Contract consumption

The Cop agent is the proposal owner for parity-controlled files during this milestone.
The Thief agent reviews sources and fields, copies accepted files byte-for-byte, and
verifies the Cop manifest. This workflow does not make Cop authoritative at runtime.
If the proposal is absent or unsupported, M1 stays partially complete and `PENDING`; no replacement
schema, tool list, fixture, or config is invented.

## Architectural decisions

Decision placeholders are indexed in [adr/README.md](adr/README.md):

1. MCP contract.
2. Message envelope and idempotency.
3. Schema-version discrepancy.
4. Shared JSON and private TOML.
5. Scent model.
6. Commit-reveal canonicalization.
7. LLM movement policy.
8. Simulator reuse and license.
9. GUI truth model.
10. Gmail reporting.

No placeholder is an accepted runtime decision. Each requires cited evidence, a
decision owner, tests, and compatible Cop/Thief treatment where applicable.

## Verification sequence

1. Lock dependencies with uv.
2. Sync from the committed lock in a clean environment.
3. Run Ruff with zero findings.
4. Run all tests with branch coverage at least 85%.
5. Enforce source/test file-size limits.
6. Scan tracked project material for secret patterns.
7. Validate accepted contract fixtures and hashes when the Cop proposal exists.
8. Confirm source contains no lecturer-simulator runtime code.

The task ledger, ownership, priorities, traceability, and Definitions of Done are in
[TODO.md](TODO.md).
