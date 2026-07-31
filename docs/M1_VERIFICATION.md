# M1 Verification Record

Run date: 2026-07-25

Working branch: `agent/thief-m0-m1-reconcile-scaffold`

Starting main: `119fa911d5b1a5aecdaa9531d0912e5c6f9ab32f`

## TDD evidence

The public SDK test was created before the package. This command produced the expected
red state:

```text
uv run --no-project --with pytest pytest tests/unit/test_sdk.py -q
```

Result: collection failed with one `ModuleNotFoundError: p2p_thief_agent`. After the
minimal SDK implementation, the test passed.

## Final local gates

| Command/check | Actual result |
|---|---|
| `uv lock --check` | Exit 0; 13 packages resolved, lock current |
| Initial clean `uv sync --frozen` | Exit 0; created `.venv`, built project, installed 10 packages |
| Final `uv sync --frozen` | Exit 0; 10 packages checked |
| `uv run pytest --cov --cov-branch --cov-fail-under=85` | Exit 0; 8 passed; 92.86% coverage |
| `uv run ruff check .` | Exit 0; all checks passed, zero findings |
| `uv run python scripts/check_file_lengths.py` | Exit 0; 17 source/script and 3 test files checked |
| `uv run python scripts/check_secrets.py` | Exit 0; 90 text files checked, zero findings |
| `uv run p2p-thief --help` | Exit 0; scaffold help only |
| `uv run p2p-thief --version` | Exit 0; `p2p-thief 1.00` |
| Generated-example JSON parse/hash check | Exit 0; 4/4 parsed and hashes match `SOURCE_INVENTORY.md`; official provenance not established |
| Markdown relative-link check | Exit 0; 39 documents, zero broken targets |
| Simulator runtime provenance scan | Exit 0; zero named simulator runtime matches in `src/tests/scripts` |
| `git diff --check` | Exit 0; no whitespace errors |

Branch coverage was enabled. The scaffold contains 28 measured source statements; only
the module-execution wrapper is uncovered, leaving 92.86% global coverage.

## Contract gate

```text
uv run python scripts/check_shared_contracts.py
```

Actual result: exit 1 with `PENDING`; no accepted parity manifest exists, so
shared-hash verification was not run. A Cop candidate exists at exact commit
`84339c210c8e3293d972bccec5912abf519d502c`, but it is unfrozen and
coordinator-rejected pending revision. Zero candidate files were integrated.

No contract version, controlled-file list, manifest hash, or file hash is accepted for
handoff. Generated-example hashes are observations only and are not presented as
official provenance or cross-repository parity.

## Scope confirmation

No game, networking, FastMCP, commit-reveal runtime, LLM, Gmail, GUI, replay, or
reporting behavior was implemented. The package contains metadata, a public SDK marker,
CLI help/version, empty layer boundaries, and quality tooling only.

## Addendum — 2026-07-29 (record above covers the scaffold only)

The 2026-07-25 record above verified the **M0/M1 scaffold** (8 tests, 92.86%) and is
retained as history. It no longer describes the repository. Substantial work has since
landed: the M2 core domain, the EXC-001 deterministic baseline, a commit-reveal protocol
layer, and the M3 local-state, scoring, and baseline-integration package.

> **This addendum was itself superseded.** Its original table recorded 452 tests at
> 95.36% over an Option-B protocol layer that included RFC-8785 canonicalization,
> separated hash domains, a Node neutral stub, and two-identity negotiation. Commit
> `11d0c7a` ("replace Option-B profile with simulator wire; archive old layer") removed
> that layer on 2026-07-29, deleting `protocol/canonical.py`, `protocol/commitment.py`,
> `protocol/negotiation.py`, and roughly twenty conformance tests, and retiring the
> Node stub into `archive/pre-sim-realign/`. The counts below replace it.

Measured gates on 2026-07-31:

| Command/check | Actual result |
|---|---|
| `uv run ruff check .` | Exit 0; all checks passed |
| `uv run pytest --cov --cov-branch --cov-fail-under=85` | Exit 0; **232 passed**; 99.71% branch coverage |
| `uv run python scripts/check_file_lengths.py` | Exit 0; 33 source/script and 20 test files checked |
| `uv run python scripts/check_secrets.py` | Exit 0; 131 text files, zero findings |
| `uv run p2p-thief --help` / `--version` | Exit 0; `p2p-thief 1.00` |
| `uv run python scripts/check_shared_contracts.py` | Exit 1; `PENDING` (fail-closed; no accepted conformance profile) |
| `git diff --check` | Exit 0; no whitespace errors |

The shipped protocol layer is the simulator-conformant wire recorded in
[SIM_WIRE_PROTOCOL.md](SIM_WIRE_PROTOCOL.md). **Stage C acceptance is not recorded**: no
`CONFORMANCE_PROFILE: ACCEPTED` and no `M2_GAMEPLAY: GO` verdict exists, the adopted
profile has no independent-stub evidence behind it, and the contract checker remains
fail-closed at `PENDING` / exit 1. This addendum is a descriptive verification snapshot,
not an acceptance verdict.
