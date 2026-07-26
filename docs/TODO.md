# Active Thief Task Ledger

Statuses: `DONE`, `IN PROGRESS`, `PENDING`, or `BLOCKED`. Every M2–M9 item is blocked
until the M1 accepted-contract handoff is complete. This ledger decomposes Thief-owned
work only; Cop contract revision and coordinator acceptance are external prerequisites,
not Thief implementation tasks.

## M0 — Evidence and source reconciliation

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M0-001 | Verify branch history and reconcile conflicting documentation | DONE | `REPOSITORY_AUDIT.md` |
| M0-002 | Record direct Appendix E/F requirements and parameter statuses | DONE | `REQUIREMENTS_LEDGER.md`, `PARAMETERS_BASELINE.md` |
| M0-003 | Quarantine historical drafts and distinguish simulator/reference behavior | DONE | `config/README.md`, source/conflict registers |
| M0-004 | Correct the coordinator source hierarchy and artifact provenance | DONE | `SOURCE_OF_TRUTH.md`, `SOURCE_INVENTORY.md` |
| M0-005 | Preserve explicit unknowns without inventing runtime fields | DONE | `UNKNOWN_REQUIREMENTS.md`, ADR placeholders |

## M1 — Public contract, match configuration, parity and freeze

Current blocker: candidate
`84339c210c8e3293d972bccec5912abf519d502c` exists, but it is unfrozen,
coordinator-rejected, and has not supplied an accepted handoff. “Proposal missing” is
not the blocker.

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M1-001 | Maintain independently installable package, public SDK, and behavior-free CLI | DONE | Frozen uv sync and CLI tests |
| M1-002 | Enforce Ruff, branch coverage, file-length, secret, CLI, and diff gates | DONE | Local gates and `.github/workflows/ci.yml` |
| M1-003 | Correct stale source, proposal, and artifact-provenance claims | DONE | Updated source/status documentation |
| M1-004 | Review Cop candidate `84339c2` read-only, path by path | DONE | `CONTRACT_REVIEW.md` with NO-GO verdict |
| M1-005 | Keep the current contract checker fail-closed | DONE | Exit 1 with documented `PENDING` |
| M1-006 | Receive every accepted handoff value and coordinator acceptance verdict | BLOCKED | Complete `CONTRACT_HANDOFF_CHECKLIST.md` |
| M1-007 | Verify accepted manifest bytes, controlled paths, and every declared file hash before copying | BLOCKED | Pre-copy checklist and recorded hash table |
| M1-008 | Copy all accepted controlled paths verbatim from the accepted Cop commit | BLOCKED | 100% exact-byte presence; no Thief-authored shared edits |
| M1-009 | Add only the Thief adapter/tests required by the accepted neutral match-config contract | BLOCKED | Bidirectional neutral-opponent conformance and negative tests |
| M1-010 | Prove cross-repository parity and obtain final coordinator freeze verdict | BLOCKED | Both checkers pass, manifest self-hash matches, acceptance recorded |

## M2 — Core domain rules

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M2-001 | Implement immutable coordinates, actions, and configured grid bounds | BLOCKED | Construction/boundary unit tests |
| M2-002 | Implement N/S/E/W/STAY legal-action validation | BLOCKED | Normal, boundary, diagonal, off-grid, and blocked tests |
| M2-003 | Implement disclosed-barrier domain rules | BLOCKED | Placement/disclosure and legal-move tests |
| M2-004 | Implement barrier-on-current-cell capture | BLOCKED | Accepted-order capture test |
| M2-005 | Implement trapped-Thief capture under the accepted STAY interpretation | BLOCKED | Accepted-order trapped/capture tests |

## M3 — Local state, scoring and deterministic baseline

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M3-001 | Model immutable Thief-local state and history snapshots | BLOCKED | Local-truth and immutability tests |
| M3-002 | Track known disclosed barriers without Cop-private truth | BLOCKED | Provenance/boundary tests |
| M3-003 | Implement accepted scoring and outcome calculation | BLOCKED | Capture, survival, tie, and technical-loss tests |
| M3-004 | Implement a deterministic legal baseline policy | BLOCKED | Tie-break, fallback, trapped, and repeatability tests |

