# Active Thief Task Ledger

Statuses: `DONE`, `IN PROGRESS`, `PENDING`, and `SUPERSEDED`. `DONE` requires verified
exit evidence. `IN PROGRESS` means actively being worked. `PENDING` means queued,
awaiting review, or awaiting an explicit decision; it does not mean blocked. Work
proceeds sequentially. When a required choice or acceptance is not recorded, ask the
user rather than infer it.

## M0 — Evidence and source reconciliation

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M0-001 | Verify branch history and reconcile conflicting documentation | DONE | `REPOSITORY_AUDIT.md` |
| M0-002 | Record direct Appendix E/F requirements and parameter statuses | DONE | `REQUIREMENTS_LEDGER.md`, `PARAMETERS_BASELINE.md` |
| M0-003 | Quarantine historical drafts and distinguish simulator/reference behavior | DONE | `config/README.md`, source/conflict registers |
| M0-004 | Correct the coordinator source hierarchy and artifact provenance | DONE | `SOURCE_OF_TRUTH.md`, `SOURCE_INVENTORY.md` |
| M0-005 | Preserve explicit unknowns without inventing runtime fields | DONE | `UNKNOWN_REQUIREMENTS.md`, ADR placeholders |

## M1 — Interoperability conformance profile

**The copy model was superseded on 2026-07-28.** Under `THIEF-002` this repository has
no access to the companion Cop repository and must interoperate with an unknown
classmate opponent, so byte-parity with one peer is not evidence of interoperability.
`M1-007` … `M1-011` are retained as `SUPERSEDED` rather than deleted, so the change of
approach stays visible. `M1-004`, `M1-006`, and `M1-006b`/`M1-006c` remain `DONE`: they
were reviews of external artifacts and no peer byte was ever integrated.

Current work starts at `M1-013`; later M1 tasks remain `PENDING` until their exit
evidence is reached.

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M1-001 | Maintain independently installable package, public SDK, and behavior-free CLI | DONE | Frozen uv sync and CLI tests |
| M1-002 | Enforce Ruff, branch coverage, file-length, secret, CLI, and diff gates | DONE | Local gates and `.github/workflows/ci.yml` |
| M1-003 | Correct stale source, proposal, and artifact-provenance claims | DONE | Updated source/status documentation |
| M1-004 | Review Cop candidate `84339c2` read-only, path by path | DONE | `CONTRACT_REVIEW.md` with NO-GO verdict |
| M1-005 | Keep the current contract checker fail-closed | DONE | Exit 1 with documented `PENDING` |
| M1-006 | Review revised Cop candidate `b586af9` and coordinator portability findings | DONE | Updated `CONTRACT_REVIEW.md` and `GATE_RESOLUTION_REVIEW.md` |
| M1-006b | Review Cop candidate `e0df5ba` read-only, path by path (18 controlled files) | DONE | `CONTRACT_REVIEW.md` with P0/P1 findings and NO-GO verdict |
| M1-006c | Review Cop bundle `0.2.0-proposed` at `0c20bf0` read-only (32 controlled files) | DONE | `CONTRACT_REVIEW.md`: 32/32 hashes and 7/7 vectors independently reproduced; four of seven coordinator blockers unresolved plus two new P0 defects; NO-GO |
| M1-007 | ~~Receive every provisionally authorized handoff value and coordinator verdict~~ | SUPERSEDED | Copy model withdrawn 2026-07-28 under `THIEF-002` |
| M1-008 | ~~Verify provisional manifest bytes, controlled paths, and declared file hashes before copying~~ | SUPERSEDED | Copy model withdrawn 2026-07-28 under `THIEF-002` |
| M1-009 | ~~Copy all provisionally authorized controlled paths verbatim from the named Cop commit~~ | SUPERSEDED | Copy model withdrawn 2026-07-28 under `THIEF-002` |
| M1-010 | ~~Add only the Thief adapter/tests required by the provisionally authorized match-config contract~~ | SUPERSEDED | Reframed as `M1-016`/`M1-017` against a neutral stub |
| M1-011 | ~~Prove cross-repository parity and two variable match identities~~ | SUPERSEDED | Byte parity with one peer is not evidence about an unknown opponent |
| M1-013 | Author the Thief-owned wire conformance profile with labelled authority per item | IN PROGRESS | Stage A of `CONTRACT_HANDOFF_CHECKLIST.md`; every item book-confirmed, Option-B, or `UNKNOWN` |
| M1-014 | Define canonicalization with reproducible vectors including escaping and separated hash domains | PENDING | Vectors covering nested objects, numbers, non-ASCII, quotes, backslashes, control characters, and non-BMP codepoints |
| M1-015 | Build a neutral stub opponent sharing no source file with any peer repository | PENDING | Stub is independently authored and imports no peer module |
| M1-016 | Prove bidirectional conformance and two participant identities against the stub | PENDING | Thief-proposes and Thief-accepts both pass without editing a profile file |
| M1-017 | Prove fail-closed negative vectors before gameplay | PENDING | Participant, value, version, hash, ordering, replay, and private-leakage vectors all reject |
| M1-012 | Record profile acceptance and the separate M2 gameplay verdict | PENDING | `CONFORMANCE_PROFILE: ACCEPTED` naming an exact revision, then `M2_GAMEPLAY: GO` |

## M2 — Core domain rules

