# Active Thief Task Ledger

Statuses: `DONE`, `IN PROGRESS`, `PENDING`, and `SUPERSEDED`. `DONE` requires verified
exit evidence. `IN PROGRESS` means actively being worked. `PENDING` means queued,
awaiting review, or awaiting an explicit decision; it does not mean blocked. Work
proceeds sequentially. When a required choice or acceptance is not recorded, ask the
user rather than infer it.

**2026-07-31 decomposition.** Every milestone task is now broken into executable
sub-tasks with letter suffixes (`M5-002a`, `M5-002b`, …). Parent rows keep their original
ID, status, and exit evidence verbatim and now act as the milestone gate; a parent may
only become `DONE` when all of its sub-tasks are `DONE`. No existing status was changed
by the decomposition.

## Conventions

- **Authority tags** in the exit-evidence column cite the governing source in the order
  fixed by `SOURCE_OF_TRUTH.md`: `[book §]` · `[AE-nn]` Appendix E rule · `[AF-tn]`
  Appendix F table · `[G§n]` submission guidelines · `[PRD-x]` local PRD · `[ADR-nnnn]`.
- **`THIEF-002` applies to every row.** No task may be satisfied by reading, cloning, or
  inspecting the companion Cop repository. The pinned `Game-P2P-Cop-Chase` simulator at
  `960499fd5e8777b4929625f5d8fdcf2ab4677b54` is the sanctioned wire reference; match its
  wire, never copy its source.
- A task whose authority is an open unknown carries the `U-nnn` marker and must not be
  implemented as binding until the coordinator rules.

## How to use this ledger

1. Find the lowest-numbered milestone that is still open and work its tasks in ID order.
   Phases are sequential by design; the book's chapter 10 warning about skipping ahead is
   why the stage-2 gap is called out explicitly.
2. A sub-task is the unit of work. Complete it, run every continuous gate, then commit
   with a focused message naming the sub-task ID. Commit only when asked.
3. Never mark a parent `DONE` while any of its sub-tasks is open, and never self-issue a
   milestone acceptance — that is the coordinator's decision.
4. If a task requires a value nobody has confirmed, stop and register a `U-nnn` rather
   than choosing one silently. Silent choices are the defect this ledger exists to catch.
5. `THIEF-002` applies to every row without exception. The pinned simulator is the only
   sanctioned external reference, and it is read for behaviour, never copied for source.

---

## Milestone exit gates

A milestone closes only when every task under it is `DONE` **and** its exit gate is
observed running end to end, not merely written. Book chapter 10 is explicit that a
milestone is "the behaviour is observed", never "the code is written".

| Milestone | Exit gate | State |
|---|---|---|
| M0 | Authority order, provenance, conflicts, and unknowns are evidence-backed | closed |
| M1 | Stage A profile, Stage B vectors and stub, Stage C coordinator acceptance | Stage C **not recorded**; checker fail-closed |
| M2 | Complete hardened domain suite: movement, barriers, capture | closed |
| EXC-001 | Deterministic baseline policy on public domain APIs | closed |
| M3 | Immutable local state, scoring, and baseline integration | closed except `M3-005` |
| M4 | Independent vectors, tamper tests, and commit-reveal round trip | substance built; formal close gated on M1 Stage C |
| M5 | The Thief runs as server and client and completes a resilient game | **open — no transport exists yet** |
| M6 | Legal deterministic behaviour under observation and fallback tests | open |
| M7 | One complete series produces accepted audit artifacts | open |
| M8 | Unknown-opponent rehearsal and evidence screenshots pass | open |
| M9 | Submission checklist and current Moodle instructions satisfied | open |

---

## Continuous gates

These run before every commit and in CI; they are not milestone-scoped.

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| G-001 | Keep `uv sync --frozen` reproducible | DONE | Clean clone installs from `uv.lock` `[G§8.4]` |
| G-002 | Keep `ruff check .` at zero findings | DONE | Zero violations under the pinned `select` set `[G§7.1]` |
| G-003 | Keep branch coverage at or above 85% | DONE | `pytest` fails under the configured `fail_under` `[G§6.2]` |
| G-004 | Keep every source file at or under 150 lines | DONE | `scripts/check_file_lengths.py` `[G§3.2]` |
| G-005 | Keep the secret scanner clean | DONE | `scripts/check_secrets.py` reports zero findings `[AE-39]` `[AE-40]` |
| G-006 | Keep the contract checker fail-closed until Stage C | DONE | `scripts/check_shared_contracts.py` exits 1 at `PENDING`; never edited to pass |
| G-007 | Keep the working tree whitespace-clean | DONE | `git diff --check` reports nothing |
| G-008 | Keep the prompt-engineering log current | DONE | `PROMPT_LOG.md` records each significant prompt `[G§8.3]` |
| G-009 | Keep CI running every gate on every push | DONE | `.github/workflows/ci.yml` |
| G-010 | Keep `DOCS_COMPLETENESS.md` reconciled after each milestone | PENDING | Every listed doc has a current owner and status |
| G-011 | Keep `PLAN.md` milestone states consistent with this ledger | PENDING | A milestone cannot read `DONE` in one file and open in the other |
| G-012 | Keep `REQUIREMENTS_LEDGER.md` in step with implemented behaviour | PENDING | A row marked satisfied has a test to point at |
| G-013 | Keep `UNKNOWN_REQUIREMENTS.md` in step with blocking tasks | PENDING | Every `U-nnn` names the tasks it blocks, and every blocked task cites its `U-nnn` |
| G-014 | Keep ADRs current when a decision changes | PENDING | A superseded decision is marked superseded, never silently edited |
| G-015 | Keep every commit message focused and single-purpose | DONE | `[G§8.2]` |
| G-016 | Never push, merge, or open a PR without the coordinator | DONE | Repository policy; local green is not acceptance |
| G-017 | Never read, clone, or inspect the companion Cop repository | DONE | `THIEF-002`; the pinned simulator is the sanctioned reference instead |
| G-018 | Never modify `Material/` or `.claude/` | DONE | Read-only by policy |
| G-019 | Stage files by explicit path only | DONE | No `git add .` or `-A`; no force-push, reset, or rebase |
| G-020 | Keep `.env-example` present with dummy values only | DONE | `[G§7.4]`; no real provider name or key |
| G-021 | Keep dependencies pinned through `uv.lock` | DONE | No unpinned or floating requirement `[G§8.4]` |
| G-022 | Keep the SDK the only public surface | DONE | Adapters and tests import `p2p_thief_agent.sdk`, never internals `[G§4.1]` |

---

## M0 — Evidence and source reconciliation

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M0-001 | Verify branch history and reconcile conflicting documentation | DONE | `REPOSITORY_AUDIT.md` |
| M0-002 | Record direct Appendix E/F requirements and parameter statuses | DONE | `REQUIREMENTS_LEDGER.md`, `PARAMETERS_BASELINE.md` |
| M0-002a | Record every Appendix F parameter with value, status, and locator | DONE | `PARAMETERS_BASELINE.md` `[AF-t13..t19]` |
| M0-002b | Record all 55 Appendix E rules with their sanctions | DONE | `REQUIREMENTS_LEDGER.md` `[AE-1..55]` |
| M0-003 | Quarantine historical drafts and distinguish simulator/reference behavior | DONE | `config/README.md`, source/conflict registers |
| M0-004 | Correct the coordinator source hierarchy and artifact provenance | DONE | `SOURCE_OF_TRUTH.md`, `SOURCE_INVENTORY.md` |
| M0-004a | Pin the simulator reference commit | DONE | `SIMULATOR_BASELINE.md` records `960499fd…` `[ADR-0008]` |
| M0-005 | Preserve explicit unknowns without inventing runtime fields | DONE | `UNKNOWN_REQUIREMENTS.md`, ADR placeholders |
| M0-006 | Record the book's internal contradictions the report must disclose | PENDING | Book p. 5 grants freedom to resolve contradictions **if** the report states where, what, and why. One entry per contradiction relied on: capture-proof party (p. 38 vs p. 39), barrier adjacency wording (p. 37), step/survival boundary (`M3-005`), scent-decay arithmetic (`M6-005`), replay-hash sketch (`M8-002d`) |
| M0-006a | Record the appendix-lettering inconsistency | PENDING | The parameters table is called E, F, V, I, and "1" in different places; the rules table E and H |
| M0-006b | Record the board-size illustration inconsistency | PENDING | Binding value 7×7; illustrations use 10×10, 6×6, 5×5, and 3×3 |
| M0-006c | Record the `[Number of Agents]` name collision | PENDING | Table 13 means players (2); Table 18 means games in a series (6) |
| M0-006d | Record the series-of-six versus one-scoring-game tension | PENDING | Table 18 fixes six; rule 52 counts one. Resolved as six sub-games inside one counted meeting |
| M0-006e | Record the missing technical-loss row in Table 17 | PENDING | The scoring table omits a value the config schema requires |
| M0-007 | Keep the source inventory current | DONE | Every external source has a provenance note and access date |
| M0-007a | Record which sources are authoritative and which are reference | DONE | The simulator is reference; the book is authority `[ADR-0008]` |
| M0-008 | Keep the repository audit reproducible | DONE | The provenance comparison can be re-run and gives the same answer |
| M0-009 | Keep the prompt log complete through the current pass | DONE | `PROMPT_LOG.md` covers every significant prompt `[G§8.3]` |

---

## M1 — Interoperability conformance profile

**The copy model was superseded on 2026-07-28.** Under `THIEF-002` this repository has
no access to the companion Cop repository and must interoperate with an unknown
classmate opponent, so byte-parity with one peer is not evidence of interoperability.
`M1-007` … `M1-011` are retained as `SUPERSEDED` rather than deleted, so the change of
approach stays visible. `M1-004`, `M1-006`, and `M1-006b`/`M1-006c` remain `DONE`: they
were reviews of external artifacts and no peer byte was ever integrated.

Current work starts at `M1-013`; later M1 tasks remain `PENDING` until their exit
evidence is reached.

**2026-07-29 reconciliation.** Stage A and Stage B exit evidence now exists: the
Thief-owned wire profile, RFC-8785 canonicalization with escaping and non-BMP vectors,
separated hash domains, the independent Node neutral stub, bidirectional two-identity
conformance, and fail-closed negative/leakage vectors — tracked box by box in
`CONTRACT_HANDOFF_CHECKLIST.md`. Stage C acceptance (`CONFORMANCE_PROFILE: ACCEPTED`
naming a revision, then `M2_GAMEPLAY: GO`) is **not yet recorded**, so `M1-012`…`M1-017`
keep their statuses pending that coordinator verdict, and the contract checker stays
fail-closed at `PENDING` / exit 1.

