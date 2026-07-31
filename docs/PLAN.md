# Plan

Status: M0, M2, and M3 are `DONE`; M1 is `IN PROGRESS` at M1-013. M4–M9 are `PENDING`
and proceed in order. The M4 substance is implemented — commit-reveal, canonical
hashing, wire message models, and the signed-terms handshake all ship under
`protocol/` — but M4 completion awaits M1 Stage C. Nothing is classified `BLOCKED`;
unresolved decisions are requested explicitly rather than inferred.

**Stage-B status, corrected 2026-07-31.** Stage A is satisfied by
[SIM_WIRE_PROTOCOL.md](SIM_WIRE_PROTOCOL.md). Stage B is **partly** satisfied: the
Node stub that proved the earlier Option-B profile was retired to
`archive/pre-sim-realign/` when the wire was re-aligned on 2026-07-29, so no stub
exercises the current profile. What does exist is stronger for the commitment domain
alone — `tests/unit/test_reference_vector.py` reproduces a commit hash emitted by the
**reference simulator** during a real match, which is foreign-implementation evidence
rather than self-authored vectors. Stage B for the tool surface, negotiation, and
message shapes remains unproven (`M1-015`–`M1-017`).

Beyond the M0–M1 scaffold this repository now implements the M2 core domain, M3 local
state and scoring, the deterministic baseline strategy, and the protocol layer. It has
no peer runtime, transport, or FastMCP dependency: `fastmcp` is deliberately absent
from `pyproject.toml` until `M5-002` begins.

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
| M1 | Interoperability conformance profile | Author a Thief-owned wire profile from book-confirmed rules and Option-B choices, prove it bidirectionally against a neutral stub opponent, and obtain profile acceptance | `IN PROGRESS` |
| M2 | Core domain rules | Coordinates, actions, grid, legal movement, barrier and capture semantics behind the SDK | `DONE` |
| M3 | Local state, scoring and deterministic baseline | Immutable local history, disclosed-barrier state, scoring, and deterministic legal baseline | `DONE` |
| M4 | Protocol, canonicalization and commit-reveal | Accepted public messages, exact canonical bytes, state transitions, commitment verification, and audit outcomes | `PENDING` |
| M5 | FastMCP runtime and resilience | Symmetric server/client peer, gateway, idempotency, deadlines, watchdog, recovery, and tunnel path | `PENDING` |
| M6 | Scent, belief and private strategy | Confirmed scent physics, public observations, Thief-local belief, and private strategy | `PENDING` |
| M7 | Series orchestration, artifacts, gatekeeper and reporting | Six-sub-game flow, official artifacts, external-call gatekeeper, and agreed JSON reporting | `PENDING` |
| M8 | GUI, replay, interoperability and security hardening | Local-truth UI, replay/verifier, neutral-opponent E2E, tamper tests, and security review | `PENDING` |
| M9 | League evidence, submission and release | League evidence, academic README, final clean gates, access checks, and annotated release | `PENDING` |

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
  negative vectors. *Currently only partly met — see the Stage-B note at the top.*
- **Stage C** — the coordinator accepts the profile, then separately issues
  `M2_GAMEPLAY: GO`.

No peer commit SHA, manifest hash, controlled-path list, or per-file hash is required
any more, and no peer file may be copied. The reviews above remain valid as reviews of
an external artifact; they are not a route to consuming one.

M1 is complete only after Stages A and B have exit evidence and Stage C acceptance is
explicitly recorded. Stage C is `PENDING`, not assumed. Profile acceptance authorizes
protocol implementation only and never opens gameplay on its own.

The contract checker stays fail-closed at `PENDING` with exit 1 throughout. Its message
retains historical copy-model wording; under this model it means no accepted conformance
profile exists.

## Decision gates

The nine live placeholders under [adr/](adr/README.md) do not authorize runtime
behavior (ADR-0006 was superseded on 2026-07-29 and archived).
Shared-impact decisions require direct evidence and explicit acceptance. In particular,
schema versions, participant/match binding, canonicalization, `config_sha256` scope,
extension policy, and neutral-opponent failure semantics must be explicitly decided
before their dependent protocol or runtime behavior is declared complete.

## Verification sequence

1. `uv sync --frozen`
2. `uv run ruff check .`
3. `uv run pytest --cov --cov-branch --cov-fail-under=85`
4. `uv run python scripts/check_file_lengths.py`
5. `uv run python scripts/check_secrets.py`
6. CLI help and version smoke tests
7. Current contract-status check: exit 1 with `PENDING`
8. `git diff --check`

CI runs the same currently applicable sequence. The contract-status step remains
fail-closed until an exact conformance-profile revision is accepted and recorded.

The protected checker still prints historical “no proposal” wording. In current
coordination terms, its `PENDING` result means no accepted conformance-profile revision
is recorded. CI therefore verifies the nonzero exit and `PENDING` marker until Stage C
is complete.