Coordinator authorized contract-independent M2 domain implementation on 2026-07-28.
This work uses only Appendix E/F `CONFIRMED` rules with explicit inputs; it does not
depend on any shared-contract byte, MCP endpoint, or Cop-owned file. FastMCP,
commit-reveal, and live peer runtime remain separate later milestones.

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M2-001 | Implement immutable coordinates, actions, and configured grid bounds | DONE | `test_coordinates.py`, `test_board.py`; `M2_DOMAIN.md` |
| M2-002 | Implement N/S/E/W/STAY legal-action validation | DONE | `test_movement.py` normal/boundary/diagonal/off-grid/blocked |
| M2-003 | Implement disclosed-barrier domain rules | DONE | `test_barriers.py`, `test_movement.py` |
| M2-004 | Implement barrier-on-current-cell capture | DONE | `test_capture.py` barrier-on-Thief and precedence |
| M2-005 | Implement trapped-Thief capture under the accepted STAY interpretation | DONE | `test_capture.py` trapped/STAY-no-rescue |
| M2-006 | Reject invalid off-board positions and malformed iterable barrier quotas consistently | DONE | Focused movement, capture, barrier, and strategy tests; full suite |

## EXC — Contract-independent exceptions

Work authorized outside the milestone sequence because it depends on no shared-contract
byte, MCP endpoint, or Cop-owned file. An entry here **never** satisfies a milestone
task; the corresponding milestone row keeps its own status.

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| EXC-001 | Implement the deterministic Thief baseline policy on existing public domain APIs | DONE | `test_strategy_metrics.py`, `test_baseline_strategy.py`, `test_strategy_sdk.py`; `PRD_strategy.md`; branch `agent/thief-baseline-strategy` |

`EXC-001` does **not** close `M3-004`. It adds no Thief-local state, no history, no
scoring, and no turn state machine, so the M3 integration evidence is still `PENDING`.

## M3 — Local state, scoring and deterministic baseline

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M3-001 | Model immutable Thief-local state and history snapshots | PENDING | Local-truth and immutability tests |
| M3-002 | Track known disclosed barriers without Cop-private truth | PENDING | Provenance/boundary tests |
| M3-003 | Implement accepted scoring and outcome calculation | PENDING | Capture, survival, tie, and technical-loss tests |
| M3-004 | Integrate the completed deterministic legal baseline policy | PENDING | Tie-break, fallback, trapped, repeatability, and local-state integration tests |

## M4 — Protocol, canonicalization and commit-reveal

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M4-001 | Implement accepted public envelopes and message models | PENDING | Schema/version/identity failure tests |
| M4-002 | Implement exact canonical bytes and shared test vectors | PENDING | Independent vector/hash tests |
| M4-003 | Implement explicit protocol states and illegal-transition rejection | PENDING | Transition table tests |
| M4-004 | Implement SHA-256 commit, acknowledgement, reveal, and nonce secrecy | PENDING | Normal/order/tamper tests |
| M4-005 | Implement audit mismatch and technical-loss outcomes | PENDING | Replayable audit failure tests |

## M5 — FastMCP runtime and resilience

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M5-001 | Route runtime coordination through one Thief gateway | PENDING | Architecture/boundary tests |
| M5-002 | Run the Thief as both FastMCP server and client | PENDING | Separate-process integration tests |
| M5-003 | Enforce accepted idempotency, acknowledgement, and duplicate handling | PENDING | Duplicate/reorder tests |
| M5-004 | Implement deadlines, watchdog, controlled recovery, and backpressure | PENDING | Timeout/crash/recovery tests |
| M5-005 | Validate localhost and public-tunnel paths against identical fixtures | PENDING | Connectivity and failure evidence |

## M6 — Scent, belief and private strategy

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M6-001 | Implement confirmed multiplicative scent physics | PENDING | Emission/decay/clipping tests |
| M6-002 | Consume accepted public scent observations in the accepted order | PENDING | Shape/order/boundary tests |
| M6-003 | Maintain a Thief-local belief without objective Cop truth | PENDING | Privacy and update tests |
| M6-004 | Add private strategy improvements behind legal validation | PENDING | Determinism/deadline/no-network tests |

## M7 — Series orchestration, artifacts, gatekeeper and reporting

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M7-001 | Orchestrate the accepted six-sub-game series lifecycle | PENDING | Series state/scoring tests |
| M7-002 | Build accepted declaration, config, log, and result artifacts | PENDING | Schema/link/hash tests |
| M7-003 | Implement the centralized external-call gatekeeper | PENDING | FIFO/rate/retry/backpressure tests |
| M7-004 | Implement accepted private verbal-provider modes | PENDING | Mocked provider/fallback tests |
| M7-005 | Send the mutually agreed final JSON report through Gmail | PENDING | Mocked recipient/body/attachment/agreement tests |

## M8 — GUI, replay, interoperability and security hardening

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M8-001 | Build a live Thief local-truth GUI through the SDK | PENDING | View-model truth-boundary tests |
| M8-002 | Build replay UI on the accepted verifier | PENDING | Valid/malformed/reordered/tampered replay tests |
| M8-003 | Run bidirectional games against a neutral compliant-opponent harness | PENDING | Unknown-opponent E2E evidence |
| M8-004 | Harden secrets, identity, input validation, and dependency boundaries | PENDING | Security/privacy review and tests |
| M8-005 | Exercise crash, timeout, mismatch, and tamper recovery end to end | PENDING | Failure-injection evidence |

## M9 — League evidence, submission and release

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M9-001 | Capture required league/game artifacts and repository commit evidence | PENDING | Reviewed evidence bundle |
| M9-002 | Complete all six academic README components | PENDING | README checklist |
| M9-003 | Verify team identity, repository access, and current Moodle instructions | PENDING | Submission identity/access record |
| M9-004 | Run all gates from a clean frozen environment and complete security/provenance review | PENDING | Final validation record |
| M9-005 | Create the reviewed annotated `v1.0-submission` release tag | PENDING | Tag points to accepted submission commit |

The archived 635-task document remains historical coverage under
`archive/pre-audit/documentation/TODO.md`; it is not the active plan.