**2026-07-31 correction to the note above.** The Stage A/B artifacts it names —
`WIRE_CONFORMANCE_PROFILE.md` and `tests/neutral_stub/` — were **archived** during the
simulator re-alignment and now live under `archive/pre-sim-realign/`. They are historical
evidence, not current exit evidence. The active wire specification is
`docs/SIM_WIRE_PROTOCOL.md`. See `M1-018`.

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
| M1-013a | Label every profile item book-confirmed, simulator-derived, or `UNKNOWN` | IN PROGRESS | No item is unlabelled; simulator behaviour is never promoted to mandatory |
| M1-014 | Define canonicalization with reproducible vectors including escaping and separated hash domains | PENDING | Vectors covering nested objects, numbers, non-ASCII, quotes, backslashes, control characters, and non-BMP codepoints |
| M1-014a | Cover nested objects, arrays, and numeric forms | PENDING | Ordering and number formatting are pinned |
| M1-014b | Cover quotes, backslashes, and control characters | PENDING | Escape handling is byte-exact |
| M1-014c | Cover non-ASCII and non-BMP codepoints | PENDING | `ensure_ascii=False` behaviour asserted |
| M1-014d | Prove the hash domains cannot collide | PENDING | Commitment and config hashes use distinct inputs |
| M1-015 | Build a neutral stub opponent sharing no source file with any peer repository | PENDING | Stub is independently authored and imports no peer module |
| M1-015a | Assert exact tool and argument names against the stub | PENDING | A renamed tool or argument fails the suite |
| M1-016 | Prove bidirectional conformance and two participant identities against the stub | PENDING | Thief-proposes and Thief-accepts both pass without editing a profile file |
| M1-017 | Prove fail-closed negative vectors before gameplay | PENDING | Participant, value, version, hash, ordering, replay, and private-leakage vectors all reject |
| M1-017a | Reject altered fixed and below-minimum values | PENDING | `[AE-11]` `[AE-12]` |
| M1-017b | Reject duplicate JSON keys and unsupported versions | PENDING | Duplicates change canonical bytes `[ADR-0003]` |
| M1-017c | Reject any private field appearing in shared config | PENDING | One leakage vector per private field class |
| M1-012 | Record profile acceptance and the separate M2 gameplay verdict | PENDING | `CONFORMANCE_PROFILE: ACCEPTED` naming an exact revision, then `M2_GAMEPLAY: GO` |
| M1-018 | Restate Stage A/B exit evidence against the post-realign artifacts | DONE | Corrected 2026-07-31: the M1 note now marks `WIRE_CONFORMANCE_PROFILE.md` and `tests/neutral_stub/` as archived under `archive/pre-sim-realign/` and cites `SIM_WIRE_PROTOCOL.md` as the active spec |
| M1-019 | Keep the parameters baseline reconciled with Appendix F | DONE | Every value carries its table locator and status |
| M1-019a | Flag any value the book leaves ambiguous | DONE | Ambiguity becomes a `U-nnn`, never a silent default |
| M1-020 | Keep the requirements ledger traceable | DONE | Every row cites a source locator |
| M1-020a | Distinguish confirmed from proposed rows | DONE | A proposal never reads as confirmed |
| M1-021 | Keep the verification policy explicit | DONE | What counts as evidence, and what does not, is written down |
| M1-021a | Require the pinned commit for any simulator observation | DONE | An unpinned observation is not evidence |
| M1-022 | Keep team identity confirmed and current | DONE | Group id, members, team code, and both addresses verified against lecturer answers |
| M1-022a | Record the confirmed eight-character team code | DONE | `sharNamr` `[AE-45]` |
| M1-022b | Record both lecturer addresses with their source | DONE | Sharing and reporting addresses differ in purpose, not spelling |
| M1-023 | Maintain the submission checklist against the book's Appendix C | DONE | Every checklist row maps to a task in this ledger |
| M1-024 | Keep the ADR set current and status-marked | DONE | `ADR_STATUS_REVIEW.md` records which decisions are live |
| M1-025 | Keep the JSON artifact schemas documented | PENDING | `JSON_ARTIFACT_SCHEMAS.md` matches the emitted artifacts; `U-019` still open |
| M1-026 | Keep the book/template reconciliation current | DONE | `BOOK_TEMPLATE_RECONCILIATION.md` records where official templates and book text differ |
| M1-027 | Keep the specification-conflict register current | DONE | Every identified conflict has a resolution status |
| M1-028 | Keep CI running every gate on every push | DONE | `.github/workflows/ci.yml` |
| M1-028a | Fail the build on any gate failure | DONE | No warn-and-continue path |
| M1-028b | Pin the CI Python and `uv` versions | DONE | CI reproduces the local environment `[G§8.4]` |

---

## M2 — Core domain rules

Coordinator authorized contract-independent M2 domain implementation on 2026-07-28.
This work uses only Appendix E/F `CONFIRMED` rules with explicit inputs; it does not
depend on any shared-contract byte, MCP endpoint, or Cop-owned file. FastMCP,
commit-reveal, and live peer runtime remain separate later milestones.

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M2-001 | Implement immutable coordinates, actions, and configured grid bounds | DONE | `test_coordinates.py`, `test_board.py`; `M2_DOMAIN.md` |
| M2-001a | Model `Coordinate` as a frozen value type | DONE | Hashable, equality-by-value, no in-place mutation |
| M2-001b | Model the five-member action vocabulary | DONE | `N`/`S`/`E`/`W`/`STAY` only `[AE-13]` `[AF-t15]` |
| M2-001c | Read grid size, origin corner, and start index from config | DONE | No hard-coded 7 `[AF-t13]` |
| M2-002 | Implement N/S/E/W/STAY legal-action validation | DONE | `test_movement.py` normal/boundary/diagonal/off-grid/blocked |
| M2-002a | Make diagonal movement structurally inexpressible | DONE | `[AE-14]`; not merely rejected at runtime |
| M2-003 | Implement disclosed-barrier domain rules | DONE | `test_barriers.py`, `test_movement.py` |
| M2-003a | Enforce the barrier quota | DONE | `[AF-t15]` |
| M2-003b | Make a placed barrier permanently impassable | DONE | Blocked for the remainder of the sub-game |
| M2-004 | Implement barrier-on-current-cell capture | DONE | `test_capture.py` barrier-on-Thief and precedence |
| M2-005 | Implement trapped-Thief capture under the accepted STAY interpretation | DONE | `test_capture.py` trapped/STAY-no-rescue `[AE-47]` |
| M2-006 | Reject invalid off-board positions and malformed iterable barrier quotas consistently | DONE | Focused movement, capture, barrier, and strategy tests; full suite |
| M2-007 | Expose the domain layer through the SDK | DONE | Adapters reach board, movement, barriers, and capture without internal imports `[G§4.1]` |
| M2-008 | Cover the domain layer with boundary tests | DONE | Every edge, corner, quota limit, and illegal input asserted |
| M2-008a | Test movement against all four board edges | DONE | Off-board attempts reject |
| M2-008b | Test movement into and around barriers | DONE | A blocked cell is never entered |
| M2-008c | Test barrier placement at and beyond quota | DONE | The boundary case is asserted, not assumed |
| M2-008d | Test capture in each defined way | DONE | Co-location, barrier-on-cell, trapped |
| M2-008e | Test malformed and hostile inputs reject | DONE | Non-integer, negative, and oversized coordinates |
| M2-009 | Document the domain vocabulary | DONE | Terms match the book's rules, not invented synonyms; `M2_DOMAIN.md` |
| M2-010 | Prove the domain layer is contract-independent | DONE | It imports no shared-contract byte and no transport module |
| M2-011 | Keep every domain value configurable | DONE | Board size, quota, and thresholds all read from config `[G§7.2]` |
| M2-012 | Define precedence when two capture conditions coincide | DONE | Deterministic single reason is reported |
| M2-013 | Model the police own-cell barrier allowance | DONE | The placing peer may target its own cell; corrected from the book's ambiguous p. 37 wording |

---

## EXC — Contract-independent exceptions

Work authorized outside the milestone sequence because it depends on no shared-contract
byte, MCP endpoint, or Cop-owned file. An entry here **never** satisfies a milestone
task; the corresponding milestone row keeps its own status.

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| EXC-001 | Implement the deterministic Thief baseline policy on existing public domain APIs | DONE | `test_strategy_metrics.py`, `test_baseline_strategy.py`, `test_strategy_sdk.py`; `PRD_strategy.md`; branch `agent/thief-baseline-strategy` |
| EXC-001a | Implement pure positional metrics | DONE | Manhattan distance, mobility, onward reach, edge contacts, dead-end detection |
| EXC-001b | Rank legal actions deterministically | DONE | Fixed tie-break order; identical inputs give identical output |

`EXC-001` did **not** close `M3-004`: it added no Thief-local state, no history, no
scoring, and no turn state machine. `M3-004` was completed separately on 2026-07-29 by
the `state/policy.py` integration, which binds this baseline to the immutable local
state without altering the pure `EXC-001` module.

---

## M3 — Local state, scoring and deterministic baseline

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M3-001 | Model immutable Thief-local state and history snapshots | DONE | `test_local_state.py`; `state/local_state.py`; `M3_LOCAL_STATE.md` |
| M3-001a | Prove the state type cannot hold objective Cop truth | DONE | Field whitelist test `[AE-8]` |
| M3-002 | Track known disclosed barriers without Cop-private truth | DONE | `test_known_barriers.py`; `state/known_barriers.py` |
| M3-002a | Record barrier provenance as disclosed-only | DONE | A barrier enters state only via disclosure `[AE-15]` |
| M3-003 | Implement accepted scoring and outcome calculation | DONE | `test_scoring.py`; `state/scoring.py` (FIXED Appendix F Table 17) |
| M3-003a | Encode capture 20/5 and survival 5/10 from config | DONE | `[AF-t17]`; values are not hard-coded |
| M3-003b | Encode the technical-loss zero | DONE | `[AE-19]` `[AE-48]` |
| M3-003c | Map outcomes to the simulator `result_claim` set | DONE | `wire_result_claim` → `capture`/`survival`/`timeout`; Tie stays in the scoring layer |
| M3-004 | Integrate the completed deterministic legal baseline policy | DONE | `test_local_policy.py`; `state/policy.py` |
| M3-005 | Resolve the step-limit / survival-threshold boundary | DONE | Closed 2026-07-31 from the book, without needing a coordinator ruling: chapter 3 table 2 defines survival as surviving "the limit of valid moves", and table 15 makes the limit equal the threshold, so the horizon is **inclusive**. `resolve_outcome` already used `steps >= survival_threshold`; `test_survival_at_threshold` now pins 34/35/36 explicitly. `U-022` closed, `C-017` `RESOLVED` |
| M3-005a | Register the boundary as a numbered unknown | DONE | `U-022` registered naming both readings; conflict `C-017` records the source defect |
| M3-005b | Add a boundary test pinning the chosen reading | PENDING | Turn `threshold-1`, `threshold`, `threshold+1` each asserted |
| M3-005c | Disclose the choice in the academic report | PENDING | Book p. 5 contradiction clause |
| M3-006 | Expose state, scoring, and policy through the SDK | DONE | Adapters never import `state` internals `[G§4.1]` |
| M3-007 | Prove the baseline policy is deterministic | DONE | Identical inputs yield an identical action every run |
| M3-007a | Fix the tie-break order explicitly | DONE | No reliance on set or dict iteration order |
| M3-007b | Prefer cells with greater onward reach | DONE | Mobility and dead-end avoidance are explicit metrics |
| M3-008 | Prove the local state never holds Cop-private truth | PENDING | The property holds **by construction** — `ThiefLocalState` has only `board`, `position`, `known_barriers`, `step`, `last_action`, and `history` — but no test asserts it, so a future field could break `[AE-8]` silently. Needs an explicit field-whitelist test |
| M3-009 | Prove scoring reads config rather than constants | DONE | Changing the config changes the award; no literal 20 or 10 in the policy path |
| M3-010 | Cover the state layer at full branch coverage | DONE | All four `state` modules at 100% branch within the green suite |
| M3-011 | Document the local-state and scoring model | DONE | `M3_LOCAL_STATE.md` describes the built behaviour |
| M3-012 | Keep the baseline module pure and side-effect free | DONE | `EXC-001` stays independent of local state; integration lives in `state/policy.py` |
| M3-013 | Map local outcomes to terminal results | DONE | Capture, survival, and technical loss each resolve deterministically |

Coordinator accepted M3-001..004 as DONE on 2026-07-29. The `state` package is
contract-independent, holds no Cop-private truth, and is re-exported through the SDK;
all four modules are at 100% branch coverage within the green suite.