## M4 — Protocol, canonicalization and commit-reveal

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M4-001 | Implement accepted public envelopes and message models | BLOCKED | Schema/version/identity failure tests |
| M4-002 | Implement exact canonical bytes and shared test vectors | BLOCKED | Independent vector/hash tests |
| M4-003 | Implement explicit protocol states and illegal-transition rejection | BLOCKED | Transition table tests |
| M4-004 | Implement SHA-256 commit, acknowledgement, reveal, and nonce secrecy | BLOCKED | Normal/order/tamper tests |
| M4-005 | Implement audit mismatch and technical-loss outcomes | BLOCKED | Replayable audit failure tests |

## M5 — FastMCP runtime and resilience

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M5-001 | Route runtime coordination through one Thief gateway | BLOCKED | Architecture/boundary tests |
| M5-002 | Run the Thief as both FastMCP server and client | BLOCKED | Separate-process integration tests |
| M5-003 | Enforce accepted idempotency, acknowledgement, and duplicate handling | BLOCKED | Duplicate/reorder tests |
| M5-004 | Implement deadlines, watchdog, controlled recovery, and backpressure | BLOCKED | Timeout/crash/recovery tests |
| M5-005 | Validate localhost and public-tunnel paths against identical fixtures | BLOCKED | Connectivity and failure evidence |

## M6 — Scent, belief and private strategy

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M6-001 | Implement confirmed multiplicative scent physics | BLOCKED | Emission/decay/clipping tests |
| M6-002 | Consume accepted public scent observations in the accepted order | BLOCKED | Shape/order/boundary tests |
| M6-003 | Maintain a Thief-local belief without objective Cop truth | BLOCKED | Privacy and update tests |
| M6-004 | Add private strategy improvements behind legal validation | BLOCKED | Determinism/deadline/no-network tests |

## M7 — Series orchestration, artifacts, gatekeeper and reporting

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M7-001 | Orchestrate the accepted six-sub-game series lifecycle | BLOCKED | Series state/scoring tests |
| M7-002 | Build accepted declaration, config, log, and result artifacts | BLOCKED | Schema/link/hash tests |
| M7-003 | Implement the centralized external-call gatekeeper | BLOCKED | FIFO/rate/retry/backpressure tests |
| M7-004 | Implement accepted private verbal-provider modes | BLOCKED | Mocked provider/fallback tests |
| M7-005 | Send the mutually agreed final JSON report through Gmail | BLOCKED | Mocked recipient/body/attachment/agreement tests |

## M8 — GUI, replay, interoperability and security hardening

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M8-001 | Build a live Thief local-truth GUI through the SDK | BLOCKED | View-model truth-boundary tests |
| M8-002 | Build replay UI on the accepted verifier | BLOCKED | Valid/malformed/reordered/tampered replay tests |
| M8-003 | Run bidirectional games against a neutral compliant-opponent harness | BLOCKED | Unknown-opponent E2E evidence |
| M8-004 | Harden secrets, identity, input validation, and dependency boundaries | BLOCKED | Security/privacy review and tests |
| M8-005 | Exercise crash, timeout, mismatch, and tamper recovery end to end | BLOCKED | Failure-injection evidence |

## M9 — League evidence, submission and release

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M9-001 | Capture required league/game artifacts and repository commit evidence | BLOCKED | Reviewed evidence bundle |
| M9-002 | Complete all six academic README components | BLOCKED | README checklist |
| M9-003 | Verify team identity, repository access, and current Moodle instructions | BLOCKED | Submission identity/access record |
| M9-004 | Run all gates from a clean frozen environment and complete security/provenance review | BLOCKED | Final validation record |
| M9-005 | Create the reviewed annotated `v1.0-submission` release tag | BLOCKED | Tag points to accepted submission commit |

The archived 635-task document remains historical coverage under
`archive/pre-audit/documentation/TODO.md`; it is not the active plan.
