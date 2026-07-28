# Plan

Status: M0 complete; M1 public-contract gate blocked pending coordinator
authorization for provisional parity testing. Final freeze follows successful
cross-repository parity/conformance. M2–M9 are blocked.

The Thief M0–M1 scaffold is based on remote main
`e1cc4992cd1c9a7705edf13fc976f85482ce601b`. It has package, SDK, CLI, test, and
quality boundaries but no gameplay or peer runtime.

## Architecture boundary

```text
CLI / future GUI / future MCP adapters
                 |
             public SDK
                 |
domain + orchestration + services + strategy
                 |
 protocol / config / external adapters
```

Every external entry point delegates through the SDK (`PS-007`). Cop and Thief remain
independently installable and share no runtime filesystem, mutable state, or private
truth (`SR-004`, `THIEF-001`).

## Common gated milestones

| Gate | Common phase | Thief-owned outcome | Current status |
|---|---|---|---|
| M0 | Evidence and source reconciliation | Correct source hierarchy, traceable Appendix E/F evidence, explicit unknowns/conflicts, reconciled repository history | `DONE` |
| M1 | Public contract, match configuration, parity and freeze | Independently review a provisionally authorized handoff, copy controlled bytes exactly, verify the manifest and per-file hashes, prove neutral match-config conformance, and obtain final freeze | `BLOCKED` |
| M2 | Core domain rules | Coordinates, actions, grid, legal movement, barrier and capture semantics behind the SDK | `BLOCKED ON M1` |
| M3 | Local state, scoring and deterministic baseline | Immutable local history, disclosed-barrier state, scoring, and deterministic legal baseline | `BLOCKED ON M1` |
| M4 | Protocol, canonicalization and commit-reveal | Accepted public messages, exact canonical bytes, state transitions, commitment verification, and audit outcomes | `BLOCKED ON M1` |
| M5 | FastMCP runtime and resilience | Symmetric server/client peer, gateway, idempotency, deadlines, watchdog, recovery, and tunnel path | `BLOCKED ON M1` |
| M6 | Scent, belief and private strategy | Confirmed scent physics, public observations, Thief-local belief, and private strategy | `BLOCKED ON M1` |
| M7 | Series orchestration, artifacts, gatekeeper and reporting | Six-sub-game flow, official artifacts, external-call gatekeeper, and agreed JSON reporting | `BLOCKED ON M1` |
| M8 | GUI, replay, interoperability and security hardening | Local-truth UI, replay/verifier, neutral-opponent E2E, tamper tests, and security review | `BLOCKED ON M1` |
| M9 | League evidence, submission and release | League evidence, academic README, final clean gates, access checks, and annotated release | `BLOCKED ON M1` |

Only Thief-owned work is decomposed in [TODO.md](TODO.md). The Cop repository remains
the sole author of parity-controlled shared files.

## M1 gate

The Cop candidates `84339c2`, `b586af9`, and `e0df5ba` must not be copied. On
2026-07-28 the coordinator audited `e0df5ba` (Cop main `be705f9`) and issued
`ACCEPTED_FOR_PROVISIONAL_PARITY: NO`: hashes are integrity-correct but the contract
is semantically rejected across seven issues, including mixed stable/per-match
configuration, unsupported schema fields, `rate_limits.json` misclassification, and
unauthenticated role alternation. Independent findings are in
[CONTRACT_REVIEW.md](CONTRACT_REVIEW.md),
[GATE_RESOLUTION_REVIEW.md](GATE_RESOLUTION_REVIEW.md), and the authoritative
[COORDINATOR_VERDICT_2026-07-28.md](COORDINATOR_VERDICT_2026-07-28.md).

Contract consumption starts only after every input in
[CONTRACT_HANDOFF_CHECKLIST.md](CONTRACT_HANDOFF_CHECKLIST.md) is supplied:

- provisionally authorized Cop commit and candidate version;
- provisionally accepted manifest exact-byte SHA-256;
- provisionally accepted controlled-path list and per-file hashes;
- explicit coordinator authorization for parity/conformance testing.

After receipt, Thief verifies the handoff before copying, copies every controlled path
byte-for-byte from the provisionally authorized commit, makes no shared-file edits, and proves
bidirectional match-configuration conformance with a neutral compliant opponent. Any
shared defect returns to Cop for a revised candidate.

M1 exits only when 100% of controlled bytes and the manifest self-hash match, both
repositories independently pass their contract checks, and the coordinator accepts
the resulting cross-repository evidence and issues the separate final contract-freeze
and M2 gameplay verdicts. Provisional copy authorization alone never opens M2.

## Decision gates

The ten placeholders under [adr/](adr/README.md) do not authorize runtime behavior.
Shared-impact decisions require direct evidence, compatible Cop/Thief treatment, and
coordinator acceptance. In particular, schema versions, participant/match binding,
canonicalization, `config_sha256` scope, extension policy, and neutral-opponent
failure semantics must be settled before M2.

## Verification sequence

1. `uv sync --frozen`
2. `uv run ruff check .`
3. `uv run pytest --cov --cov-branch --cov-fail-under=85`
4. `uv run python scripts/check_file_lengths.py`
5. `uv run python scripts/check_secrets.py`
6. CLI help and version smoke tests
7. Current contract-status check: exit 1 with `PENDING`
8. `git diff --check`

CI runs the same currently applicable sequence. The contract-status step must remain
fail-closed until a provisionally authorized handoff is integrated and verified.

The protected checker still prints historical “no proposal” wording. In current
coordination terms, its `PENDING` result means no provisionally authorized handoff is
integrated. CI
therefore verifies the nonzero exit and `PENDING` marker without changing the
Cop-owned candidate path.