---

## M4 — Protocol, canonicalization and commit-reveal

**Flag #2 ruling (2026-07-29): "Both".** The substance of `M4-001`…`M4-005` is
implemented — message models, exact canonical bytes with shared vectors, explicit
protocol states with illegal-transition rejection, the commit/acknowledge/reveal/
nonce-secrecy flow, and audit mismatch / technical-loss outcomes — living in `protocol/`
with tests under `tests/`. The coordinator classified this work as **both** M1 Stage-B
conformance evidence **and** the M4 milestone substance. The listed exit evidence
therefore already exists, but formal M4 completion still awaits M1 Stage-C acceptance
(see the M1 note above), so these rows stay `PENDING` — not because the code is missing,
but because the gate that authorizes protocol acceptance has not been recorded.

**2026-07-31 correction.** On 2026-07-29 the protocol layer was **re-aligned to the
pinned simulator wire** and the self-authored Option-B layer (envelope, sessions, JCS,
Node stub, profile) was archived under `archive/pre-sim-realign/`. `protocol/wire.py` is
now **envelope-free**: the tool argument *is* the message dict. Row `M4-001` still reads
"public envelopes" and describes the retired design; see `M4-007`.

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M4-001 | Implement the envelope-free simulator-conformant message models | PENDING | Schema/version/identity failure tests. Retitled 2026-07-31: `protocol/wire.py` is envelope-free — the tool argument *is* the message dict — so the former "public envelopes" wording described the retired Option-B design |
| M4-001a | Model `TurnMessage`, `ControlMessage`, and `AuditPayload` | PENDING | `protocol/wire.py`; matches `SIM_WIRE_PROTOCOL.md` |
| M4-001b | Reject unknown, missing, and mistyped fields | PENDING | Negative vectors per message type |
| M4-002 | Implement exact canonical bytes and shared test vectors | PENDING | Independent vector/hash tests |
| M4-002a | Pin the canonicalization form | PENDING | `canonical_json` with `ensure_ascii=False`; vectors cover escapes and non-BMP |
| M4-002b | Separate the hash domains | PENDING | Per-turn commitment and `config_sha256` cannot collide |
| M4-002c | Reproduce the pinned simulator's commitment bytes exactly | PENDING | `commit_of` verified byte-exact against `960499fd…`, by reimplementation only |
| M4-003 | Implement explicit protocol states and illegal-transition rejection | PENDING | Transition table tests |
| M4-004 | Implement SHA-256 commit, acknowledgement, reveal, and nonce secrecy | PENDING | Normal/order/tamper tests |
| M4-004a | Generate nonces with `secrets`, never `random` | PENDING | `token_hex(16)`, fresh per commit `[book §8]` |
| M4-004b | Keep the nonce hidden until the final audit | PENDING | Reveal carries move and hint only `[AE-18]` |
| M4-004c | Enforce commit-before-reveal ordering | PENDING | An out-of-order reveal is rejected |
| M4-005 | Implement audit mismatch and technical-loss outcomes | PENDING | Replayable audit failure tests |
| M4-005a | Recompute every commitment at audit and compare | PENDING | Any mismatch is a technical loss, no appeal `[AE-19]` |
| M4-006 | Implement Step-0 host, code, and token attestation | PENDING | Appendix E rule 24: OS/CPU/RAM/GPU, model version, group, sub-game, sealed LLM token budget, and the exact running Git commit are sealed before the first move. `sealing.sealed_spec_record` covers part of this; the missing piece is the Git commit binding and the pre-move ordering test |
| M4-006a | Bind the exact running Git commit into the sealed record | PENDING | `[AE-53]`; the same value later populates `github_commit` |
| M4-006b | Seal the agreed LLM token budget | PENDING | `[AE-54]` |
| M4-006c | Prove Step-0 completes before the first move | PENDING | Ordering test rejects a move before attestation |
| M4-007 | Retitle the M4 rows to match the envelope-free wire | DONE | `M4-001` retitled and the section note corrected on 2026-07-31; neither now describes the retired Option-B envelope design |
| M4-008 | Expose the protocol layer through the SDK | PENDING | The SDK reaches commit, seal, verify, audit, and handshake `[G§4.1]` |
| M4-009 | Cover commit-reveal with adversarial vectors | PENDING | Every tampering class is detected, not merely most |
| M4-009a | Detect a mutated move at audit | PENDING | Recomputed hash diverges |
| M4-009b | Detect a mutated intent flag | PENDING | The bluff flag is inside the seal |
| M4-009c | Detect a mutated or substituted nonce | PENDING | Nonce is part of the hashed input |
| M4-009d | Detect a single-byte mutation anywhere in the record | PENDING | SHA-256 is bit-sensitive; proven end to end |
| M4-009e | Detect a reordered step sequence | PENDING | Step index is bound into the record |
| M4-010 | Prove nonce generation quality | PENDING | Fresh per commit, cryptographically sourced, never reused |
| M4-010a | Prove two identical moves produce different commitments | PENDING | The dictionary-attack defence, demonstrated `[AE-18]` |
| M4-011 | Prove canonicalization is byte-stable across platforms | PENDING | LF endings and fixed encoding give identical bytes |
| M4-011a | Prove CRLF cannot enter a controlled file | PENDING | CRLF would break every hash |
| M4-011b | Prove non-ASCII content hashes identically | PENDING | `ensure_ascii=False` behaviour pinned |
| M4-012 | Compare digests in constant time | PENDING | `compare_digest`, never `==` `[book §8]` |
| M4-013 | Prove the protocol layer imports no transport | PENDING | Guard test; the protocol must work over any carrier |
| M4-014 | Document the protocol layer | PENDING | `PRD_commit_reveal.md` and `SIM_WIRE_PROTOCOL.md` match the built construction |
| M4-015 | Implement the signed-terms handshake | PENDING | Role-free identity, `config_sha256`, and required-terms checking |
| M4-015a | Reject a handshake missing a required term | PENDING | `missing_required_terms` covers every mandatory field |
| M4-015b | Reject a handshake whose config hash differs | PENDING | `[AE-11]`; refuse to play on mismatch |
| M4-016 | Keep the committed payload field set flexible | PENDING | The opponent re-hashes the revealed payload, so the field set is not itself an interop constraint — but the canonical form and concatenation are |
| M4-017 | Maintain the archived Option-B layer as history only | PENDING | `archive/pre-sim-realign/` is never imported or resurrected |

---

