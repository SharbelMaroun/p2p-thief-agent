# Repository Audit and Branch Reconciliation

Audit date: 2026-07-25.

## Verified starting state

| Item | Result |
|---|---|
| `origin/main` | `119fa911d5b1a5aecdaa9531d0912e5c6f9ab32f` |
| `origin/Sharbel` | `e1103738ce3c0d9ab8232ebb93af65e59ef8af42` |
| Merge base | `7713004e0afe0fb47ac490fea3dc47e573f05484` |
| Divergence | main-only `3`; Sharbel-only `7` |
| Sharbel triple-dot inventory | `21` files: `5` added, `16` modified, `0` deleted |
| Merge simulation | Exactly five content conflicts listed below |
| Baseline implementation | `0` Python files, `0` tests, no `pyproject.toml`, no `uv.lock` |
| Preserved local evidence | Untracked `Material/`; never staged or modified |

The main-only commits `c856fa8` and `849c16e` provide direct Appendix E/F evidence and
generated-example JSON key observations. `119fa91` preserves the `849c16e` tree byte-for-byte.
`docs/JSON_ARTIFACT_SCHEMAS.md` is deliberately preserved.

## Five-conflict reconciliation

| Conflict | Chosen treatment | Rationale |
|---|---|---|
| `PRD_scent_belief.md` | Main evidence plus selective structure | Preserve fixed `AF-016` values and add the official multiplicative formula; reject branch “candidate” status and simulator subtractive decay |
| `PRD_strategy.md` | Main rule-25 nuance | Deterministic movement is the default/policy, but Appendix E labels the LLM guidance a recommendation without an automatic sanction |
| `REPOSITORY_AUDIT.md` | Recreate from both histories | Preserve main AF/JS evidence and add branch topology/classification; reject stale values/templates unknown and false parity claims |
| `SPECIFICATION_CONFLICTS.md` | Resolve row-by-row | Keep official emails/six-game evidence, close README/tag issues, and add schema-version, scent, LLM, and parity discrepancies |
| `UNKNOWN_REQUIREMENTS.md` | Narrow main's open questions | Remove verified values, addresses, filenames, README/tag and Ruff items; keep canonicalization, MCP, private config, formal template constraints, identity, and contract proposal open |

## Sharbel file classification

| Category | Files/content | Treatment |
|---|---|---|
| Useful and source-backed | Completeness matrix, GUI/replay tracking, submission categories, state-machine/watchdog acceptance structure | Recreated with direct citations |
| Useful but design/assumption | Bayesian strategy details, exact pipelines, simulator tool names, implementation frameworks | Retained only as open ADR/design topics |
| Stale | Appendix F values called candidates, email spelling conflict, README/tag unknowns, missing template structures | Replaced by main's stronger direct evidence |
| Dangerous to overwrite | `AF-013..022`, `JS-001..003`, `JSON_ARTIFACT_SCHEMAS.md`, rule-25 nuance, six-game series | Deliberately preserved |
| Deliberately not ported | “byte-identical already,” `rimesegal` aliases, hard LLM prohibition, one-game normative default, exact guessed canonical JSON | Rejected |

## Current M1 classification

| Area | State |
|---|---|
| Documentation | Reconciled active plan plus ten pending ADRs |
| Package | Behavior-free `p2p_thief_agent` SDK/CLI scaffold |
| Quality | uv lock, Ruff, branch coverage, length and secret gates |
| Runtime config | None; historical drafts remain quarantined |
| Shared contract | Revised `b586af9` was coordinator-reviewed but not authorized for Thief copying; later local `665bd30` is proposed/unreviewed; zero parity-controlled files copied |
| Simulator reuse | No runtime code copied |

Exact local check results are recorded in [M1_VERIFICATION.md](M1_VERIFICATION.md).

Documentation/scaffold completeness is not contract freeze, runtime completion, or
submission readiness.
