# Plan

Status: M0 complete; M1 public-contract gate blocked pending coordinator
authorization for provisional parity testing. Final freeze follows successful
cross-repository parity/conformance. M2 core domain is implemented under the
2026-07-28 coordinator authorization for contract-independent domain work and awaits
independent re-review; M3–M9 remain blocked.

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
| M1 | Interoperability conformance profile | Author a Thief-owned wire profile from book-confirmed rules and Option-B choices, prove it bidirectionally against a neutral stub opponent, and obtain profile acceptance | `BLOCKED` |
| M2 | Core domain rules | Coordinates, actions, grid, legal movement, barrier and capture semantics behind the SDK | `IMPLEMENTED` (contract-independent, authorized 2026-07-28; coordinator re-review pending, `MERGE_ALLOWED: NO`) |
| M3 | Local state, scoring and deterministic baseline | Immutable local history, disclosed-barrier state, scoring, and deterministic legal baseline | `BLOCKED ON M1` |
| M4 | Protocol, canonicalization and commit-reveal | Accepted public messages, exact canonical bytes, state transitions, commitment verification, and audit outcomes | `BLOCKED ON M1` |
| M5 | FastMCP runtime and resilience | Symmetric server/client peer, gateway, idempotency, deadlines, watchdog, recovery, and tunnel path | `BLOCKED ON M1` |
| M6 | Scent, belief and private strategy | Confirmed scent physics, public observations, Thief-local belief, and private strategy | `BLOCKED ON M1` |
| M7 | Series orchestration, artifacts, gatekeeper and reporting | Six-sub-game flow, official artifacts, external-call gatekeeper, and agreed JSON reporting | `BLOCKED ON M1` |
| M8 | GUI, replay, interoperability and security hardening | Local-truth UI, replay/verifier, neutral-opponent E2E, tamper tests, and security review | `BLOCKED ON M1` |
| M9 | League evidence, submission and release | League evidence, academic README, final clean gates, access checks, and annotated release | `BLOCKED ON M1` |

Only Thief-owned work is decomposed in [TODO.md](TODO.md). Under `THIEF-002` this
repository authors its own wire profile and consumes no peer-owned file.

## M1 gate

The Cop candidates `84339c2`, `b586af9`, and `e0df5ba` must not be copied. On
2026-07-28 the coordinator audited `e0df5ba` (Cop main `be705f9`) and issued
`ACCEPTED_FOR_PROVISIONAL_PARITY: NO`: hashes are integrity-correct but the contract
is semantically rejected across seven issues, including mixed stable/per-match
configuration, unsupported schema fields, `rate_limits.json` misclassification, and
unauthenticated role alternation. A newer Cop bundle `0.2.0-proposed`
(`0c20bf0`, 32 controlled files) has been reviewed read-only by the Thief: its bytes
and vectors reproduce exactly, but four of the seven blockers remain unresolved and it
carries no coordinator verdict, so it must not be copied either. Independent findings
are in
[CONTRACT_REVIEW.md](CONTRACT_REVIEW.md),
[GATE_RESOLUTION_REVIEW.md](GATE_RESOLUTION_REVIEW.md), and the authoritative
[COORDINATOR_VERDICT_2026-07-28.md](COORDINATOR_VERDICT_2026-07-28.md).

### The copy model was superseded on 2026-07-28

M1 no longer consumes a peer's bundle. Team direction (`THIEF-002`) forbids read and
write access to the companion Cop repository and makes league play against classmates
the target, so byte-parity with one companion repository is evidence about that
repository and nothing else. A classmate's agent has never seen those files.

M1 is now an **interoperability conformance gate**, specified in
[CONTRACT_HANDOFF_CHECKLIST.md](CONTRACT_HANDOFF_CHECKLIST.md):

- **Stage A** — the Thief authors its own wire profile, labelling every item
  book-confirmed, an Option-B project choice, or `UNKNOWN`, including exact
  canonicalization with escaping vectors and separated hash domains.
- **Stage B** — that profile is proved bidirectionally against a neutral stub opponent
  sharing no source file with any peer, with two participant identities and fail-closed
  negative vectors.
- **Stage C** — the coordinator accepts the profile, then separately issues
  `M2_GAMEPLAY: GO`.

No peer commit SHA, manifest hash, controlled-path list, or per-file hash is required
any more, and no peer file may be copied. The reviews above remain valid as reviews of
an external artifact; they are not a route to consuming one.

M1 exits only when Stage A, Stage B, and Stage C are all satisfied. Profile acceptance
authorizes protocol implementation only and never opens gameplay on its own.

The contract checker stays fail-closed at `PENDING` with exit 1 throughout. Its message
retains historical copy-model wording; under this model it means no accepted conformance
profile exists.

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