## M5 — FastMCP runtime and resilience

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M5-001 | Route runtime coordination through one Thief gateway | PENDING | Architecture/boundary tests |
| M5-001a | Define the five subsystem ports behind the gateway | PENDING | MCP connector, decision module, log manager, deadline tracker, watchdog `[AE-3]` |
| M5-001b | Forbid subsystem-to-subsystem imports by test | PENDING | Import-graph test fails on any direct peer link |
| M5-001c | Keep decision logic out of the gateway | PENDING | It coordinates; it does not decide `[book §9]` |
| M5-002 | Run the Thief as both FastMCP server and client | DONE | Server, client, an in-memory round trip, **and** a separate-process round trip over HTTP all pass (`M5-002e`). Live-match concerns — negotiation, deadlines, the turn loop — belong to `M5-003`/`M5-004`/`M5-007` |
| M5-002a | Expose the four tools on a local FastMCP server | DONE | `adapters.build_server` exposes `negotiate`, `receive_turn`, `submit_audit`, `receive_control`, each taking one argument with no envelope. A test asserts `receive_move` — the withdrawn Option-B name — is **not** reachable. See `SIM_WIRE_PROTOCOL.md` |
| M5-002b | Confine every FastMCP import to an adapters layer | DONE | A guard test walks every module under `src/` and fails on any non-`adapters` importer of fastmcp |
| M5-002c | Implement the outbound client against the opponent URL | DONE | `adapters.FastMCPClient` implements `peer.PeerTransport`; argument keywords come from `peer.TOOL_ARGUMENTS`, the single place they are written, so inbound and outbound cannot drift apart |
| M5-002d | Decide and document the tool acknowledgement semantics | DONE | **Decision:** tools never validate and never raise; `drain` validates afterwards and a failure there is a recorded game outcome. This diverges from the reference, which validates structurally inside the tool and raises. The divergence is kept because a *tampered audit is structurally well-formed* yet must be scored as a technical loss (`AE-19`); a peer that raises invites the opponent to retry a decided loss as a transport fault. Recorded in `adapters/fastmcp_server.py` and `PRD_p2p_mcp.md` |
| M5-002e | Prove a message round-trips between two processes | DONE | **Book stage-2 milestone closed.** `tests/integration/test_localhost_two_processes.py` spawns a real second interpreter on a free port, sends a turn over HTTP, and reads back the JSONL transcript that process wrote; the validating PID is asserted not to be this one (`AE-1`/`AE-2`). A tampered audit is also driven across the socket and confirmed to arrive and be *scored*, not lost as a transport error `[AE-19]` |
| M5-003 | Enforce accepted idempotency, acknowledgement, and duplicate handling | PENDING | Duplicate/reorder tests |
| M5-003a | Enforce idempotency keys across retries | PENDING | A retried turn cannot double-apply |
| M5-003b | Reject replayed message identifiers | PENDING | Deterministic rejection, not silent drop |
| M5-004 | Implement deadlines, watchdog, controlled recovery, and backpressure | PENDING | Timeout/crash/recovery tests |
| M5-004a | Attach a timestamp and expiry to every request | DONE | `services/deadlines.Deadline` carries `started` and `expires`, and the boundary itself counts as expired. Book §8.4.1's boxed note is the spec — *"Missing a Deadline is a Failure, Not Patience"* — permitting exactly two outcomes: retry, or declare a technical loss and clear the queue cleanly. Time is **injected**, so a timeout is proven by passing a number rather than sleeping `[book §8.4.1]` |
| M5-004b | Implement bounded retry with backoff | DONE | `services/deadlines.attempt` gives each try its own expiry and stops at `max_retries`, raising `DeadlineError` so the caller can declare a technical loss. **Key names confirmed against the pinned reference 2026-08-01**: `network_and_league.response_timeout_sec` (30), `rate_limiter_gatekeeper.retry_backoff_sec` (5), `.max_retries` (3), `network_and_league.watchdog_timeout_sec` (60) — all in the **shared, signed** match object, so neither peer can give itself a longer rope. A slow attempt that overruns its own expiry is **not** retried. Appendix F table 19 marks the first three `Minimum` and the watchdog `Negotiation` `[AF-t19]` |
| M5-004c | Trip the watchdog at `watchdog_timeout_sec` | PENDING | Default 60 s `[AF-t19]`; the book's 180 s code sample is illustrative `[AE-6]` |
| M5-004d | Persist state and shut down cleanly on trip | PENDING | `persist_state()` then `controlled_shutdown()` `[AE-7]` |
| M5-004e | Route a mid-turn disconnect to a terminal technical loss | PENDING | No deadlock path out of the awaiting-reveal state |
| M5-004f | Enforce FIFO queue depth and backpressure | PENDING | `queue_depth` from config `[G§5.3]` |
| M5-005 | Validate localhost and public-tunnel paths against identical fixtures | PENDING | Connectivity and failure evidence |
| M5-005a | Keep tunnel credentials out of shared configuration | PENDING | `[AE-39]`; secrets stay private `[G§7.4]` |
| M5-005b | Exchange only the public URL | PENDING | `[AE-10]`; provider choice stays local |
| M5-005c | Rehearse a full game across two machines | PENDING | Book stage-5 milestone |
| M5-006 | Run the Thief in its own process under its own config directory | IN PROGRESS | `[AE-1]` `[AE-2]`: the separate-process test proves the Thief runs and validates in its own interpreter with no shared memory or module state. The **own config directory** half needs the private-TOML loader (`M5-002f`) and is not done |
| M5-002f | Read the opponent URL from private configuration only | DONE | `shared/private_config.py` reads `[network].opponent_url` from one explicit private TOML path and is the only way in to an opponent address; `assert_no_network_address` guards the way out, refusing a shared object that carries an address either by member **name** or by **value**, since either check alone is easy to slip past. `config/game.toml.example` added, matching book p. 131 and the reference's own `config/thief/game.toml`. **Confirmed against the pinned wire reference 2026-07-31** before implementing: separate `config/police/` and `config/thief/` directories, address at `[network].opponent_url`, and the shared negotiated JSON never carries a URL, port, host, or any address — local settings must not "leak into the agreement". This closes the private keys `ADR-0004` left `PENDING` `[AE-10]` `[AE-39]` |
| M5-002g | Fail cleanly on an unreachable opponent URL | DONE | `http://127.0.0.1:1/mcp` raises `TransportError`, never a crash |
| M5-002h | Fail cleanly on a malformed opponent response | DONE | A reply that is not a JSON object raises `TransportError` deterministically. The client is **liberal** about the ack shape — `{"ok": true}`, `{"status": "ok"}`, and `{"status": "delivered"}` are all accepted — because the profile never fixed the opponent's shape; only an explicit `ok: false` / failing `status` / non-empty `error` is a `PeerRejectionError` |
| M5-002i | Keep the client stateless between calls | DONE | `__slots__` makes hidden per-turn state impossible rather than merely absent; each call opens and closes its own session |
| M5-002j | Document the client contract in `PRD_p2p_mcp.md` | DONE | Call shapes, the two-way fault mapping, and the acknowledgement decision recorded |
| M5-007 | Implement the turn loop around the transport | DONE | `orchestration/` now holds the declared phase machine, `run_turn`, and `run_sub_game_over_wire`. Order corrected against the reference: **await → compute → apply → seal → send**, not compute-first. **This peer opens** — the book gives the Thief the first move of every cycle, so step 1 does not wait; a Thief that waited would deadlock against a Cop correctly waiting for it. Termination is *not* the Cop's mirror: a `capture_claim` is **checked against local truth, never believed**, because the Thief is the peer that knows where it stood, and an incorrect claim is simply the game continuing. 84 tests across four modules plus four over a real socket |
| M5-007a | Drive the loop from the protocol state machine | DONE | `orchestration/phases.py`: the specification's table transcribed unchanged, refusing every undeclared transition **by name** `[AE-004]` `[AE-005]`. Most of the tests are refusals on purpose — a machine that accepted everything would pass a happy-path test and still deadlock the first time a peer went out of order, so all 28 undeclared pairs are asserted to raise. `TECHNICAL_LOSS` is reachable only where the table allows |
| M5-007b | Make one turn atomic against partial failure | DONE | A turn is sealed **exactly once**; a failed send never re-seals, because a second hash for one step is an audit mismatch and an automatic zero `[AE-019]`. Deciding and sealing were moved into `COMPUTING_MOVE`, the only phase the table permits `TECHNICAL_LOSS` from — they were briefly inside `COMMITTING`, where a seal failure had **no legal exit** and stranded the machine mid-turn. The companion peer carried the same latent defect and was corrected the same day |
| M5-007c | Bound the loop by the negotiated step limit | DONE | `run_sub_game_over_wire` is bounded by `survival_threshold` and validates it, and the horizon is **inclusive** — completing the final step uncaught is a win, not one step short (`U-022`) `[AF-t15]` |
| M5-007d | Emit a structured log line per phase transition | DONE | `run_turn` takes an `on_transition` callback fired on every phase entered, and `PhaseMachine.history` keeps the ordered record. The log manager that consumes them is `M5-008` |
| M5-008 | Implement the log manager subsystem | PENDING | Append-only, structured, sufficient to reconstruct the match |
| M5-008a | Record every sent and received message | PENDING | Enough to satisfy the end-of-game audit `[AE-36]` |
| M5-008b | Record commitments and, at audit time, nonces | PENDING | Nonces written only after the final reveal `[AE-18]` |
| M5-008c | Keep the log append-only | PENDING | No in-place edit path exists |
| M5-008d | Write logs under a per-match path | PENDING | Matches never overwrite each other |
| M5-009 | Implement the deadline tracker subsystem | PENDING | Every outbound request carries an expiry and is reaped on breach |
| M5-009a | Reap expired requests rather than awaiting them | PENDING | Past expiry is failure, never patience `[book §9]` |
| M5-009b | Clear the queue cleanly on a declared technical loss | PENDING | No orphaned pending request survives |
| M5-010 | Handle opponent-side rejection responses | PENDING | A peer's content rejection is scored, not retried forever |
| M5-010a | Distinguish rejection from transport failure | PENDING | Retry applies to one and not the other |
| M5-010b | Terminate deterministically on an unrecoverable rejection | PENDING | The match reaches a defined terminal state |
| M5-011 | Prove the runtime under adversarial peer behaviour | PENDING | A hostile or broken opponent cannot hang or corrupt this peer |
| M5-011a | Survive a peer that never responds | PENDING | Deadline plus watchdog produce a terminal outcome |
| M5-011b | Survive a peer that responds out of order | PENDING | The state machine rejects the transition `[AE-5]` |
| M5-011c | Survive a peer that replays an earlier message | PENDING | Idempotency guard rejects it |
| M5-011d | Survive a peer that sends oversized or malformed input | PENDING | Validation rejects before domain code runs |
| M5-011e | Survive a peer that disconnects mid-audit | PENDING | The audit outcome is still decided and recorded |
| M5-012 | Complete the book's stage-2 localhost milestone | DONE | Book p. 105: a message sent by peer A on localhost is received correctly by peer B. **Closed by `M5-002e`** — `tests/integration/test_localhost_two_processes.py` spawns a real second interpreter, sends over HTTP, and reads back the transcript that process wrote. This row duplicated `M5-002e` and was left `PENDING` after it closed; reconciled 2026-08-01 when re-reading the ledger. Its sub-rows `M5-012b`..`M5-012e` are superseded by `M5-014` (negotiate) and `M5-007` (turn, sub-game, audit) |
| M5-012a | Launch two peers on distinct localhost ports | PENDING | Separate processes, separate config directories `[AE-1]` |
| M5-012b | Exchange one negotiate round trip | PENDING | Offer out, acceptance back, both sides agree the terms hash |
| M5-012c | Exchange one turn round trip | PENDING | Commit out, acknowledgement back, reveal accepted |
| M5-012d | Complete one full sub-game over the wire | PENDING | Terminates on capture or survival, not on timeout |
| M5-012e | Complete the end-of-game mutual audit over the wire | PENDING | Both logs reconcile; every commitment recomputes |
| M5-012f | Record the run as stage-2 milestone evidence | PENDING | The book requires observed behaviour, not written code |
| M5-013 | Document the runtime architecture | PENDING | `PRD_p2p_mcp.md` and `PLAN.md` describe the gateway, subsystems, and turn loop |
| M5-013a | Draw the subsystem diagram | PENDING | Gateway plus five subsystems, no peer-to-peer links `[G§20.1]` |
| M5-013b | Document every failure path and its outcome | PENDING | One row per fault class and its terminal state |
| M5-014 | Implement negotiation and mismatch refusal | DONE | `protocol/agreement.py` owns the policy — Appendix F floors, participants, and what a refusal must say — while `handshake.py` keeps the signing mechanics. `accept_offer` gates in a deliberate order: structure, signature, required terms, Appendix F, then equality with our own terms. It is **wired into the live handler**: `InboundPeer(my_terms=…)` applies it and refuses by name, and without terms still only shape-checks, which is the state before the shared match object is loaded. 33 unit tests plus 6 live-handler tests `[AE-11]` `[AE-12]` |
| M5-014a | Build and send a match offer | DONE | `Handshake.signed()` returns terms, the public challenge nonce, the signature over those terms, and role-free identity. **Deviation from this row's original wording, deliberate:** the offer does *not* carry a participants list. The reference establishes participants from the two exchanged identities rather than as a message field, and inventing one would put a term in our signature that no classmate signs. `validate_participants` covers the agreed-between list wherever the runtime holds one |
| M5-014b | Compare `config_sha256` byte-for-byte before play | DONE | `accept_offer` compares the terms themselves, which is strictly stronger than comparing the hash because only it can say **which** term differs — and rule 11 wants a refusal the opponent can act on. A test pins that the two never disagree: agreement implies an identical `config_sha256`, and a differing term produces both a different hash and a refusal naming it `[AE-11]` |
| M5-014c | Validate participant identity and ordering | DONE | `validate_participants` requires exactly two distinct non-empty named groups and, when a group id is supplied, that it is one of them. Ordering needs no separate rule: the list lives inside the hashed object, so both peers already hold the same order |
| M5-014d | Refuse below-minimum and altered fixed values | DONE | `check_appendix_f`: `smell_grid_size`, `decay_per_step`, `emit_intensity`, and `num_games` are `FIXED` (exact match); `board_size`, `max_steps`, and `barriers_max` are `MINIMUM` (may move only in the harder direction). `tests/unit/test_appendix_f.py` pins the statuses against `docs/PARAMETERS_BASELINE.md` — tables 13, 15, 16, 18 — so a silently edited constant fails here rather than at a match `[AE-12]` `[AF-§1]` |
| M5-014e | Prove propose and accept directions both pass | DONE | Two `Handshake` peers under different group identities each accept the other's offer against the same terms, with no profile file edited in either direction |
| M5-015 | Exchange and verify the scent-model lock at negotiation | PENDING | Mismatch refuses the match before the first move `[AE-23]` |
| M5-016 | Implement backpressure signalling | PENDING | A full queue signals rather than silently dropping `[G§5.3]` |
| M5-017 | Prove two peers reach the same terminal outcome | PENDING | Both sides agree the result before any report is composed |
| M5-018 | Keep transport concerns out of the SDK | PENDING | A guard test proves the SDK imports no transport module |

---

