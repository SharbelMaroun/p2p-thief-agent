# Plan

Status: M0, M2, and M3 are `DONE`; M1 is `IN PROGRESS` at M1-013. M5 is `IN PROGRESS`;
M6–M9 are `PENDING` and proceed in order. The M4 substance is implemented — commit-reveal,
canonical hashing, wire message models, and the signed-terms handshake all ship under
`protocol/`, and every `M4-001`…`M4-017` row is `DONE` (2026-08-01). The M1 Stage-C
profile acceptance M4 was gated on was recorded 2026-07-31
([STAGE_C_ACCEPTANCE.md](STAGE_C_ACCEPTANCE.md), narrow scope), so M4 completion now awaits
only the coordinator's formal milestone verdict, not an unrecorded gate. Nothing is
classified `BLOCKED`; unresolved decisions are requested explicitly rather than inferred.

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
state and scoring, the deterministic baseline strategy, the protocol layer, and the M5
peer runtime. `fastmcp` is a live dependency: `adapters/fastmcp_server.py` and
`adapters/fastmcp_client.py` expose the four-tool server and the outbound client, and
`tests/integration/` drives a real two-process HTTP round trip (`M5-002` DONE). Cop and
Thief still share no runtime filesystem, mutable state, or private truth — every FastMCP
import is confined to the `adapters` layer by a guard test.

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
| M4 | Protocol, canonicalization and commit-reveal | Accepted public messages, exact canonical bytes, state transitions, commitment verification, and audit outcomes | `DONE` — *corrected 2026-08-02: this row still read `PENDING` although every `M4-001`…`M4-017` row in `TODO.md` is DONE, including the constant-time compare, canonicalization vectors, Step-0 attestation and adversarial vectors added 2026-08-01. Formal milestone closure is the coordinator's verdict* |
| M5 | FastMCP runtime and resilience | Symmetric server/client peer, gateway, idempotency, deadlines, watchdog, recovery, play loop, and tunnel path | `IN PROGRESS` — **done:** server, client, the two-process round trip, the private opponent-URL boundary, the negotiation refusal gate, the turn loop and sub-game, idempotency, the full reliability set (deadlines, watchdog with `persist_state`/`controlled_shutdown`, mid-turn-disconnect terminal loss, backpressure `M5-016`), the orchestrator gateway (`M5-001`), the log manager (`M5-008`), the deadline tracker (`M5-009`), retry-aware delivery (`M5-010`), the autonomous play loop (`M5-019`) with hosting and readiness (`M5-019e`) and negotiation sequencing (`M5-019f`), the adversarial-peer proof (`M5-011`), the SDK transport guard (`M5-018`), the own-config-directory (`M5-006`), the architecture docs (`M5-013`), and the same-terminal-outcome proof (`M5-017`). **Remaining — all externally or coordinator/M6-blocked, not skippable engineering:** the tunnel path (`M5-005`, real ngrok/two machines + M8 screenshots), the Step-0/`config_sha256` wire question (`M5-014f`, `U-024`), and the scent-lock at negotiation (`M5-015`, needs the M6 scent model). *Rows corrected 2026-08-02* |
| M6 | Scent, belief and private strategy | Confirmed scent physics, public observations, Thief-local belief, and private strategy | `PENDING` |
| M7 | Series orchestration, artifacts, gatekeeper and reporting | Six-sub-game flow, official artifacts, external-call gatekeeper, and agreed JSON reporting | `DONE` |
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
explicitly recorded. **Stage C was accepted on 2026-07-31** in
[STAGE_C_ACCEPTANCE.md](STAGE_C_ACCEPTANCE.md), on the strength of the
reference-implementation vector rather than on assertion. The acceptance is narrow:
it authorizes protocol and runtime implementation, leaves `M1-015`–`M1-017` open, and
does **not** open gameplay — `M2_GAMEPLAY: GO` is a separate verdict and is not issued.

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