## M6 — Scent, belief and private strategy

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M6-001 | Implement confirmed multiplicative scent physics | PENDING | Emission/decay/clipping tests |
| M6-001a | Emit a 5×5 field centred on the agent | PENDING | Centre `τ = 0.9` `[AF-t16]` `[PRD-scent]` |
| M6-001b | Apply `τ(t+1) = max(0, (1-ρ)·τ(t) + Δτ)` per full turn | PENDING | Decay runs once after both sides act |
| M6-001c | Pin the radial profile with numeric vectors | PENDING | 0.90 / 0.62 / 0.20 / 0.14 / 0.04 to documented precision |
| M6-001d | Clip intensities to non-negative | PENDING | A never-visited cell reads 0 |
| M6-002 | Consume accepted public scent observations in the accepted order | PENDING | Shape/order/boundary tests |
| M6-002a | Populate and parse `smell_grid` as `{"r,c": intensity}` | PENDING | Matches `SIM_WIRE_PROTOCOL.md` |
| M6-003 | Maintain a Thief-local belief without objective Cop truth | PENDING | Privacy and update tests |
| M6-003a | Maintain a board-sized probability matrix | PENDING | Sized to the negotiated grid, not the book's 10×10 illustration |
| M6-003b | Apply Bayes with a per-hint trust factor | PENDING | A hint contradicted by scent lowers its own trust weight |
| M6-003c | Normalize without dividing by zero | PENDING | A zero-evidence update leaves a valid distribution |
| M6-003d | Prove the belief never reads objective truth | PENDING | `[AE-8]` `[AE-9]` |
| M6-003e | Decode an inbound hint into a belief-space update | PENDING | Free text maps to evidence without a coordinate protocol `[AE-27]` |
| M6-003f | Lower a hint's trust when scent contradicts it | PENDING | A claimed direction with no scent residue is evidence of a lie |
| M6-004 | Add private strategy improvements behind legal validation | PENDING | Determinism/deadline/no-network tests |
| M6-004a | Maximise distance from the believed Cop cell | PENDING | Legal actions only; deterministic tie-breaks |
| M6-004e | Keep every emitted action legal under the domain layer | PENDING | Belief may misdirect; it may never produce an illegal move |
| M6-004f | Bound per-turn decision time | PENDING | The policy returns within the negotiated response timeout `[AF-t19]` |
| M6-004g | Keep the policy deterministic and reproducible | PENDING | Identical observations yield an identical action sequence |
| M6-004h | Load strategy tuning from the private TOML only | PENDING | No tuning value enters the shared JSON `[ADR-0004]` |
| M6-004b | Keep the LLM out of movement decisions | PENDING | `[AE-25]` `[ADR-0007]`; the move is always pure Python |
| M6-004c | Enforce natural-language-only hints within the word limit | PENDING | `[AE-26]` mandatory, `[AE-27]` forbids coordinate protocols; 15 words `[AF-t14]` |
| M6-004d | Ship a zero-token template provider as default | PENDING | A whole series must be playable at zero tokens `[AF-t21]` |
| M6-005 | Lock and exchange the scent-model hash before the first move | PENDING | Appendix E rule 23 (deviation cancels the game): the agreed emission/decay model is canonicalised, SHA-256 locked pre-game, exchanged at negotiation, and any mismatch refuses the match. The locked formula follows the DEV-SPEC reading — at `ρ = 0.10` the factor `(1-ρ)` **retains** 90% of prior scent. The book's "reduced by 90%" (p. 43) and "`ρ` toward 1.0 saturates the board" (p. 46) are arithmetic errors and must not be implemented |
| M6-005a | Canonicalise the scent model to hashable bytes | PENDING | Formula, constants, and field size in one canonical record |
| M6-005b | Exchange and compare the lock at negotiation | PENDING | Mismatch refuses the match before the first move |
| M6-005c | Record the arithmetic correction in the report | PENDING | Book p. 43 and p. 46 errors disclosed under the p. 5 clause |
| M6-006 | Serialize and parse the scent observation on the wire | PENDING | The observed field survives a round trip without precision loss |
| M6-006a | Encode the emitted field into `smell_grid` | PENDING | Sparse map keyed `"r,c"`; empty cells omitted, not zero-filled |
| M6-006b | Parse an opponent field defensively | PENDING | Out-of-range, non-numeric, and off-board keys reject |
| M6-006c | Pin the numeric precision on the wire | PENDING | Both peers must agree, or the locked model hash means nothing |
| M6-007 | Prove the scent model is symmetric and involuntary | PENDING | Emission follows movement automatically; no path can suppress or fake it |
| M6-007a | Emit on every action including `STAY` | PENDING | Staying still still deposits scent `[book §6]` |
| M6-007b | Read only the opponent's field, never one's own | PENDING | A test proves own-scent is never used as evidence |
| M6-007c | Make suppression impossible by construction | PENDING | No flag or branch can skip emission |
| M6-008 | Implement hint generation | PENDING | A hint is produced each turn, truthful or bluffed, within the agreed limits |
| M6-008a | Carry an explicit truth/bluff intent flag | PENDING | Sealed in the commitment so it cannot be revised later |
| M6-008b | Generate from a zero-token template provider | PENDING | Default path; no network, no account `[AF-t21]` |
| M6-008c | Enforce the word limit at generation time | PENDING | 15 words default `[AF-t14]` |
| M6-008d | Reject a generated hint that encodes coordinates | PENDING | `[AE-27]`; a validator, not a convention |
| M6-008e | Support landmark hints when a map area is agreed | PENDING | Generic landmarks when `map_area` is empty |
| M6-008f | Trigger any model provider only every N steps | PENDING | `every_n_steps` bounds consumption |
| M6-009 | Implement hint consumption | PENDING | An inbound hint updates belief without ever being trusted blindly |
| M6-009a | Parse an inbound hint without executing it | PENDING | Text is evidence, never an instruction |
| M6-009b | Weight the hint by the sender's running trust score | PENDING | Repeated contradiction lowers the weight |
| M6-009c | Tolerate an absent, empty, or over-long hint | PENDING | Missing evidence is not an error state |
| M6-010 | Prove the strategy layer under observation tests | PENDING | Behaviour stays legal and deterministic under every observation shape |
| M6-010a | Test with no scent and no hint | PENDING | A uniform belief still yields a legal action |
| M6-010b | Test with contradictory scent and hint | PENDING | The physical evidence wins |
| M6-010c | Test with a saturated scent field | PENDING | No overflow, no division by zero |
| M6-010d | Test with the Cop adjacent and with the Cop far | PENDING | Both produce sane, legal, distinct choices |
| M6-010e | Test that repeated runs are byte-identical | PENDING | Determinism is a submission property, not an accident |
| M6-011 | Benchmark the per-turn decision cost | PENDING | Belief update plus policy stays well inside the response timeout |
| M6-011a | Measure worst-case belief update time | PENDING | Measured at the negotiated grid size |
| M6-011b | Record the measurement in the research evidence | PENDING | Feeds `M9-006` and the computational-fairness claim |
| M6-012 | Document the perception and strategy layers | PENDING | `PRD_scent_belief.md` and `PRD_strategy.md` match the built behaviour |
| M6-012a | Document the belief update rule and its trust factor | PENDING | Formula, inputs, and normalisation |
| M6-012b | Document the locked scent model and its hash | PENDING | The exact bytes that were locked `[AE-23]` |
| M6-013 | Keep the verbal layer strictly optional | PENDING | Disabling every provider still produces a complete, legal game |
| M6-013a | Prove a full series runs at zero tokens | PENDING | Template provider only `[AF-t21]` |
| M6-013b | Prove a provider outage never forfeits a turn | PENDING | Fallback is automatic and silent to the opponent |
| M6-014 | Add regression vectors for the scent field | PENDING | Stored expected fields guard against silent physics drift |
| M6-015 | Measure strategy quality against the baseline | PENDING | Belief-driven evasion must beat the blind baseline or be reverted |
| M6-015a | Define the comparison protocol | PENDING | Fixed seeds, fixed opponent policy, repeated runs |
| M6-015b | Record the result either way | PENDING | A negative result is evidence, not a failure to hide |
| M6-016 | Prove belief and scent never leak beyond the agreed wire fields | PENDING | Internal certainty is private; only the agreed observation crosses |
| M6-017 | Record the belief model in the academic report | PENDING | Bayes update, trust factor, and the distance objective `[AE-42]` |
| M6-018 | Offer the scent implementation to the opponent for parity | PENDING | The book recommends sharing the scent source so both run identical logic `[book §6]` |
| M6-019 | Prove evasion improves survival over random legal movement | PENDING | The baseline must beat chance before belief is added |
| M6-019a | Establish the random-legal-move control | PENDING | Fixed seeds, repeated runs |
| M6-019b | Record survival rate for each policy | PENDING | Feeds `M9-007a` |
| M6-020 | Handle the belief update when the Cop is provably adjacent | PENDING | Certainty collapses the distribution without breaking normalisation |
| M6-021 | Handle the first turn with no prior observation | PENDING | The agreed start positions are public; belief begins there |
| M6-022 | Keep scent physics identical to the locked model at run time | PENDING | A runtime assertion compares against the locked hash `[AE-23]` |
| M6-023 | Bound belief memory across a long series | PENDING | No unbounded history accumulation over six sub-games |
| M6-024 | Prove hint generation never blocks the turn deadline | PENDING | Generation is bounded or skipped, never awaited indefinitely |
| M6-025 | Test the strategy against a barrier-heavy board | PENDING | Near-quota barrier layouts still yield legal, sane evasion |
| M6-026 | Test the strategy when only `STAY` is legal | PENDING | A fully enclosed Thief still returns a legal action before capture resolves |
| M6-027 | Document the trust-decay policy for repeated lies | PENDING | How quickly trust falls and whether it recovers |
| M6-028 | Add a determinism regression test across releases | PENDING | A stored action sequence guards against silent policy drift |

---

## M7 — Series orchestration, artifacts, gatekeeper and reporting

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M7-001 | Orchestrate the accepted six-sub-game series lifecycle | PENDING | Series state/scoring tests |
| M7-001a | Run six sub-games under one series identity | PENDING | `[AF-t18]`; `sub_game_number` carried into artifacts |
| M7-001b | Implement the confirmed six-sub-game role schedule | PENDING | `U-021` closed 2026-07-29 on a coordinator-relayed lecturer answer: sub-games 1, 3, 5 natural role, 2, 4, 6 swapped, Thief moves first. Keep the schedule injected rather than hard-coded so a later correction is a one-line change; see `C-012` |
| M7-001c | Aggregate cumulative series score | PENDING | Per-sub-game lines sum to a series result |
| M7-001d | Apply the tie award on a cumulative tie | PENDING | `[AF-t17]` |
| M7-002 | Build accepted declaration, config, log, and result artifacts | PENDING | Schema/link/hash tests |
| M7-002a | Emit `declaration_<game_id>.json` | PENDING | Groups, members, both repos, MCP addresses, hardware, model, tokens, times |
| M7-002b | Emit `config_<game_id>_g<NN>.json` | PENDING | Quantitative parameters plus crypto locks and identity |
| M7-002c | Emit `log_<game_id>_g<NN>.json` | PENDING | Step-by-step commit-reveal, hashes, nonces |
| M7-002d | Emit `result_<game_id>.json` | PENDING | Per-group scores and cumulative result; this is the emailed report |
| M7-002e | Share one `game_uid` across all four artifacts | PENDING | Filenames derive from `game_id` `[AF-§3]` |
| M7-002f | Carry four repository links in the result artifact | PENDING | `[AE-49]`; two per group |
| M7-002g | Carry the per-game commit hash and total tokens | PENDING | `[AE-53]` `[AE-54]` |
| M7-003 | Implement the centralized external-call gatekeeper | PENDING | FIFO/rate/retry/backpressure tests |
| M7-003a | Route every external call through one gatekeeper | PENDING | No service calls an external API directly `[G§5.1]` |
| M7-003b | Implement the token bucket | PENDING | `tokens ← min(C, tokens + r·Δt)`; allow iff `tokens ≥ 1` `[AE-28]` |
| M7-003c | Queue overflow rather than rejecting | PENDING | FIFO to `queue_depth`, then backpressure `[G§5.3]` |
| M7-003d | Read every limit from configuration | PENDING | No hard-coded rate values `[G§7.2]` `[AF-t19]` |
| M7-004 | Implement accepted private verbal-provider modes | PENDING | Mocked provider/fallback tests |
| M7-004a | Fall back deterministically on provider failure | PENDING | A blocked provider never stalls a turn |
| M7-005 | Send the mutually agreed final JSON report through Gmail | PENDING | Mocked recipient/body/attachment/agreement tests |
| M7-005a | Restrict the OAuth scope to `gmail.send` | PENDING | `[AE-30]`; no read or modify scope |
| M7-005b | Keep `credentials.json` and `token.json` git-ignored | PENDING | `[AE-39]` `[AE-40]` |
| M7-005c | Send JSON as an attachment only | PENDING | `[AE-33]` `[AE-34]`; free text is rejected |
| M7-005d | Send to the confirmed reporting address | PENDING | `rmisegal+uoh26finalgame@gmail.com` per lecturer answer `AF-020`; the book's Table 20 spelling `rimesegal` is a source typo |
| M7-005e | Back off on HTTP 429 | PENDING | Immediate resend risks account suspension `[book §12]` |
| M7-005f | Run the full mutual audit before agreeing a result | PENDING | `[AE-36]` |
| M7-005g | Send independently of the opponent | PENDING | `[AE-32]` `[AE-35]`; a side that does not send scores nothing |
| M7-006 | Implement the Quota Manager and DOS Detector gates | PENDING | Appendix E rules 28/29 and chapter 9 require **three** gates in series before any Gmail call: a daily Quota Manager, the token bucket (`M7-003`), and a DOS detector that locks the pipeline on runaway-send patterns. Fail-fast at the first rejecting gate; the lock is observable |
| M7-006a | Implement the daily quota counter | PENDING | Exhausted quota stops all further sends |
| M7-006b | Implement the DOS detector and pipeline lock | PENDING | Runaway-send patterns lock the pipeline `[AE-29]` |
| M7-006c | Prove fail-fast ordering across the three gates | PENDING | Quota → bucket → detector |
| M7-007 | Declare games already played against each opponent | PENDING | Appendix E rules 37/38: every game start carries an accurate count of prior counted games against that opponent, derived from emitted result artifacts rather than hand-entered. A false declaration is absolute disqualification, so the count must be reproducible from the artifact set |
| M7-007a | Derive the count from emitted result artifacts | PENDING | No hand-entered figure enters the declaration |
| M7-007b | Exclude warm-up games from the counted total | PENDING | `[AE-52]`; warm-ups are permitted but uncounted |
| M7-008 | Attach every game's configuration artifact to the repository | PENDING | Appendix F.2 items 3 and 4: each game's configuration artifact is named from its `game_id` and committed, so any past game's exact configuration remains retrievable |
| M7-008a | Commit each game's config under a `game_id`-derived name | PENDING | Artifacts from different games cannot collide |
| M7-008b | Prove any past game's config is retrievable from the repo | PENDING | A retrieval test walks the committed set |
| M7-009 | Account for LLM tokens across a series | PENDING | Per-game and per-series totals counted, sealed at Step-0, and reported `[AE-54]` |
| M7-010 | Emit warm-up games as uncounted | PENDING | A warm-up produces artifacts but never enters the counted total `[AE-52]` |
| M7-011 | Persist artifacts atomically | PENDING | A crash mid-write cannot leave a half-written artifact that later fails audit |
| M7-012 | Validate every emitted artifact against its schema | PENDING | An artifact that fails its own schema is never sent |
| M7-012a | Validate the declaration artifact | PENDING | Required identity, hardware, and timing fields present |
| M7-012b | Validate the config artifact | PENDING | Every Appendix F parameter present with a legal value |
| M7-012c | Validate the log artifact | PENDING | Every step carries commitment, nonce, move, and hint |
| M7-012d | Validate the result artifact | PENDING | Scores, four links, commit hash, and token totals present |
| M7-012e | Reject an artifact set whose `game_uid` values disagree | PENDING | All four must share one identity `[AF-§3]` |
| M7-013 | Implement the OAuth setup path | PENDING | First run creates a token; later runs refresh without human action |
| M7-013a | Run the consent flow once and store the token locally | PENDING | `token.json` created, never committed `[book App. A]` |
| M7-013b | Refresh the access token automatically | PENDING | The refresh token gives months of autonomy |
| M7-013c | Fail closed when no credential is present | PENDING | No silent skip of a mandatory report |
| M7-013d | Document the five setup steps for a fresh machine | PENDING | Reproducible by a teammate `[G§2.1]` |
| M7-014 | Compose the report email | PENDING | MIME message with a JSON attachment and a machine-stable subject |
| M7-014a | Attach the result artifact as a file | PENDING | Attachment only; body text is never the report `[AE-34]` |
| M7-014b | Use a deterministic subject naming the game | PENDING | Auto-assignment depends on it `[AE-45]` |
| M7-014c | Base64url-encode and send through the API | PENDING | `users().messages().send` with `userId="me"` |
| M7-015 | Prove reporting under failure | PENDING | No failure mode silently loses a report |
| M7-015a | Retry after a 429 with backoff | PENDING | Respect the throttle rather than hammering `[book §12]` |
| M7-015b | Surface a permanently failed send loudly | PENDING | An unsent report costs the game's points `[AE-32]` |
| M7-015c | Never send twice for one game | PENDING | Duplicate reports risk a conflict verdict `[AE-35]` |
| M7-016 | Implement result agreement with the opponent | PENDING | Both sides converge on one result before either reports |
| M7-016a | Exchange the computed outcome after the audit | PENDING | Agreement follows audit, never precedes it `[AE-36]` |
| M7-016b | Detect and record a disagreement | PENDING | A conflict is 0/0 for both and must be visible `[AE-35]` |
| M7-016c | Refuse to report an unagreed result | PENDING | Reporting a disputed outcome invites the conflict sanction |
| M7-017 | Implement series-level score aggregation evidence | PENDING | The cumulative figure is reproducible from the artifact set |
| M7-017a | Recompute the series total from stored artifacts | PENDING | No in-memory-only total is trusted |
| M7-017b | Apply the diversity reward for a new opponent | PENDING | `[AF-t18]`; a repeat opponent adds nothing |
| M7-018 | Run a full local series rehearsal before any counted game | PENDING | Six sub-games, four artifact families, audit, agreement, and a mocked send |
| M7-018a | Rehearse with a deliberately failing sub-game | PENDING | A technical loss still produces a complete artifact set |
| M7-018b | Rehearse with a tampered audit | PENDING | Detection, scoring, and reporting all behave |
| M7-019 | Document the reporting pipeline | PENDING | `PRD_gatekeeper_reporting.md` matches the built gates and flow |
| M7-020 | Emit the declaration before the first move of each game | PENDING | The pre-game declaration is signed and fixed before play begins |
| M7-020a | Include both groups and their members | PENDING | Identity is public and agreed |
| M7-020b | Include both repository links per group | PENDING | Four links total `[AE-49]` |
| M7-020c | Include the MCP addresses in use | PENDING | Public URLs only; no credential |
| M7-020d | Include the hardware and model declaration | PENDING | Carried from Step-0 `[AE-24]` |
| M7-020e | Include the agreed token limit and game times | PENDING | Start and end recorded |
| M7-021 | Bind the config artifact to the negotiated match | PENDING | The emitted config is the one actually played, not a template |
| M7-021a | Include every quantitative parameter | PENDING | All Appendix F values with their agreed settings |
| M7-021b | Include the cryptographic locks | PENDING | Config hash and the scent-model lock `[AE-23]` |
| M7-022 | Make the log artifact sufficient for an independent audit | PENDING | A third party can re-verify without our code |
| M7-022a | Record each step's commitment and revealed payload | PENDING | Enough to recompute every hash |
| M7-022b | Record nonces only in the final audit section | PENDING | Nonce secrecy holds until the end `[AE-18]` |
| M7-022c | Record the hint and intent per step | PENDING | The verbal layer is auditable too |
| M7-023 | Keep artifact emission independent of transport health | PENDING | A disconnected game still produces its artifact set |
| M7-024 | Version the artifact schemas | PENDING | A schema change is visible, not silent `[G§8.1]` |

---

## M8 — GUI, replay, interoperability and security hardening

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M8-001 | Build a live Thief local-truth GUI through the SDK | PENDING | View-model truth-boundary tests |
| M8-001a | Render the belief heatmap | PENDING | Deeper colour means higher probability `[PRD-gui]` `[ADR-0009]` |
| M8-001b | Render the turn banner | PENDING | Green `YOUR TURN`, grey `LOCKED` after commit |
| M8-001c | Lock input while the banner is grey | PENDING | Out-of-turn input is ignored |
| M8-001d | Prove the objective board is never renderable | PENDING | `[AE-8]` `[AE-9]` |
| M8-002 | Build replay UI on the accepted verifier | PENDING | Valid/malformed/reordered/tampered replay tests |
| M8-002a | Load a saved match log and step forward/back | PENDING | `[AE-20]` mandatory `[PRD-replay]` |
| M8-002b | Recompute every step's hash and compare | PENDING | Uses the M4 construction |
| M8-002c | Void the whole match on the first mismatch | PENDING | A single tampered step yields `TAMPERED` |
| M8-002d | Record why the book's chapter-7 verifier is not used | PENDING | Book p. 74 computes `SHA256("{nonce}|{move}")`, which cannot verify a chapter-5 commitment |
| M8-002e | Document the replay UI workflow and states | PENDING | Screens, controls, and both verdict states described `[G§10.2]` |
| M8-003 | Run bidirectional games against a neutral compliant-opponent harness | PENDING | Unknown-opponent E2E evidence |
| M8-003a | Rehearse against a stub that shares no source with this repo | PENDING | Independently authored; imports no project module |
| M8-003b | Prove both proposal and acceptance directions | PENDING | Neither direction needs a profile file edited |
| M8-003c | Rehearse against a real classmate agent before the counted league | PENDING | Warm-ups are permitted and uncounted `[AE-52]` |
| M8-004 | Harden secrets, identity, input validation, and dependency boundaries | PENDING | Security/privacy review and tests |
| M8-004a | Validate every inbound field before use | PENDING | Malformed peer input cannot reach domain code `[G§6.3]` |
| M8-004b | Bound memory and queue growth under sustained load | PENDING | No unbounded queue or leak over a long series |
| M8-004c | Apply Nielsen usability heuristics to both UIs | PENDING | Visibility of status, error prevention, recovery `[G§10.1]` |
| M8-005 | Exercise crash, timeout, mismatch, and tamper recovery end to end | PENDING | Failure-injection evidence |
| M8-005a | Inject crash, timeout, mismatch, and tamper faults | PENDING | Each produces a defined, logged outcome |
| M8-006 | Build the GUI view-model behind the SDK | PENDING | No widget touches domain or protocol code directly `[G§4.1]` |
| M8-006a | Expose a read-only snapshot for rendering | PENDING | The view cannot mutate game state |
| M8-006b | Update the view on state change rather than polling | PENDING | Redraw follows the state machine |
| M8-006c | Keep the GUI out of coverage requirements | PENDING | Omitted per the guidelines' coverage config `[G§6.2]` |
| M8-007 | Render the board and own position | PENDING | Own cell, known barriers, and turn number are visible |
| M8-007a | Render known barriers only | PENDING | A barrier appears only once disclosed `[AE-15]` |
| M8-007b | Render received hints as text | PENDING | The verbal channel is visible to the operator |
| M8-007c | Show the current score and step count | PENDING | Operator can see progress toward the threshold |
| M8-008 | Implement replay navigation | PENDING | Step forward, step back, and jump to a step |
| M8-008a | Recompute verification on every navigation | PENDING | The verdict is derived, never cached from load time |
| M8-008b | Show the per-step verdict alongside the board | PENDING | Operator sees where a match failed |
| M8-008c | Load a malformed log without crashing | PENDING | Corrupt input yields a clear error, not a stack trace |
| M8-008d | Detect a reordered log | PENDING | Step sequence is validated, not assumed |
| M8-009 | Run the security review | PENDING | Secrets, identity, input validation, and dependencies all reviewed |
| M8-009a | Confirm no secret is readable from any artifact | PENDING | Artifacts are shared; secrets must not travel in them `[AE-39]` |
| M8-009b | Confirm no private field crosses the wire | PENDING | Leakage vector per private field class |
| M8-009c | Review third-party dependencies and pin them | PENDING | `uv.lock` is authoritative `[G§8.4]` |
| M8-009d | Confirm the LLM path cannot influence a move | PENDING | Even with a provider enabled `[AE-25]` |
| M8-010 | Run the resource and endurance pass | PENDING | A full six-sub-game series runs without degradation |
| M8-010a | Run a long series and watch memory | PENDING | No unbounded growth across sub-games |
| M8-010b | Confirm clean shutdown releases every resource | PENDING | Sockets, files, and threads all closed |
| M8-011 | Document both interfaces | PENDING | Screens, states, and workflows described `[G§10.2]` |
| M8-011a | Document the live GUI workflow | PENDING | Turn banner states and what each means |
| M8-011b | Document accessibility considerations | PENDING | Colour is not the only signal `[G§10.2]` |
| M8-012 | Prove the replay app on a foreign log | PENDING | It verifies a log this peer did not write |
| M8-012a | Verify an opponent-produced log | PENDING | The audit is mutual; both logs must verify `[AE-36]` |
| M8-012b | Detect a foreign log that was tampered | PENDING | The detection path is not self-only |
| M8-013 | Rehearse the full failure matrix end to end | PENDING | Every fault class has an observed outcome, not a predicted one |
| M8-013a | Rehearse an opponent crash mid-series | PENDING | The series still produces artifacts |
| M8-013b | Rehearse a tunnel drop mid-turn | PENDING | Terminal outcome is defined, not a hang |
| M8-013c | Rehearse a config mismatch at negotiation | PENDING | The match is refused before play `[AE-11]` |
| M8-014 | Freeze the wire profile before the counted league | PENDING | No wire change after the first counted game without a coordinator decision |
| M8-015 | Capture the required submission screenshots | PENDING | Belief-map GUI and replay `Verified OK` `[AE-42]` |
| M8-015a | Capture the belief-map GUI screenshot | PENDING | Required README content |
| M8-015b | Capture the replay `Verified OK` screenshot | PENDING | Required README content |
| M8-015c | Capture a `TAMPERED` screenshot from a corrupted log | PENDING | Demonstrates the detection path |
| M8-015d | Make every screenshot reproducible from a stored fixture | PENDING | A grader can regenerate them |

---

## M9 — League evidence, submission and release

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M9-001 | Capture required league/game artifacts and repository commit evidence | PENDING | Reviewed evidence bundle |
| M9-001a | Play at least two counted games against at least two groups | PENDING | `[AE-31]`; below the minimum scores zero |
| M9-001b | Count only one scoring game per opponent | PENDING | `[AE-52]` |
| M9-001c | Secure opponent scheduling early | PENDING | External dependency on other teams; longest lead time |
| M9-002 | Complete all six academic README components | PENDING | README checklist |
| M9-002a | Describe the Dec-POMDP model | PENDING | State space, observations, uncertainty `[AE-42]` |
| M9-002b | Discuss the FastMCP communication dilemma | PENDING | Queues, failures, orchestrator, gatekeeper |
| M9-002c | Describe the implemented strategy | PENDING | Baseline evasion metrics and policy |
| M9-002d | Include learning curves if RL is used | PENDING | Not applicable while the policy stays deterministic |
| M9-002e | Embed the GUI and replay screenshots | PENDING | From `M8-001`/`M8-002` |
| M9-002f | Cross-link the companion repository | PENDING | `[AE-49]`; a link only, no repository access |
| M9-003 | Verify team identity, repository access, and current Moodle instructions | PENDING | Submission identity/access record |
| M9-003a | Confirm lecturer access to the repository | PENDING | Public, or shared with `rmisegal@gmail.com` |
| M9-003b | Use the eight-character team code | PENDING | `sharNamr`, confirmed 2026-07-28 `[AE-45]` |
| M9-003c | Confirm each member submits separately | PENDING | `[AE-44]` |
| M9-003d | Fill the Moodle template without moving fields | PENDING | `[AE-43]`; save as PDF |
| M9-004 | Run all gates from a clean frozen environment and complete security/provenance review | PENDING | Final validation record |
| M9-004a | Verify no secret exists anywhere in Git history | PENDING | `[AE-39]`; a secret committed once requires rotation |
| M9-005 | Create the reviewed annotated `v1.0-submission` release tag | PENDING | Tag points to accepted submission commit `[AE-41]` |
| M9-006 | Complete parameter research and sensitivity analysis | PENDING | Guidelines §9.1: systematic one-at-a-time experiments across the negotiable parameters, with the measured effect of each on match outcomes documented in tables |
| M9-006a | Sweep the negotiable board and movement parameters | PENDING | Grid size, barrier quota, step limit, survival threshold |
| M9-006b | Sweep the scent parameters within their fixed bounds | PENDING | Sensitivity to `ρ` and field size, noting both are `Fixed` for play |
| M9-006c | Record each parameter's measured effect on outcome | PENDING | Experiment tables with run counts, not anecdotes |
| M9-007 | Publish the results-analysis notebook and result visualisations | PENDING | Guidelines §9.2/§9.3: a notebook compares strategies and configurations, uses LaTeX for equations, cites academic references, and emits labelled high-resolution charts |
| M9-007a | Compare the baseline against belief-driven evasion | PENDING | Survival rate and mean survived turns over repeated runs |
| M9-007b | Emit labelled, accessible, high-resolution charts | PENDING | Clear axes, legend, caption `[G§9.3]` |
| M9-007c | Cite academic references and format equations in LaTeX | PENDING | `[G§9.2]` |
| M9-008 | Evidence ISO/IEC 25010, extension points, and concurrency safety | PENDING | Guidelines §12/§13/§15 (grouped as "Extension and Standards" in their §17.6): the eight quality characteristics are evidenced, extension seams are documented, and any threading or multiprocessing carries a thread-safety justification |
| M9-008a | Map the eight ISO/IEC 25010 characteristics to evidence | PENDING | One evidence pointer per characteristic `[G§13.1]` |
| M9-008b | Document the strategy and verbal-provider extension seams | PENDING | How a third party swaps a policy without editing core `[G§12.1]` |
| M9-008c | Justify every thread or process with a safety note | PENDING | Locks, queues, and shutdown paths described `[G§15.2]` |
| M9-009 | Provide the code-quality self-assessment | PENDING | `[AE-55]`; grades code quality only, never the league result |
| M9-009a | Score each guidelines requirement honestly | PENDING | SDK, OOP, gatekeeper, TDD, coverage, linter, secrets, `uv` `[G§19.1]` |
| M9-009b | Name the requirements not met and why | PENDING | An honest gap costs less than an overclaim |
| M9-010 | Assemble the league evidence bundle | PENDING | Every counted game's four artifacts, commit hashes, and sent-report proof |
| M9-010a | Archive the artifact set per counted game | PENDING | Retrievable by `game_id` |
| M9-010b | Record the commit hash that ran each game | PENDING | `[AE-53]`; code may change between games |
| M9-010c | Record proof that each report was sent | PENDING | An unsent report voids that game's points `[AE-32]` |
| M9-010d | Reconcile declared game counts against the artifact set | PENDING | A false declaration is absolute disqualification `[AE-38]` |
| M9-011 | Write the academic report body | PENDING | A scientific document, not an installation guide `[AE-42]` |
| M9-011a | Justify the architectural decisions and trade-offs | PENDING | ADRs summarised with rationale `[G§20.1]` |
| M9-011b | Present empirical results, not claims | PENDING | Numbers come from reproducible runs |
| M9-011c | Disclose every book contradiction relied on | PENDING | Book p. 5 requires where, what, and why; see `M0-006` |
| M9-011d | Cite the reference list | PENDING | Academic citation format `[G§9.2]` |
| M9-012 | Complete the installation and usage documentation | PENDING | A grader can install and run from the README alone `[G§2.1]` |
| M9-012a | Document system requirements and setup | PENDING | Including `uv` and Python version |
| M9-012b | Document every run mode and flag | PENDING | Peer, replay, and CLI paths |
| M9-012c | Document the configuration files and their effect | PENDING | Shared JSON versus private TOML `[ADR-0004]` |
| M9-012d | Document troubleshooting for common failures | PENDING | Tunnel down, opponent unreachable, credential missing |
| M9-012e | State the licence and third-party attributions | PENDING | `[G§2.1]` |
| M9-013 | Run the pre-submission dry run | PENDING | Clone fresh, install frozen, run every gate, run a game, produce artifacts |
| M9-013a | Verify from a clean clone on a second machine | PENDING | Nothing depends on an untracked local file |
| M9-013b | Verify every gate passes from that clean clone | PENDING | `G-001`…`G-009` |
| M9-013c | Verify the replay app validates a real stored match | PENDING | `[AE-20]` |
| M9-014 | Verify the four success metrics are demonstrable | PENDING | Coordination, adaptation, integrity, architecture — each with evidence `[book §11.4]` |
| M9-014a | Evidence coordination | PENDING | Turn management and P2P synchronisation without a judge |
| M9-014b | Evidence adaptation | PENDING | Belief updating under partial observation |
| M9-014c | Evidence integrity | PENDING | Commit-reveal plus a passing mutual audit |
| M9-014d | Evidence architecture | PENDING | Orchestrator and gatekeeper patterns under load |
| M9-015 | Confirm the addresses and links one final time | PENDING | `rmisegal@gmail.com` and `rmisegal+uoh26finalgame@gmail.com`; the book's Table 20 spelling is a typo |
| M9-015a | Confirm the repository is reachable by the grader | PENDING | Public, or shared `[AE-49]` |
| M9-015b | Confirm the cross-link to the companion repository resolves | PENDING | A link only; no repository access `[AE-49]` |
| M9-016 | Archive the final submission state | PENDING | The tagged commit, artifacts, and evidence bundle retained together |
| M9-017 | Verify the repository meets the minimum contents rule | PENDING | README, `/config`, PRD files, PLAN, and TODO all present `[AE-50]` |
| M9-017a | Confirm every mechanism has its own PRD | PENDING | `[G§2.3]`; one per algorithm or central mechanism |
| M9-017b | Confirm the docs folder matches the guidelines' structure | PENDING | `[G§2.2]` |
| M9-018 | Verify no secret exists anywhere in Git history | PENDING | `[AE-39]`; a secret committed once requires rotation |
| M9-018a | Scan the full history, not just the working tree | PENDING | A deleted secret remains in earlier commits |
| M9-018b | Confirm `.gitignore` covers every credential path | PENDING | `[AE-40]` |
| M9-019 | Verify the annotated tag points at the reviewed commit | PENDING | Not at a later commit written after the deadline `[AE-41]` |
| M9-020 | Prepare the handover note for the coordinator | PENDING | Current state, open unknowns, and next action in one page |
| M9-020a | List every task still open at submission | PENDING | Honest, not aspirational |
| M9-020b | List every unknown still unresolved | PENDING | With the reading chosen and why |
| M9-021 | Confirm the league minimums are actually met | PENDING | Two counted games against two different groups, both reported `[AE-31]` |
| M9-021a | Reconcile our count against each opponent's report | PENDING | Conflicting reports are 0/0 for both `[AE-35]` |
| M9-022 | Record the final self-assessed code-quality score | PENDING | Against the guidelines' quick-reference card `[G§19.1]` |
| M9-023 | Verify every emitted artifact is committed | PENDING | Appendix F.2 item 4; nothing exists only on a local disk |
| M9-024 | Close out the prompt-engineering log | PENDING | Final entry records the submission pass `[G§8.3]` |

---

## Appendix — Appendix E rule coverage map

Every mandatory rule maps to at least one owning task. A rule with no owning task is a
ledger defect, not an exemption.

| Rules | Subject | Owning tasks |
|---|---|---|
| 1, 2 | Two processes, no shared memory | `M5-006` |
| 3 | Orchestrator single gateway | `M5-001`, `M5-001a`…`c` |
| 4, 5 | State machine, illegal transitions | `M4-003` |
| 6, 7 | Watchdog | `M5-004c`, `M5-004d` |
| 8, 9 | Local-truth UI only | `M3-001a`, `M6-003d`, `M8-001d` |
| 10 | Public tunnel | `M5-005b` |
| 11, 12 | Identical config, raise-only minimums | `M1-014`, `M1-017` |
| 13, 14 | Orthogonal only, no diagonals | `M2-001b`, `M2-002a` |
| 15, 16 | Truthful barrier disclosure | `M3-002a` |
| 17, 18 | Commit-reveal, nonce secrecy | `M4-004`, `M4-004a`, `M4-004b` |
| 19 | Reject audit mismatch | `M4-005a` |
| 20 | Replay verification app | `M8-002`, `M8-002a`…`c` |
| 21, 22 | Truthful capture claims | `M2-004` |
| 23 | Scent-model hash lock | `M6-005`, `M6-005a`, `M6-005b` |
| 24 | Step-0 attestation | `M4-006`, `M4-006a`…`c` |
| 25 | LLM never decides moves | `M6-004b` |
| 26, 27 | Natural language only, no coordinate protocol | `M6-004c` |
| 28 | Token-bucket rate limiter | `M7-003b` |
| 29 | DOS detector | `M7-006b` |
| 30 | Authorized send only | `M7-005a` |
| 31 | Minimum different opponents | `M9-001a` |
| 32, 33, 34 | Automatic JSON reporting | `M7-005c`, `M7-005g` |
| 35 | Result agreement, separate reports | `M7-005g` |
| 36 | Full mutual audit | `M7-005f` |
| 37, 38 | Accurate game-count declaration | `M7-007`, `M7-007a`, `M7-007b` |
| 39, 40 | No secrets, `.gitignore` | `G-005`, `M7-005b`, `M9-004a` |
| 41 | Annotated submission tag | `M9-005` |
| 42 | Academic report | `M9-002`, `M9-002a`…`f` |
| 43, 44, 45 | Moodle form, per-member, team code | `M9-003b`, `M9-003c`, `M9-003d` |
| 46, 47, 48 | Barrier capture, trapped, scoring table | `M2-004`, `M2-005`, `M3-003a`…`c` |
| 49 | Two repos, cross-links | `M7-002f`, `M9-002f` |
| 50 | Minimum repository contents | `G-010`, `M9-004` |
| 51 | Reporting address | `M7-005d` |
| 52 | One scoring game per opponent | `M9-001b`, `M7-007b` |
| 53 | Per-game commit hash | `M4-006a`, `M7-002g` |
| 54 | Total tokens reported | `M4-006b`, `M7-002g` |
| 55 | Self-assessment on code quality only | `M9-009` |

---

## Appendix — submission-guidelines coverage map

The book's Table 4 names the course submission guidelines as a graded criterion, so each
section needs an owning task exactly as the Appendix E rules do.

| Guideline | Subject | Owning tasks |
|---|---|---|
| §2.1 | Comprehensive `README.md` | `M9-002` |
| §2.2 | `docs/PRD.md`, `PLAN.md`, `TODO.md` | `G-010` |
| §2.3 | One PRD per algorithm/mechanism | `G-010` |
| §2.4 | Recommended project structure | `M1-001` |
| §3.1 | Modular structure | `M1-001` |
| §3.2 | 150-line file cap | `G-004` |
| §3.3 | Docstrings and why-comments | `G-002` |
| §4.1 | SDK is the sole entry point | `M1-001` |
| §4.2 | OOP, no duplication | `G-002` |
| §5.1 | Centralized API gatekeeper | `M7-003a` |
| §5.2 | Rate limits from configuration | `M7-003d` |
| §5.3 | Queue management for overflow | `M7-003c`, `M5-004f` |
| §6.1 | TDD red/green/refactor | `G-003` |
| §6.2 | 85% coverage floor | `G-003` |
| §6.3 | Edge cases and error handling | `M8-004a` |
| §7.1 | Zero Ruff violations | `G-002` |
| §7.2 | No hardcoded values | `M7-003d`, `M2-001c` |
| §7.3 | Configuration architecture | `M1-014` |
| §7.4 | Secrets management, `.env-example` | `G-005`, `M7-005b` |
| §8.1 | Version tracking from 1.00 | `M1-001` |
| §8.2 | Branches, PRs, tags | `M9-005` |
| §8.3 | Prompt engineering log | `G-008` |
| §8.4 | `uv` mandatory, no pip | `G-001` |
| §9.1 | Parameter research / sensitivity | `M9-006`, `M9-006a`…`c` |
| §9.2 | Results-analysis notebook | `M9-007`, `M9-007a`, `M9-007c` |
| §9.3 | Visual presentation of results | `M9-007b` |
| §10.1 | Usability criteria, Nielsen heuristics | `M8-004c` |
| §10.2 | Interface documentation and screenshots | `M8-002e`, `M9-002e` |
| §11.1 | Token cost analysis | `M7-002g` |
| §11.2 | Budget management | `M7-003b` |
| §12.1 | Extension points | `M9-008b` |
| §13.1 | ISO/IEC 25010 characteristics | `M9-008a` |
| §14 | Package organization | `M1-001` |
| §15 | Parallel processing, thread safety | `M9-008c` |
| §16 | Building-block design | `M1-001` |

---

## Appendix — book seven-stage roadmap coverage

Book chapter 10 prescribes building in order, each stage running end-to-end before the
next. Stage 6 substance was implemented before stage 2 existed; `M5-002e` closes that gap.

| Stage | Subject | Owning tasks | State |
|---|---|---|---|
| 1 | Base logic: grid, movement, barriers, capture | `M2-001`…`M2-006` | complete |
| 2 | Basic MCP infrastructure over localhost | `M5-002`, `M5-002e` | **open — not started** |
| 3 | Blind strategy module | `EXC-001`, `M3-004` | complete |
| 4 | Natural language and scent | `M6-001`…`M6-005` | open |
| 5 | Cloud exposure and tunnelling | `M5-005`, `M5-005c` | open |
| 6 | Security and cryptography | `M4-001`…`M4-006` | substance built, gate pending |
| 7 | Reporting and visualization shell | `M7-005`, `M8-001`, `M8-002` | open |

---

## Appendix — PRD to task map

| PRD | Owning tasks |
|---|---|
| `PRD_p2p_mcp.md` | `M5-001`…`M5-006` |
| `PRD_commit_reveal.md` | `M4-001`…`M4-006` |
| `PRD_scent_belief.md` | `M6-001`…`M6-003`, `M6-005` |
| `PRD_strategy.md` | `EXC-001`, `M3-004`, `M6-004` |
| `PRD_gatekeeper_reporting.md` | `M7-003`, `M7-005`, `M7-006` |
| `PRD_gui.md` | `M8-001` |
| `PRD_replay.md` | `M8-002` |

---

## Appendix — open unknowns and the tasks they block

A task whose authority is an open unknown must not be implemented as binding. Ruling on
these is coordinator work, not engineering work.

| Unknown | Question | Blocks |
|---|---|---|
| ~~`U-021`~~ | **CLOSED 2026-07-29.** Within-series role schedule: sub-games 1/3/5 natural, 2/4/6 swapped, Thief first. Coordinator-relayed lecturer answer; `C-012` updated to match on 2026-07-31 | no longer blocking |
| ~~`U-022`~~ | ~~Whether surviving exactly `[Survival Threshold]` turns is a Thief win~~ — **CLOSED 2026-07-31**: chapter 3 table 2 defines survival as surviving "the limit of valid moves" and table 15 equates limit and threshold, so the horizon is inclusive | `M3-005`, `M3-005b`, `M7-001c` |
| `U-013` | Config schema shape | `M1-014`, `M7-002b` |
| `U-006` | Port assignment | `M5-002a` |
| `U-009` | Gmail workflow and account setup | `M7-005`, `M7-006` |
| `U-015` | Simulator reuse licence boundary | `M4-002c` `[ADR-0008]` |
| `U-019` | Artifact schemas and the `game_uid` protocol | `M7-002`, `M7-002e` |
| `U-nnn` (`M3-005`) | Whether surviving exactly `survival_threshold` turns is a Thief win | `M3-005a`…`c`, `M7-001c` |
| M1 Stage C | `CONFORMANCE_PROFILE: ACCEPTED` then `M2_GAMEPLAY: GO` never recorded, so the contract checker stays fail-closed | all of `M4-001`…`M4-007` |

---

## Appendix — critical path and external dependencies

Ordering constraints that no amount of parallel work removes.

| # | Item | Depends on | Note |
|---|---|---|---|
| 1 | M1 Stage-C acceptance | coordinator | Not engineering work; it currently gates all of M4 formally |
| 2 | `M5-002` FastMCP server and client | `M4` substance (built) | No transport exists in this repo at all today |
| 3 | `M5-002e` localhost end-to-end | item 2 | Closes the book stage-2 gate that was never opened |
| 4 | `M5-005c` tunnel rehearsal | item 3 | First test against real latency and NAT |
| 5 | `M8-003c` warm-up vs a classmate | item 4 | **External dependency: another team's schedule** |
| 6 | `M9-001a` counted league games | item 5, `M7-005` | **External dependency**; a game without a sent report scores nothing |
| 7 | `M9-005` submission tag | all of the above | Cannot precede the league evidence it must contain |

Items 5 and 6 are the longest lead time in the project because they depend on other
groups being ready at the same time. Everything else is internal and can be parallelised;
these cannot. Start opponent scheduling as soon as item 4 passes, not when item 6 begins.

---

## Appendix — glossary

Terms used throughout this ledger, for anyone joining mid-project.

| Term | Meaning |
|---|---|
| Wire | The exact bytes exchanged between peers. Two agents must agree byte-for-byte or every hash comparison fails. Specified in `SIM_WIRE_PROTOCOL.md` |
| Envelope-free | The current wire shape: the tool argument *is* the message dict. The retired Option-B design wrapped messages in an envelope; it lives in `archive/pre-sim-realign/` |
| Commit-reveal | Send a hash of the move first, reveal the move after, disclose the nonce only at the final audit. Any mismatch is a technical loss |
| Nonce | A fresh random value per commitment. Prevents identical moves producing identical hashes and defeats dictionary attacks |
| Canonical JSON | A fixed serialization so both peers hash byte-identical input. Here `canonical_json` with `ensure_ascii=False` |
| Step-0 | The pre-game sealed declaration of hardware, model, group, game, token budget, and the exact running Git commit |
| Local truth | Each peer knows only its own position, its known barriers, and its observations. Representing the opponent's true position is a rule violation, not a shortcut |
| Technical loss | A crash, timeout, or proven forgery. Scores zero regardless of the position on the board |
| Gate | An automated check that must pass before a commit. Listed under Continuous gates above |
| Fail-closed | `check_shared_contracts.py` deliberately exits 1 until Stage-C acceptance is recorded. Never edit it to pass |
| `THIEF-002` | This repository must never read, clone, or inspect the companion Cop repository. The pinned simulator is the sanctioned reference instead |
| `U-nnn` | An open unknown. Blocks any task that would otherwise have to guess it |
| Coordinator | The repository owner, who makes every acceptance decision. Flag choices; never self-issue a milestone `DONE` |

The archived 635-task document remains historical coverage under
`archive/pre-audit/documentation/TODO.md`; it is not the active plan.
