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
| M1 | Stage A profile, Stage B vectors and stub, Stage C coordinator acceptance | Stage A satisfied (`SIM_WIRE_PROTOCOL.md`); **`CONFORMANCE_PROFILE: ACCEPTED` recorded 2026-07-31** (`STAGE_C_ACCEPTANCE.md`, narrow scope); Stage B interop evidence **absent** (`M1-015..017`); `M2_GAMEPLAY: GO` deliberately withheld; checker fail-closed by design |
| M2 | Complete hardened domain suite: movement, barriers, capture | closed |
| EXC-001 | Deterministic baseline policy on public domain APIs | closed |
| M3 | Immutable local state, scoring, and baseline integration | closed except `M3-005` |
| M4 | Independent vectors, tamper tests, and commit-reveal round trip | **all M4-001…M4-017 tasks DONE 2026-08-01** (profile ACCEPTED 2026-07-31 authorized completion; the 2026-08-01 gaps — canonical vectors, Step-0 attestation, adversarial vectors, constant-time compare, transport-import guard — are now closed and tested). Milestone closure is the coordinator's verdict to record |
| M5 | The Thief runs as server and client and completes a resilient game | **in progress** — transport is built: both FastMCP adapters, a real two-process HTTP round trip (`M5-002`/`M5-002e`), the turn loop and sub-game (`M5-007`), the gateway (`M5-001`), the full reliability set (`M5-004`, `M5-008`, `M5-009`, `M5-010`, `M5-016`), the autonomous mailbox-driven play loop with hosting and readiness (`M5-019`/`M5-019e`), autonomous negotiation sequencing (`M5-019f`), the adversarial-peer proof (`M5-011`), the SDK transport guard (`M5-018`), the own-config-directory (`M5-006`), the architecture docs (`M5-013`), and the same-terminal-outcome proof (`M5-017`) are DONE. Remaining, all **externally or coordinator-blocked, not skippable engineering**: the tunnel rehearsal (`M5-005`, real ngrok/two machines + M8 screenshot evidence) and the Step-0/`config_sha256` wire question (`M5-014f`, `U-024`, coordinator). The scent-lock (`M5-015`) is now DONE via `M6-005` |
| M6 | Legal deterministic behaviour under observation and fallback tests | **all M6-001…M6-028 tasks DONE 2026-08-05** — scent physics + wire, involuntary emission, full belief (Bayes + hints + trust), belief-driven evasion, verbal hints (gen/consume, zero-token default), the scent-model lock + runtime assertion, and every proof (observation stress, privacy, benchmark, strategy-quality vs blind/random, edge cases, determinism regression). Milestone closure is the coordinator's verdict to record |
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
| M1-013 | Author the Thief-owned wire conformance profile with labelled authority per item | DONE | Stage A re-authored 2026-08-06 against the **live** artifacts. The previous checkboxes were ticked against `WIRE_CONFORMANCE_PROFILE.md`, `protocol/canonical.py`, `commitment.py` and `negotiation.py` — all archived or deleted by the simulator realign, so the section certified files that no longer existed. `SIM_WIRE_PROTOCOL.md` now carries an authority table covering every item, and the checklist cites what is actually in the tree |
| M1-013a | Label every profile item book-confirmed, simulator-derived, or `UNKNOWN` | DONE | Every item labelled **book-mandatory** (a numbered Appendix E rule with a sanction) / **book-confirmed** (the book states it, no sanction) / **book-minimum** (an Appendix F floor that may be raised) / **simulator-derived** / **Option-B** / **project choice**, each with its citation. Enforced by `test_profile_authority.py`, not promised in prose. **The deviation is labelled as a deviation**: the book's `:1107` puts the nonce *inside* the hash, we put it outside behind a bar to match the reference, and `test_reference_vector.py` reproduces a real match digest the book's literal formula does not. Rule 17 still holds — it mandates the *mechanism*, and only the mechanism carries a sanction. **The distinction earned its keep during the batch**: canonical JSON was labelled `book-mandatory` on a notebook's say-so; `inst/` showed the book fixes it in a **code listing** (`:1212`), not a ruled sanction, so the label became `book-confirmed` |
| M1-014 | Define canonicalization with reproducible vectors including escaping and separated hash domains | DONE | **Already satisfied; row was stale.** `test_canonical_vectors.py` covers every listed category and its docstring already cited `M1-014a/b/c`. Verified before the stub was built, since a stub that reproduces our canonicalization needs these vectors to reproduce *against* |
| M1-014a | Cover nested objects, arrays, and numeric forms | DONE | `test_object_keys_sort_but_array_order_and_number_forms_hold` — key ordering and number formatting pinned |
| M1-014b | Cover quotes, backslashes, and control characters | DONE | `test_escapes_quotes_backslashes_and_control_characters` — escape handling byte-exact |
| M1-014c | Cover non-ASCII and non-BMP codepoints | DONE | `test_non_ascii_and_non_bmp_serialize_raw_not_escaped` plus an end-to-end non-BMP commit; `ensure_ascii=False` asserted |
| M1-014d | Prove the hash domains cannot collide | DONE | `test_commitment_and_config_hash_domains_do_not_collide` |
| M1-015 | Build a neutral stub opponent sharing no source file with any peer repository | DONE | `tests/conformance/neutral_peer.py` imports **nothing** from `p2p_thief_agent` — stdlib only — and re-derives canonicalization and the commit construction from `SIM_WIRE_PROTOCOL.md` rather than calling ours. Verified by injection, not assertion: changing the commit separator in `protocol/crypto.py` from `|` to `:` fails four conformance tests and nothing else in the suite. Reproduces our digest on a float (`31.8`) and a non-ASCII payload (`café`), the two cross-language hazards a Python-only test cannot surface |
| M1-015a | Assert exact tool and argument names against the stub | DONE | `test_conformance_wire.py` discovers tools **over the wire** with a plain MCP client, the way a stranger would, and asserts all four names and argument names. **Proven by injection**: renaming the stub's `submit_audit` to `exchange_audit` fails three tests including a real `TransportError`, and passes again on revert |
| M1-016 | Prove bidirectional conformance and two participant identities against the stub | DONE | Both directions pass with no profile file edited. `test_conformance.py` proves the **rules** agree; `test_conformance_wire.py` drives the production `FastMCPClient` against the stub behind a real FastMCP server so the **call shapes** agree too — tool names and argument names discovered over the wire by a plain MCP client, the way a stranger would, not read off our own constants. Two participant identities leave `config_sha256` unchanged, since identity is unsigned and role-free |
| M1-017 | Prove fail-closed negative vectors before gameplay | DONE | All seven categories reject. Four map to numbered rules verified in `inst/` — participant/config → 11, hash → 19, private leakage → 2, replay → 29 — and the file says plainly that **version** refuses only through rule 11 (it is a signed term) and that **ordering has no rule at all**, the reference not gating ingestion on step sequence. Children `a` (stale, `test_appendix_f.py`), `b` and `c` (built 2026-08-06) now all closed, which is what this row needed before it could honestly close |
| M1-017a | Reject altered fixed and below-minimum values | DONE | **Already satisfied; row was stale.** `test_appendix_f.py` proves a `FIXED` value cannot change and a `MINIMUM` cannot be weakened, and that raising a `MINIMUM` is legal — rule 12 is "upload minimum values… and never lower", so raising is permitted and refusing it would be our bug, not a defence |
| M1-017b | Reject duplicate JSON keys and unsupported versions | DONE | `protocol/config_integrity.py` + `test_config_shape.py`. `loads_no_duplicates` refuses a repeated key via `object_pairs_hook`, the only point where the duplicate still exists — `json.loads` resolves and forgets it silently, so no check on the parsed dict could ever find it. Rule 11 is the citation: a document with a repeated key is not bit-for-bit reproducible, and a signature over the raw bytes would verify a different object than the one parsed. Versions: `check_config_schema_version` refuses an unimplemented one. **Caught while writing it** — the artifact schema (`1.1`) and the match config (`1.2`) are separate version spaces, so a single global set would have refused our own declaration; the supported set is a parameter. **Use site is M7**: nothing reads a JSON config or artifact back yet, so the guard is proven and SDK-reachable but not yet on a live path — `M7-14`/`M7-23` are where it gets called |
| M1-017c | Reject any private field appearing in shared config | DONE | `check_no_private_fields` + `test_config_privacy.py`, one vector per class. The classes are the book's, not invented: `:2901` assigns "network port, choice of strategy models, language mode, LLM settings, email, and group identity" to the **private** `config/game.toml`, and `:3001` says that file is "not subject to negotiation". A private key in the negotiated object either leaks how we play — the strategy selection is the graded contribution — or drags an unnegotiable local value into a document both sides must hold identically. Refusal names every offending key, since rule 11's purpose is convergence on one document |
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
| M3-005b | Add a boundary test pinning the chosen reading | DONE | `test_scoring.py::test_survival_at_threshold` asserts 34/35/36 (threshold-1/threshold/threshold+1); `test_sub_game.py::test_surviving_the_threshold_wins_inclusively` pins the same horizon in the live loop |
| M3-005c | Disclose the choice in the academic report | PENDING | Book p. 5 contradiction clause |
| M3-006 | Expose state, scoring, and policy through the SDK | DONE | Adapters never import `state` internals `[G§4.1]` |
| M3-007 | Prove the baseline policy is deterministic | DONE | Identical inputs yield an identical action every run |
| M3-007a | Fix the tie-break order explicitly | DONE | No reliance on set or dict iteration order |
| M3-007b | Prefer cells with greater onward reach | DONE | Mobility and dead-end avoidance are explicit metrics |
| M3-008 | Prove the local state never holds Cop-private truth | DONE | `test_local_state.py::test_local_state_holds_no_cop_private_truth_by_field_whitelist` pins the exact field set of `ThiefLocalState` and `ThiefSnapshot`, so a later Cop-truth field breaks the suite rather than leaking silently `[AE-8]` |
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

**2026-08-01 status correction — the profile is accepted, M4 is not complete.**
Two findings supersede the "gated on M1 Stage C" framing above. First, the gate is no
longer pending: `CONFORMANCE_PROFILE: ACCEPTED` was recorded 2026-07-31
(`STAGE_C_ACCEPTANCE.md`), whose stated effect is "M4 may be completed and M5 may
begin", so these rows are **authorized to close** — they were never blocked on an
unrecorded gate, the trackers were simply stale. Second, a row-by-row verification the
same day found M4 was **not actually built out**, contradicting the handoff's "M0–M4
complete". It has since been completed in ID order and **all M4-001…M4-017 rows are now
DONE** (2026-08-01): canonicalization vectors (`test_canonical_vectors.py`), Step-0
attestation with git-commit + token-budget binding and the pre-move ordering guard
(`test_attestation.py`, `test_sealing.py`), the SDK protocol surface (`M4-008`), the five
adversarial tampering classes (`test_audit_vectors.py`), `verify` now using
`hmac.compare_digest` (`M4-012`), the dictionary-attack defence (`M4-010a`), LF/non-ASCII
byte-stability (`M4-011`), and the transport-free protocol guard (`test_protocol_boundary.py`,
`M4-013`). Formal M4 milestone closure remains the coordinator's verdict, and
`M2_GAMEPLAY: GO` stays deliberately withheld until a first live interop run exists.

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M4-001 | Implement the envelope-free simulator-conformant message models | DONE | `protocol/wire.py` (100% branch); `test_wire.py` covers schema/version/identity failures. Envelope-free — the tool argument *is* the message dict |
| M4-001a | Model `TurnMessage`, `ControlMessage`, and `AuditPayload` | DONE | `protocol/wire.py`; matches `SIM_WIRE_PROTOCOL.md`; `test_wire.py` |
| M4-001b | Reject unknown, missing, and mistyped fields | DONE | `test_wire.py` negative vectors per message type |
| M4-002 | Implement exact canonical bytes and shared test vectors | DONE | `test_canonical_vectors.py` (2026-08-01) + `test_crypto.py` + `test_reference_vector.py`; all three sub-tasks DONE |
| M4-002a | Pin the canonicalization form | DONE | `test_canonical_vectors.py` pins exact bytes for key-ordering, preserved array order, float rendering (`6.0`/`31.8`), quote/backslash/control escaping, and non-BMP raw UTF-8 under `ensure_ascii=False` — closing the gap `STAGE_C_ACCEPTANCE.md` flagged |
| M4-002b | Separate the hash domains | DONE | `test_canonical_vectors.py::test_commitment_and_config_hash_domains_do_not_collide` — the nonce-bound commitment can never equal a bare `canonical_sha256` of the same payload |
| M4-002c | Reproduce the pinned simulator's commitment bytes exactly | DONE | `test_reference_vector.py` reproduces a commit hash emitted by the reference simulator itself, by reimplementation only `[ADR-0008]` |
| M4-003 | Implement explicit protocol states and illegal-transition rejection | DONE | `orchestration/phases.py` transition table; `test_phases.py` asserts every undeclared transition raises (also `M5-007a`) |
| M4-004 | Implement SHA-256 commit, acknowledgement, reveal, and nonce secrecy | DONE | `crypto.seal`/`verify` + phase ordering; `test_crypto.py`, `test_sub_game_audit.py` |
| M4-004a | Generate nonces with `secrets`, never `random` | DONE | `new_nonce` = `secrets.token_hex(16)`, fresh per commit; `test_crypto.py` `[book §8]` |
| M4-004b | Keep the nonce hidden until the final audit | DONE | The public `TurnMessage` carries commit/hint/smell_grid, never the nonce; the nonce lives in the private ledger and is revealed only in the audit records `[AE-18]` |
| M4-004c | Enforce commit-before-reveal ordering | DONE | The phase machine requires `AWAITING_REVEAL` before `VERIFYING`; an out-of-order transition raises `PhaseError`; `test_phases.py` |
| M4-005 | Implement audit mismatch and technical-loss outcomes | DONE | `audit_records` + `state/scoring`; `test_sub_game_audit.py` |
| M4-005a | Recompute every commitment at audit and compare | DONE | `audit_records` recomputes every commitment; a mismatch is a technical loss, no appeal; `test_sub_game_audit.py` `[AE-19]` |
| M4-006 | Implement Step-0 host, code, and token attestation | DONE | All three sub-tasks DONE 2026-08-01. `sealed_spec_record` binds spec/model/code_version/group/sub-game (as the reference sim) **plus** `github_commit` and `token_budget`; `protocol/attestation.require_pregame_attestation` enforces the pre-move ordering. `test_sealing.py`, `test_attestation.py` |
| M4-006a | Bind the exact running Git commit into the sealed record | DONE | `sealed_spec_record(github_commit=…)` seals it into the step-0 commitment; `shared/git_info.running_git_commit` resolves the running HEAD (injected runner, fail-closed on a non-40-hex SHA). The same value later populates `github_commit` `[AE-53]` |
| M4-006b | Seal the agreed LLM token budget | DONE | `sealed_spec_record(token_budget=…)` seals the agreed budget; refuses a non-negative-int budget `[AE-54]` |
| M4-006c | Prove Step-0 completes before the first move | DONE | `require_pregame_attestation` raises `AttestationError` naming any step ≥ 1 sealed before the step-0 `system_spec` record; `test_attestation.py` is the ordering test. Live wiring into the running sub-game (seal the spec at game start, then guard) lands with the Step-0 runtime hook in M5 |
| M4-007 | Retitle the M4 rows to match the envelope-free wire | DONE | `M4-001` retitled and the section note corrected on 2026-07-31; neither now describes the retired Option-B envelope design |
| M4-008 | Expose the protocol layer through the SDK | DONE | `p2p_thief_agent.sdk` re-exports `commit_of`, `seal`, `verify`, `audit_records`, `Handshake` (and the sealing/canonical helpers); `test_sdk.py::test_sdk_reaches_commit_seal_verify_audit_and_handshake` `[G§4.1]` |
| M4-009 | Cover commit-reveal with adversarial vectors | DONE | `test_audit_vectors.py`; all five tampering classes below `[AE-19]` |
| M4-009a | Detect a mutated move at audit | DONE | `test_audit_vectors.py::test_a_mutated_move_is_detected` — recomputed hash diverges |
| M4-009b | Detect a mutated intent flag | DONE | `test_a_mutated_intent_flag_is_detected` — the bluff verdict is inside the seal |
| M4-009c | Detect a mutated or substituted nonce | DONE | `test_a_substituted_nonce_is_detected` |
| M4-009d | Detect a single-byte mutation anywhere in the record | DONE | `test_a_single_byte_mutation_anywhere_is_detected` (one byte in `hint`) |
| M4-009e | Detect a reordered step sequence | DONE | `test_a_renumbered_step_index_is_detected` + `test_audit_reports_the_failed_step_whatever_order_records_arrive_in`: the step is bound in the payload, so order is irrelevant |
| M4-010 | Prove nonce generation quality | DONE | `test_crypto.py`: `new_nonce` is fresh 32-hex CSPRNG output; see `M4-010a` |
| M4-010a | Prove two identical moves produce different commitments | DONE | `test_crypto.py::test_two_identical_moves_produce_different_commitments` — the dictionary-attack defence `[AE-18]` |
| M4-011 | Prove canonicalization is byte-stable across platforms | DONE | `M4-011a` (LF) + `M4-011b` (non-ASCII) below |
| M4-011a | Prove CRLF cannot enter a controlled file | DONE | `.gitattributes` pins `eol=lf` globally and per type; `test_protocol_boundary.py::test_gitattributes_pins_lf_on_controlled_files` |
| M4-011b | Prove non-ASCII content hashes identically | DONE | `test_canonical_vectors.py::test_non_ascii_and_non_bmp_serialize_raw_not_escaped` pins `ensure_ascii=False` |
| M4-012 | Compare digests in constant time | DONE | `crypto.verify` now uses `hmac.compare_digest`, never `==`; `test_crypto.py::test_verify_rejects_a_near_miss_commitment` `[book §8]` |
| M4-013 | Prove the protocol layer imports no transport | DONE | `test_protocol_boundary.py::test_protocol_layer_imports_no_transport` walks `protocol/` and fails on any `fastmcp`/`adapters`/`peer`/socket/http import |
| M4-014 | Document the protocol layer | DONE | `PRD_commit_reveal.md` and `SIM_WIRE_PROTOCOL.md` describe the built construction (commit/canonical/handshake/attestation) |
| M4-015 | Implement the signed-terms handshake | DONE | `protocol/handshake.py` + `agreement.py`: role-free identity, `config_sha256`, required-terms; `test_handshake.py`, `test_agreement.py` |
| M4-015a | Reject a handshake missing a required term | DONE | `missing_required_terms` covers every mandatory field; `test_handshake.py` |
| M4-015b | Reject a handshake whose config hash differs | DONE | `accept_offer` compares terms and refuses a mismatch by name (stronger than a bare hash compare); `test_agreement.py` `[AE-11]` |
| M4-016 | Keep the committed payload field set flexible | DONE | `verify` re-hashes the revealed payload, so the field set is not an interop constraint; `test_crypto.py::test_verify_accepts_any_payload_roster` |
| M4-017 | Maintain the archived Option-B layer as history only | DONE | No `src/` or `tests/` module imports `archive/` (verified 2026-08-01); the protocol boundary guard (`test_protocol_boundary.py`) keeps the live layer clean |

---

## M5 — FastMCP runtime and resilience

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M5-001 | Route runtime coordination through one Thief gateway | DONE | `orchestration/gateway.py` — `Gateway` holds one port of each subsystem and wires them (`on_transition` fans a phase out to log + watchdog; `play_sub_game` delegates to the turn loop). `test_gateway.py`, `test_orchestrator_boundary.py` `[AE-3]` |
| M5-001a | Define the five subsystem ports behind the gateway | DONE | `orchestration/ports.py`: `DecisionModule`, `LogPort`, `DeadlineTracker`, `WatchdogPort` Protocols + `PeerTransport` reused as the MCP-connector port `[AE-3]` |
| M5-001b | Forbid subsystem-to-subsystem imports by test | DONE | `test_orchestrator_boundary.py` walks `src/` and fails on any import from one of the five subsystems to another. Fixing the one violation (watchdog→deadlines) drove extracting the shared limit reader into `services/limits.py` |
| M5-001c | Keep decision logic out of the gateway | DONE | The gateway computes no move — `play_sub_game` delegates to the Decision Module port; `test_play_sub_game_delegates_the_move_to_the_decision_module` proves the module, not the gateway, decides `[book §9]` |
| M5-002 | Run the Thief as both FastMCP server and client | DONE | Server, client, an in-memory round trip, **and** a separate-process round trip over HTTP all pass (`M5-002e`). Live-match concerns — negotiation, deadlines, the turn loop — belong to `M5-003`/`M5-004`/`M5-007` |
| M5-002a | Expose the four tools on a local FastMCP server | DONE | `adapters.build_server` exposes `negotiate`, `receive_turn`, `submit_audit`, `receive_control`, each taking one argument with no envelope. A test asserts `receive_move` — the withdrawn Option-B name — is **not** reachable. See `SIM_WIRE_PROTOCOL.md` |
| M5-002b | Confine every FastMCP import to an adapters layer | DONE | A guard test walks every module under `src/` and fails on any non-`adapters` importer of fastmcp |
| M5-002c | Implement the outbound client against the opponent URL | DONE | `adapters.FastMCPClient` implements `peer.PeerTransport`; argument keywords come from `peer.TOOL_ARGUMENTS`, the single place they are written, so inbound and outbound cannot drift apart |
| M5-002d | Decide and document the tool acknowledgement semantics | DONE | **Decision:** tools never validate and never raise; `drain` validates afterwards and a failure there is a recorded game outcome. This diverges from the reference, which validates structurally inside the tool and raises. The divergence is kept because a *tampered audit is structurally well-formed* yet must be scored as a technical loss (`AE-19`); a peer that raises invites the opponent to retry a decided loss as a transport fault. Recorded in `adapters/fastmcp_server.py` and `PRD_p2p_mcp.md` |
| M5-002e | Prove a message round-trips between two processes | DONE | **Book stage-2 milestone closed.** `tests/integration/test_localhost_two_processes.py` spawns a real second interpreter on a free port, sends a turn over HTTP, and reads back the JSONL transcript that process wrote; the validating PID is asserted not to be this one (`AE-1`/`AE-2`). A tampered audit is also driven across the socket and confirmed to arrive and be *scored*, not lost as a transport error `[AE-19]` |
| M5-003 | Enforce accepted idempotency, acknowledgement, and duplicate handling | DONE | Both sub-tasks DONE: `InboundPeer.receive_turn` keys on `(step, sender)` and rejects a replay by name (`M5-003a`/`M5-003b`); `test_negotiation_gate.py` / inbound tests |
| M5-003a | Enforce idempotency keys across retries | DONE | `InboundPeer.receive_turn` keys on `(step, sender)` and refuses a replayed turn, so a retried delivery cannot double-apply. Verified during the 2026-08-01 audit rather than rebuilt |
| M5-003b | Reject replayed message identifiers | DONE | A replay raises `WireError` naming the step and sender — deterministic rejection, never a silent drop. The reference is *inferred* to simply ignore duplicates (its ping-pong state machine leaves them nowhere to land); this repository rejects explicitly, which its own ledger required and which is strictly more informative to an opponent |
| M5-004 | Implement deadlines, watchdog, controlled recovery, and backpressure | DONE | All six sub-tasks `M5-004a`…`f` DONE 2026-08-01. Timeout (`test_deadlines.py`), crash/recovery (`test_watchdog.py`), backpressure (`test_gatekeeper.py`), and mid-turn-disconnect (`test_sub_game.py`) tests all green |
| M5-004a | Attach a timestamp and expiry to every request | DONE | `services/deadlines.Deadline` carries `started` and `expires`, and the boundary itself counts as expired. Book §8.4.1's boxed note is the spec — *"Missing a Deadline is a Failure, Not Patience"* — permitting exactly two outcomes: retry, or declare a technical loss and clear the queue cleanly. Time is **injected**, so a timeout is proven by passing a number rather than sleeping `[book §8.4.1]` |
| M5-004b | Implement bounded retry with backoff | DONE | `services/deadlines.attempt` gives each try its own expiry and stops at `max_retries`, raising `DeadlineError` so the caller can declare a technical loss. **Key names confirmed against the pinned reference 2026-08-01**: `network_and_league.response_timeout_sec` (30), `rate_limiter_gatekeeper.retry_backoff_sec` (5), `.max_retries` (3), `network_and_league.watchdog_timeout_sec` (60) — all in the **shared, signed** match object, so neither peer can give itself a longer rope. A slow attempt that overruns its own expiry is **not** retried. Appendix F table 19 marks the first three `Minimum` and the watchdog `Negotiation` `[AF-t19]` |
| M5-004c | Trip the watchdog at `watchdog_timeout_sec` | DONE | `services/watchdog.py`: `Watchdog.check(now)` returns `ALIVE`/`SHUTDOWN`; trips on `elapsed > timeout` (book §8.4.2 page-83 code, verbatim). Threshold read from the signed match object via `deadlines.WATCHDOG_TIMEOUT`, default 60 s `[AF-t19]`; the book's 180 s code sample is illustrative `[AE-6]`. Time injected — a freeze is proven by passing a number, never sleeping. `test_watchdog.py` |
| M5-004d | Persist state and shut down cleanly on trip | DONE | On trip `Watchdog.check` calls `persist_state()` **then** `controlled_shutdown()` in that order (injected callbacks), returns `SHUTDOWN`, and fires exactly once. Teardown runs even if persistence raises (a controlled shutdown must release its connections); a heartbeat after shutdown is refused fail-closed `[AE-7]`. `test_watchdog.py` |
| M5-004e | Route a mid-turn disconnect to a terminal technical loss | DONE | The reference sim implements **no** watchdog, so this is proven at the loop level instead: `turn_loop` routes silence, a dropped send from `AWAITING_REVEAL`, and a seal failure to `TECHNICAL_LOSS` (`test_turn_loop.py`), and `sub_game` catches every `TurnLoopError` into a terminal `Outcome.TECHNICAL_LOSS` that still reveals its audit — no deadlock out of the awaiting-reveal state (`test_sub_game.py::test_a_mid_turn_disconnect_terminates_and_still_reveals_the_proof`) |
| M5-004f | Enforce queue depth and backpressure | DONE | `services/gatekeeper.py`. Guidelines §5: **"Overflow is queued, not rejected"** — a busy gate returns `False` rather than raising, and `queue_status()` reports depth, capacity, in-flight and totals. The only failure is a genuinely full queue, which raises rather than discarding. Limits are Appendix F table 19 `Minimum` values from the signed match object (30 / 2 / 100). Book ch. 9.3.1 aims the Gatekeeper at **outbound** Gmail/LLM calls; inbound duplicates are `InboundPeer`'s job. **"FIFO" dropped from the title** — the book notebook marked it *inferred*, not stated `[G§5.3]` `[AF-t19]` |
| M5-005 | Validate localhost and public-tunnel paths against identical fixtures | PENDING | Connectivity and failure evidence |
| M5-005a | Keep tunnel credentials out of shared configuration | PENDING | `[AE-39]`; secrets stay private `[G§7.4]` |
| M5-005b | Exchange only the public URL | PENDING | `[AE-10]`; provider choice stays local |
| M5-005c | Rehearse a full game across two machines | PENDING | Book stage-5 milestone: "Agent on a remote computer connects via ngrok and plays a full game against the local agent" (`police_thief_p2p_Summary.md:2458`). Three blockers, one now cleared: the *play loop* is **RESOLVED** by `M5-019`; *launching a peer* is `M5-019e`; *hardware* (two machines, a live tunnel) cannot be unit-tested. **Found 2026-08-02 and confirmed at `police_thief_p2p_Summary.md:2295`:** the mandated **evidence** is "Live GUI (belief map) and Replay App (Verified OK) screenshots", both **M8** deliverables — so this cannot be *evidenced* until M8 exists even with the hardware and CLI in place |
| M5-006 | Run the Thief in its own process under its own config directory | DONE | `[AE-1]` `[AE-2]`: the separate-process test proves the Thief runs and validates in its own interpreter with no shared memory or module state. The **own config directory** half is now closed: the skeleton moved to `config/thief/game.toml.example` (the Thief's own role directory, matching the reference's `config/<role>/`), and `shared.private_config.thief_config_path`/`load_thief_private_config` resolve **only** `config/thief/`, so this peer structurally cannot read a `config/police/` sibling. `test_thief_config_dir.py` pins the role scoping (`a police sibling file is not read`), and `.gitignore` covers `config/*/game.toml` |
| M5-002f | Read the opponent URL from private configuration only | DONE | `shared/private_config.py` reads `[network].opponent_url` from one explicit private TOML path and is the only way in to an opponent address; `assert_no_network_address` guards the way out, refusing a shared object that carries an address either by member **name** or by **value**, since either check alone is easy to slip past. `config/thief/game.toml.example` added (relocated into the Thief's role directory 2026-08-02 by `M5-006`), matching book p. 131 and the reference's own `config/thief/game.toml`. **Confirmed against the pinned wire reference 2026-07-31** before implementing: separate `config/police/` and `config/thief/` directories, address at `[network].opponent_url`, and the shared negotiated JSON never carries a URL, port, host, or any address — local settings must not "leak into the agreement". This closes the private keys `ADR-0004` left `PENDING` `[AE-10]` `[AE-39]` |
| M5-002g | Fail cleanly on an unreachable opponent URL | DONE | `http://127.0.0.1:1/mcp` raises `TransportError`, never a crash |
| M5-002h | Fail cleanly on a malformed opponent response | DONE | A reply that is not a JSON object raises `TransportError` deterministically. The client is **liberal** about the ack shape — `{"ok": true}`, `{"status": "ok"}`, and `{"status": "delivered"}` are all accepted — because the profile never fixed the opponent's shape; only an explicit `ok: false` / failing `status` / non-empty `error` is a `PeerRejectionError` |
| M5-002i | Keep the client stateless between calls | DONE | `__slots__` makes hidden per-turn state impossible rather than merely absent; each call opens and closes its own session |
| M5-002j | Document the client contract in `PRD_p2p_mcp.md` | DONE | Call shapes, the two-way fault mapping, and the acknowledgement decision recorded |
| M5-007 | Implement the turn loop around the transport | DONE | `orchestration/` now holds the declared phase machine, `run_turn`, and `run_sub_game_over_wire`. Order corrected against the reference: **await → compute → apply → seal → send**, not compute-first. **This peer opens** — the book gives the Thief the first move of every cycle, so step 1 does not wait; a Thief that waited would deadlock against a Cop correctly waiting for it. Termination is *not* the Cop's mirror: a `capture_claim` is **checked against local truth, never believed**, because the Thief is the peer that knows where it stood, and an incorrect claim is simply the game continuing. 84 tests across four modules plus four over a real socket |
| M5-007a | Drive the loop from the protocol state machine | DONE | `orchestration/phases.py`: the specification's table transcribed unchanged, refusing every undeclared transition **by name** `[AE-004]` `[AE-005]`. Most of the tests are refusals on purpose — a machine that accepted everything would pass a happy-path test and still deadlock the first time a peer went out of order, so all 28 undeclared pairs are asserted to raise. `TECHNICAL_LOSS` is reachable only where the table allows |
| M5-007b | Make one turn atomic against partial failure | DONE | A turn is sealed **exactly once**; a failed send never re-seals, because a second hash for one step is an audit mismatch and an automatic zero `[AE-019]`. Deciding and sealing were moved into `COMPUTING_MOVE`, the only phase the table permits `TECHNICAL_LOSS` from — they were briefly inside `COMMITTING`, where a seal failure had **no legal exit** and stranded the machine mid-turn. The companion peer carried the same latent defect and was corrected the same day |
| M5-007c | Bound the loop by the negotiated step limit | DONE | `run_sub_game_over_wire` is bounded by `survival_threshold` and validates it, and the horizon is **inclusive** — completing the final step uncaught is a win, not one step short (`U-022`) `[AF-t15]` |
| M5-007d | Emit a structured log line per phase transition | DONE | `run_turn` takes an `on_transition` callback fired on every phase entered, and `PhaseMachine.history` keeps the ordered record. The log manager that consumes them is `M5-008` |
| M5-008 | Implement the log manager subsystem | DONE | `services/log_manager.py` — append-only, structured, sufficient to reconstruct the match; `test_log_manager.py`. All four sub-tasks below |
| M5-008a | Record every sent and received message | DONE | `record_sent`/`record_received` (plus `record_transition`/`record_commitment`); `test_records_sent_and_received_messages_in_order` `[AE-36]` |
| M5-008b | Record commitments and, at audit time, nonces | DONE | `record_commitment` logs the commit; `reveal_nonce` raises before `open_audit()` and only logs the nonce after the final reveal `[AE-18]` |
| M5-008c | Keep the log append-only | DONE | No edit/delete method exists (`test_there_is_no_method_to_edit_or_delete_an_entry`); the file is opened in append mode and `entries` returns a copy |
| M5-008d | Write logs under a per-match path | DONE | The file name carries the `game_uid`; a reopen appends rather than truncating; `test_the_log_path_is_per_match`, `test_the_log_is_written_append_only_and_survives_a_reopen` |
| M5-009 | Implement the deadline tracker subsystem | DONE | `services/deadline_tracker.py`: `RequestTracker` registers each outbound request under a key with a deadline from the agreed limits, and reaps those past expiry; `test_deadline_tracker.py`. Also satisfies the gateway's `DeadlineTracker` port |
| M5-009a | Reap expired requests rather than awaiting them | DONE | `RequestTracker.reap(now)` removes and returns every request past its expiry; `test_expired_requests_are_reaped_and_live_ones_kept` `[book §9]` |
| M5-009b | Clear the queue cleanly on a declared technical loss | DONE | `RequestTracker.clear()` drops every pending request; `test_clear_drops_every_pending_request_on_a_technical_loss` — no orphan survives |
| M5-010 | Handle opponent-side rejection responses | DONE | `PeerRejectionError` vs `TransportError` are disjoint (`adapters.fastmcp_client.signals_refusal`); `orchestration/delivery.deliver` retries only transport faults; a rejection terminates the sub-game (`test_delivery.py`, `test_sub_game.py`) |
| M5-010a | Distinguish rejection from transport failure | DONE | `deliver` uses `retry_on=(TransportError,)`: a transient transport fault is retried to the agreed limit, a `PeerRejectionError` propagates on the first occurrence; `test_delivery.py` |
| M5-010b | Terminate deterministically on an unrecoverable rejection | DONE | A rejection routes through the turn loop to a terminal `Outcome.TECHNICAL_LOSS`; `test_sub_game.py::test_an_opponent_rejection_terminates_the_sub_game` |
| M5-011 | Prove the runtime under adversarial peer behaviour | DONE | `test_adversarial_peer.py` gathers all five hostile classes into one proof exercising the real guard paths; each sub-task below is a named test. Confirmed genuinely open in the 2026-08-02 reconciliation before it was built — a consolidation task, not new runtime code |
| M5-011a | Survive a peer that never responds | DONE | `test_a_peer_that_never_responds_is_a_technical_loss_not_a_hang`: silence routes to a bounded `TECHNICAL_LOSS` (the deadline path); the watchdog freeze path is proven independently in `test_watchdog.py` |
| M5-011b | Survive a peer that responds out of order | DONE | `test_a_peer_that_responds_out_of_order_is_rejected_by_the_state_machine`: an undeclared `WAITING_FOR_OPPONENT -> AWAITING_REVEAL` edge raises `PhaseError` `[AE-5]` |
| M5-011c | Survive a peer that replays an earlier message | DONE | `test_a_replayed_turn_is_rejected_by_the_idempotency_guard`: a duplicate `(step, sender)` raises `WireError` by name and is not re-applied |
| M5-011d | Survive a peer that sends oversized or malformed input | DONE | `test_oversized_or_malformed_input_is_rejected_before_domain_code_runs`: an injected 10 000-char extra field and a fields-missing turn both reject at `TurnMessage.from_dict`, before any domain code |
| M5-011e | Survive a peer that disconnects mid-audit | DONE | `test_a_peer_that_disconnects_mid_audit_still_records_the_outcome`: an undeliverable audit is still built and returned, so the reveal stands and the sub-game does not hang `[AE-19]` |
| M5-012 | Complete the book's stage-2 localhost milestone | DONE | Book p. 105: a message sent by peer A on localhost is received correctly by peer B. **Closed by `M5-002e`** — `tests/integration/test_localhost_two_processes.py` spawns a real second interpreter, sends over HTTP, and reads back the transcript that process wrote. This row duplicated `M5-002e` and was left `PENDING` after it closed; reconciled 2026-08-01 when re-reading the ledger. Its sub-rows `M5-012b`..`M5-012e` are superseded by `M5-014` (negotiate) and `M5-007` (turn, sub-game, audit) |
| M5-012a | Launch two peers on distinct localhost ports | DONE | **Reconciled 2026-08-02.** `tests/integration/test_localhost_two_processes.py` spawns a real second interpreter on a free port and reaps it in a fixture teardown (`M5-002e`). The *separate config directories* half is tracked by `M5-006`, not here `[AE-1]` |
| M5-012b | Exchange one negotiate round trip | SUPERSEDED | **Reconciled 2026-08-02** — superseded by `M5-014`, which built the whole negotiation gate (`accept_offer`, refusal by name, 33 unit + 6 live-handler tests) and is wired into the live `InboundPeer` |
| M5-012c | Exchange one turn round trip | SUPERSEDED | **Reconciled 2026-08-02** — superseded by `M5-007` (`run_turn` through the phase machine) and the live-socket cases in `tests/integration/` |
| M5-012d | Complete one full sub-game over the wire | SUPERSEDED | **Reconciled 2026-08-02** — superseded by `M5-007c` (`run_sub_game_over_wire`, bounded by the inclusive survival horizon) |
| M5-012e | Complete the end-of-game mutual audit over the wire | SUPERSEDED | **Reconciled 2026-08-02** — this peer's half is superseded by `M5-007`. Mutual verification of the *opponent's* audit remains genuinely open and is tracked in `PRD_p2p_mcp.md` "Not yet built", not here |
| M5-012f | Record the run as stage-2 milestone evidence | DONE | **Reconciled 2026-08-02.** The spawned peer appends a JSONL transcript of every call's validation outcome and the test reads it back — observed behaviour, not written code, which is what the book asks for |
| M5-013 | Document the runtime architecture | DONE | `PRD_p2p_mcp.md` §"Runtime architecture and failure matrix" describes the gateway, the five subsystems, and the turn loop; `PLAN.md` carries the layer boundary. Both sub-tasks below |
| M5-013a | Draw the subsystem diagram | DONE | `PRD_p2p_mcp.md` §M5-013a: the gateway plus the five named subsystems (MCP Connector, Decision Module, Log Manager, Deadline Tracker, Watchdog), with an explicit note that no arrow runs subsystem→subsystem — every link goes through the gateway (`M5-001b`) `[G§20.1]` |
| M5-013b | Document every failure path and its outcome | DONE | `PRD_p2p_mcp.md` §M5-013b: a twelve-row matrix, one per fault class (silence, dropped send, rejection, seal failure, out-of-order, replay, malformed, tampered audit, freeze, deadline expiry, queue full, unreachable peer), each with where it is caught and its terminal outcome — the table `M8-005` will exercise |
| M5-014 | Implement negotiation and mismatch refusal | DONE | `protocol/agreement.py` owns the policy — Appendix F floors, participants, and what a refusal must say — while `handshake.py` keeps the signing mechanics. `accept_offer` gates in a deliberate order: structure, signature, required terms, Appendix F, then equality with our own terms. It is **wired into the live handler**: `InboundPeer(my_terms=…)` applies it and refuses by name, and without terms still only shape-checks, which is the state before the shared match object is loaded. 33 unit tests plus 6 live-handler tests `[AE-11]` `[AE-12]` |
| M5-014a | Build and send a match offer | DONE | `Handshake.signed()` returns terms, the public challenge nonce, the signature over those terms, and role-free identity. **Deviation from this row's original wording, deliberate:** the offer does *not* carry a participants list. The reference establishes participants from the two exchanged identities rather than as a message field, and inventing one would put a term in our signature that no classmate signs. `validate_participants` covers the agreed-between list wherever the runtime holds one |
| M5-014b | Compare `config_sha256` byte-for-byte before play | DONE | `accept_offer` compares the terms themselves, which is strictly stronger than comparing the hash because only it can say **which** term differs — and rule 11 wants a refusal the opponent can act on. A test pins that the two never disagree: agreement implies an identical `config_sha256`, and a differing term produces both a different hash and a refusal naming it `[AE-11]` |
| M5-014c | Validate participant identity and ordering | DONE | `validate_participants` requires exactly two distinct non-empty named groups and, when a group id is supplied, that it is one of them. Ordering needs no separate rule: the list lives inside the hashed object, so both peers already hold the same order |
| M5-014d | Refuse below-minimum and altered fixed values | DONE | `check_appendix_f`: `smell_grid_size`, `decay_per_step`, `emit_intensity`, and `num_games` are `FIXED` (exact match); `board_size`, `max_steps`, and `barriers_max` are `MINIMUM` (may move only in the harder direction). `tests/unit/test_appendix_f.py` pins the statuses against `docs/PARAMETERS_BASELINE.md` — tables 13, 15, 16, 18 — so a silently edited constant fails here rather than at a match `[AE-12]` `[AF-§1]` |
| M5-014e | Prove propose and accept directions both pass | DONE | Two `Handshake` peers under different group identities each accept the other's offer against the same terms, with no profile file edited in either direction |
| M5-014f | Enforce the book's mandated Step-0/negotiation content and the `config_sha256` lock `U-024` | PENDING | **Found by the 2026-08-01 book-notebook catch-up.** The book mandates the pre-game exchange carry team identity, members, repository URLs, MCP server URLs, hardware specs, the LLM model, and cryptographic signatures, and that both teams lock the agreed values with a `config_sha256` hash. `Handshake.signed()` emits `terms`/`nonce`/`signature`/`identity` and `identity_block` can carry all seven members, but nothing requires them and no `config_sha256` rides on the wire — `config_sha256(terms)` exists and is compared indirectly through the signature. Whether the hash must be an explicit wire member is a contract question, so it is recorded rather than decided |
| M5-015 | Exchange and verify the scent-model lock at negotiation | DONE | **Reworked 2026-08-05.** Previously closed by `with_scent_lock`, which stamped the hash **into the signed terms** — that was wrong for league play: `differing_terms` compares the union of both key sets, so any opponent not sending `scent_model_hash` was refused, and the pinned simulator sends none (it folds pheromone terms into `config_sha256`). The lock now rides **beside** the signed terms; `negotiate_match` publishes ours via `scent_lock_fields()` and passes `expected_scent_lock` to `accept_offer`, which **tolerates omission and refuses a mismatch**. Rule 23 sanctions a deviation, not a silence. `test_scent_lock.py` `[AE-23]` |
| M5-016 | Implement backpressure signalling | DONE | **Reconciled 2026-08-02 — already satisfied, never recorded.** `services/gatekeeper.py` implements it and `tests/unit/test_gatekeeper.py` names this row's Definition of Done almost verbatim: `test_a_full_queue_refuses_loudly_rather_than_discarding` (signals rather than silently dropping) and `test_exceeding_concurrency_queues_rather_than_rejects` (guidelines §5, "Overflow is queued, not rejected"). `queue_status()` reports depth, capacity, in-flight and totals, covered by `test_queue_status_reports_depth_capacity_and_totals`. Nine tests in total. No new code was written to close this row `[G§5.3]` `[AF-t19]` |
| M5-017 | Prove two peers reach the same terminal outcome | DONE | `test_two_peer_agreement.py`: the result is *derived* from the shared audited transcript, not asserted. A neutral verifier computes the opponent's view **only** from the Thief's revealed audit and agrees on both a capture and a survival. The third case is the audit's teeth — a Thief that denies a correct capture reads `survival` while the opponent, recomputing from the Thief's own sealed `[3,3]`, reads `capture`; the disagreement is a visible conflict scored 0/0, never a silent win `[AE-19]` `[AE-21]`. Result *agreement wiring* (both peers exchanging and converging before a report) is `M7-016` |
| M5-018 | Keep transport concerns out of the SDK | DONE | `test_sdk_boundary.py`: a static walk of `sdk/` fails on any transport import, and a fresh subprocess importing `p2p_thief_agent.sdk` proves no `fastmcp`/`httpx`/`requests` stack reaches `sys.modules`. This is the **SDK** boundary guard guidelines §4.1 makes the single entry point — distinct from `M5-002b`, which guards the transport-neutral core `[G§4.1]` |
| M5-019 | Drive the mailbox: the autonomous over-wire play loop | DONE | **This row did not exist before 2026-08-02** — the Cop named the gap inside its `M5-07c`, and this ledger named it nowhere, so the repo's own most load-bearing missing piece was invisible here. `adapters.build_server` is a passive mailbox and `run_turn` only consumes, so **nothing joined them**: every sub-game test had to hand `receive` a scripted opponent. Built: `orchestration/polling.py` (`poll_for_turn`, `turn_receiver`) and `adapters.take_turn`. `tests/unit/test_autonomous_play.py` plays a whole sub-game whose only turn source is the mailbox. 24 tests across four new files, both new src files at 100% branch |
| M5-019a | Poll the local inbox for the opponent's turn | DONE | Confirmed against the reference 2026-08-02 before implementing: its `PeerRuntime` polls **its own** inboxes via `McpTransport` at `[network].poll_interval_seconds` (0.5 s shipped), and the inbound `receive_turn` tool "does not compute the next turn; it only deposits the message". The book mandates a strict state machine rather than a bare loop (section 8.3) — both hold, because polling is only *how* a queued message is picked up while `PhaseMachine` still decides what may legally follow. `DEFAULT_POLL_INTERVAL` is local, private and never negotiated, so it cannot affect a hash or interoperability |
| M5-019b | Bound the wait so silence decides instead of blocking | DONE | `[AE-006]` verbatim: "Mandatory to implement a deadline-tracking mechanism to prevent deadlocks while waiting for the opponent". `poll_for_turn` stops at the turn timeout and returns `None`, which `run_turn` turns into the declared exit to `TECHNICAL_LOSS`. The boundary itself counts as expired, matching `services/deadlines.py`. A turn **already queued** is taken even at zero budget: the deadline bounds *waiting*, and refusing an arrived message would forfeit a match on a technicality |
| M5-019c | Emit the heartbeat from the loop that actually waits | DONE | Book section 8.4.2 puts the watchdog on "the main game loop", and a peer waiting for an opponent is otherwise doing nothing observable — exactly when a frozen process and a patient one look identical. Every poll iteration pulses `[AE-007]`. Time is injected, so the pulse train is asserted by advancing a number rather than by sleeping |
| M5-019d | Keep a hostile mailbox from starving the loop | DONE | Three behaviours in `take_turn`, each of which would silently break an unattended match: a **rejected** turn is consumed (leaving it queued makes the poller re-reject it forever and starve the real turn behind it); a **second** queued turn is left in place (draining both discards the next step rather than playing it); and the other three mailboxes are drained first (a negotiate/audit/control message parked in front of a turn stalls the game). 7 tests in `test_take_turn.py` |
| M5-019e | Launch a peer as a long-running process — hosting and readiness | DONE | The two mechanical halves of launching, built 2026-08-02 and both testable without a real match. `adapters/serving.py`: `serve_in_background` runs the mailbox on a **daemon** thread (so it can never outlive the game and turn a finished match into a hang) after `ensure_port_free` fails loudly on a stale peer still holding the port; `port_answers` is the readiness probe. `services/readiness.py`: `wait_for_peer` is a **bounded** retry so start order does not matter. 18 tests across `test_serving.py`/`test_readiness.py`. See `ADR-0009` |
| M5-019e-i | Bind `0.0.0.0`, never `127.0.0.1` | DONE | **The one-word bug no local test would ever catch.** Confirmed from three independent sources: the book prints `mcp.run(transport="http", host="0.0.0.0", port=8000)` with the comment "Bind the server so a tunnel can expose it publicly" (`police_thief_p2p_Summary.md:657`); rule 10 is "Use tunnels to expose the local server to the public internet. **Sanction: Inability to compete against opponents**" (`:3326`); `DEV-SPEC.md:382` agrees. The **reference binds `127.0.0.1`** (thief 8801, police 8802) because it runs both peers on one machine — single-machine convenience, and the book outranks the simulator. Loopback would pass every local check and be invisible through the tunnel, failing only at the stage-5 rehearsal where it reads as a network fault. `DEFAULT_BIND_HOST` is pinned by a test `[AE-010]` |
| M5-019e-ii | Tolerate either start order | DONE | Two peers launched by two people cannot start at the same instant; the reference is explicit that "start order doesn't matter". `wait_for_peer` polls until the opponent answers, bounded by `[network].connect_timeout_seconds` (60) with `retry_interval_seconds` (1.0) between tries — both confirmed against the reference 2026-08-02, both **private** so neither can affect a hash. It returns `False` rather than raising: an opponent nobody launched is an operator situation, and raising would blur it with the in-match deadline failures rule 6 governs. Deliberately a separate module from `deadlines`/`watchdog`, because startup is the **one** phase where waiting is correct and that leniency must not leak into the match |
| M5-019f | Sequence negotiation and first move autonomously | DONE | `orchestration/negotiation.py`: `negotiate_match` sends this peer's signed offer, polls the agreements mailbox for the opponent's (bounded — silence before the deadline is a refusal, not a hang, `AE-6`), verifies **both directions** (`accept_offer` names any Appendix F / differing-term refusal; `Handshake.verify_peer` binds the opponent identity and re-confirms the signature covers our terms), and returns the `AgreedMatch`. `run_autonomous_match` chains it into play bounded by the **negotiated** `max_steps`, so the Thief opens step 1 only after both verifications pass — never before, and never on a local default. Transport-neutral (imports no FastMCP); `test_negotiation_sequence.py` covers agree / refuse-by-name / deadline / open-after-agreement, `negotiation.py` at 100% branch. **Deferred, by design:** the mutually-signed Step-0 attestation exchange and the pre-game declaration artifact are `M5-014f` (`U-024`, coordinator) and `M7-002a`; a `serve` CLI entry point that wires hosting + readiness + this sequencer + the sub-game is the remaining thin composition |

---

## M6 — Scent, belief and private strategy

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M6-001 | Implement confirmed multiplicative scent physics | DONE | `perception/scent.py` (100% branch); `test_scent.py`. All four sub-tasks below. **Updated 2026-08-05:** the eight `5×5` cells at squared-distance 5 are unnamed by book Figure 4 (`U-025`) and are now a **negotiated parameter** (`DEFAULT_OUTER_RING_DELTA`, explicitly no book authority) covered by the `M6-005` lock — not a private constant. No source yields a value for them, so a constant could only ever be this peer's guess |
| M6-001a | Emit a 5×5 field centred on the agent | DONE | `emission_field()` returns a 5×5 field with the agent's own cell at the FIXED `0.9`; `test_the_field_is_5x5_centred_on_the_agent_at_0_9` `[AF-t16]` `[PRD-scent]` |
| M6-001b | Apply `τ(t+1) = max(0, (1-ρ)·τ(t) + Δτ)` per full turn | DONE | `settle` (one cell) and `advance_field` (whole field) implement the book §4.3 update at ρ = 0.10; decay **retains** 90% (`C-014`), not removes it. `advance_field` is a single per-turn step, called after both peers act; `test_decay_retains_ninety_percent_not_ten`, `test_advance_field_applies_the_update_cell_by_cell` |
| M6-001c | Pin the radial profile with numeric vectors | DONE | `test_the_radial_profile_matches_book_figure_4` pins the five book-confirmed classes exactly — centre `0.90`, cross `0.62`, diagonal `0.20`, mid-side `0.14`, corner `0.04` (Figure 4, p.44). The unnamed eight are pinned against the `U-025` provisional so a ruling moves test and code together |
| M6-001d | Clip intensities to non-negative | DONE | `settle` is `max(0, …)`: a never-visited cell reads `0.0` and no update goes negative; `test_intensity_is_clipped_non_negative` |
| M6-002 | Consume accepted public scent observations in the accepted order | DONE | `perception/observation.py` (100% branch); `test_observation.py` covers shape, order-independence, the sparse "absent, not zero" rule, deterministic encode order, round-trip, and boundary/rejection. Off-board rejection needs the negotiated grid and is `M6-006b` |
| M6-002a | Populate and parse `smell_grid` as `{"r,c": intensity}` | DONE | `parse_smell_grid` decodes an inbound `{"r,c": intensity}` map to `(row,col)→intensity` (order-independent, rejects malformed key / non-numeric / negative by name); `encode_smell_grid` produces the sparse wire form, omitting silent cells (`M6-006a`) and emitting keys in sorted order — matching `SIM_WIRE_PROTOCOL.md` |
| M6-003 | Maintain a Thief-local belief without objective Cop truth | DONE | `perception/belief.py` (distribution + Bayes + privacy), `perception/hint.py` (hint decoding), `perception/trust.py` (trust factor). Design recorded in `PRD_scent_belief.md` before building. All six sub-tasks below; `test_belief.py`/`test_hint.py`/`test_trust.py`, every module at 100% branch |
| M6-003a | Maintain a board-sized probability matrix | DONE | `uniform_belief(rows, cols)` sizes the distribution to the **negotiated** grid (not the book's 10×10), every cell `1/(rows·cols)`, summing to 1; `test_a_uniform_belief_is_sized_to_the_grid_and_sums_to_one` |
| M6-003b | Apply Bayes with a per-hint trust factor | DONE | `apply_evidence` is the Bayes mechanism; `trust.trust_weighted` tempers a decoded hint's likelihood toward uniform by `(1 − trust)`, so the hint applies through `apply_evidence` at its trust-scaled strength. A hint contradicted by scent has its trust lowered (`M6-003f`), which lowers its weight next time; `test_trust.py` |
| M6-003c | Normalize without dividing by zero | DONE | `normalize` falls back to the max-entropy uniform when the total is zero, so contradictory evidence leaves a valid distribution rather than a division by zero; `test_a_zero_total_falls_back_to_uniform_not_a_division_by_zero`, `test_a_likelihood_that_is_zero_everywhere_resets_to_uniform` |
| M6-003d | Prove the belief never reads objective truth | DONE | `test_the_belief_update_takes_no_objective_cop_truth`: `apply_evidence` accepts only a prior and a public likelihood — no parameter names the Cop's real cell, so objective truth cannot enter by construction, and the result is always a distribution `[AE-8]` `[AE-9]` |
| M6-003e | Decode an inbound hint into a belief-space update | DONE | `hint.decode_hint` maps free text to a likelihood through directional-cue **gradients** (north/south/east/west/center/corner), deterministic pure Python so it can feed the move without the LLM (`AE-25`) and using only common vocabulary, never an agreed `"r,c"` protocol (`AE-27`). An unrecognised/empty/absent hint decodes to uniform — missing evidence is not an error; `test_hint.py` |
| M6-003f | Lower a hint's trust when scent contradicts it | DONE | `trust.update_trust` moves trust by the overlap of the hint's likelihood with the Cop's own scent, measured against the no-correlation baseline: a hint pointing where scent shows nothing drops trust (clipped to `[0,1]`), a corroborated one raises it; `test_a_hint_contradicted_by_scent_loses_trust` `[AE-27]` |
| M6-004 | Add private strategy improvements behind legal validation | DONE | `strategy/belief_policy.py` (movement) + `verbal/hints.py` (hints); `test_belief_policy.py`, `test_movement_llm_free.py`, `test_hints.py`, all modules 100% branch. All sub-tasks below |
| M6-004a | Maximise distance from the believed Cop cell | DONE | `choose_evasive_action` reads the believed Cop cell (`believed_cop_cell`, argmax with a lowest-cell tie-break) and feeds it as the threat to the baseline `choose_action`, which maximises distance from it; `test_the_move_increases_distance_from_the_believed_cop` |
| M6-004e | Keep every emitted action legal under the domain layer | DONE | Reusing `choose_action` means the move is always legal — a belief peaked on the Thief's own cell or a wall still yields a legal action; `test_every_emitted_action_is_legal_even_when_belief_points_at_our_own_cell` |
| M6-004f | Bound per-turn decision time | DONE | The policy is pure Python over the legal actions (≤5) with board-local metrics, no history scan, recursion, or I/O — bounded by construction, proven network/LLM-free by `test_movement_llm_free.py`. The turn-level deadline that bounds *waiting* is `M5-004`/`M5-019b` `[AF-t19]` |
| M6-004g | Keep the policy deterministic and reproducible | DONE | Fixed lexicographic criteria and a fixed tie-break; `test_the_policy_is_deterministic` asserts identical inputs yield an identical action over repeated calls |
| M6-004h | Load strategy tuning from the private TOML only | DONE | The policy is deliberately **weight-free** (lexicographic, not a weighted sum), so no tuning value exists to enter the shared JSON; `test_the_policy_carries_no_tunable_weights_to_leak` pins the signature. Any future tuning loads from the private TOML `[ADR-0004]` |
| M6-004b | Keep the LLM out of movement decisions | DONE | `test_movement_llm_free.py` walks `strategy/` and `perception/` and fails on any LLM-provider or network import, so the move can never depend on a model's output `[AE-25]` `[ADR-0007]` |
| M6-004c | Enforce natural-language-only hints within the word limit | DONE | `verbal/hints.validate_hint`: a hint must be non-empty natural language, within the agreed `hint_max_words` (default 15 `[AF-t14]`), and must not encode coordinates — `test_a_hint_encoding_coordinates_is_rejected` proves `"3,4"`/`"(2, 5)"`/`"r3c4"` are refused `[AE-26]` `[AE-27]` |
| M6-004d | Ship a zero-token template provider as default | DONE | `verbal/hints.template_hint` emits a validated natural-language hint from a fixed template set — no model, no account, no network — so a whole series is playable at zero tokens; deterministic in the step, and it validates at generation time (`M6-008c`). `test_the_template_provider_yields_a_legal_hint_at_zero_tokens` `[AF-t21]` |
| M6-005 | Lock and exchange the scent-model hash before the first move | DONE | `perception/scent_lock.py`: the full model (formula, FIXED constants, field size, and the complete 25-cell profile including the negotiated `U-025` ring) is canonicalised and SHA-256 locked. **Reworked 2026-08-05** — the lock left the signed terms and the ring became a parameter, so the record now describes an *agreed* model rather than this peer's private constants. The digest `416a57e1…` is pinned in `test_scent_lock.py` and is reproduced exactly by the independently written Cop peer, which is the only real evidence that a lock is worth anything `[AE-23]` |
| M6-005a | Canonicalise the scent model to hashable bytes | DONE | `scent_model_record` is one canonical dict — formula, `center_intensity`/`decay_per_step`/`field_size`, and the emission profile by squared distance — hashed with the same `canonical_sha256` as config and commitments; `test_the_record_carries_the_formula_constants_field_and_profile`, `test_any_change_to_the_model_changes_the_lock` |
| M6-005b | Exchange and compare the lock at negotiation | DONE | **Reworked 2026-08-05.** `scent_lock_fields()` publishes the hash and the ring value it covers alongside the signed offer; `accept_offer(expected_scent_lock=…)` compares them. A differing model is refused **by name**; a peer publishing **no** lock is still played. Proven end to end through `negotiate_match`, including that our own lock actually goes out on the offer we send `[AE-23]` |
| M6-005c | Record the arithmetic correction in the report | DONE | The p.43 "reduced by 90%" and p.46 saturation errors are disclosed under the book p.5 clause in `SPECIFICATION_CONFLICTS.md` (`C-014`/`C-015`) and `PRD_scent_belief.md`; the model retains 90% at ρ = 0.10 and the lock encodes that. Embedding the disclosure in the final academic README is `M9-011c`/`M3-005c` |
| M6-006 | Serialize and parse the scent observation on the wire | DONE | `perception/observation.py` (100% branch); `test_observation.py`. The field survives the round trip without precision drift — `test_the_wire_form_is_idempotent_under_re_encoding`. All three sub-tasks below |
| M6-006a | Encode the emitted field into `smell_grid` | DONE | `encode_smell_grid` emits the sparse `{"r,c": intensity}` map — silent/zero/below-precision cells omitted, keys in sorted order; `test_encoding_omits_silent_cells_rather_than_zero_filling` |
| M6-006b | Parse an opponent field defensively | DONE | `parse_smell_grid(grid, board)` rejects a malformed key, a non-numeric/negative intensity, **and** any cell off the negotiated board — an opponent's field is untrusted input; `test_an_off_board_cell_is_rejected_against_the_negotiated_grid` |
| M6-006c | Pin the numeric precision on the wire | DONE | `encode_smell_grid` rounds every intensity to `SCENT_PRECISION` (6 dp), so an identical field serialises to byte-identical bytes on both peers. **Correction 2026-08-06: the stated reason was wrong.** This row claimed byte-identical serialisation is "the property the locked scent-model hash depends on". It is not — `scent_model_record()` contains exactly `model`, `update`, `center_intensity`, `decay_per_step`, `field_size`, and `emission_profile_by_squared_distance`: the *model*, never an emitted value. Verified by inspection. Rounding is a readability and determinism choice; **no lock and no interop property rests on it**, and a peer rounding differently is still conformant. The rounding stays; the justification is corrected |
| M6-007 | Prove the scent model is symmetric and involuntary | DONE | `perception/field.py` (100% branch); `test_field.py`. Emission follows the agent's cell automatically and no path can suppress or fake it; all three sub-tasks below |
| M6-007a | Emit on every action including `STAY` | DONE | `deposit(field, board, cell)` takes the agent's cell, not its action, so a `STAY` re-emits on the same cell; `test_staying_still_still_deposits_scent` shows the stayed centre exceeds decay alone `[book §6]` |
| M6-007b | Read only the opponent's field, never one's own | DONE | `scent_likelihood` turns the *observed* (opponent) field into belief evidence; `test_the_belief_modules_never_read_own_emission` walks `belief`/`hint`/`trust` and proves they never touch the own-emission functions `emit_at`/`deposit` |
| M6-007c | Make suppression impossible by construction | DONE | `deposit`/`emit_at` carry no action and no suppression flag (signature-pinned), and `emit_at` always yields a non-empty field for an on-board cell; `test_emission_cannot_be_conditioned_or_suppressed` |
| M6-008 | Implement hint generation | DONE | `verbal/generation.py` (100% branch); `test_generation.py`. `generate_hint` produces a hint each turn, truthful or bluffed, within the agreed limits. All six sub-tasks below |
| M6-008a | Carry an explicit truth/bluff intent flag | DONE | `Hint(text, intent)` carries `intent ∈ {truth, bluff}`; the caller seals it in the step payload, so it cannot be revised — `test_the_intent_is_sealed_in_the_commitment` shows changing the intent changes `commit_of` |
| M6-008b | Generate from a zero-token template provider | DONE | With no provider, `generate_hint` uses `template_hint` — no network, no account; `test_the_default_path_is_a_validated_zero_token_template` `[AF-t21]` |
| M6-008c | Enforce the word limit at generation time | DONE | Every path (template, landmark, model) runs through `validate_hint`, so the word limit is enforced where the hint is made; default 15 `[AF-t14]` |
| M6-008d | Reject a generated hint that encodes coordinates | DONE | `validate_hint` applies to a model provider's output too; a model that leaks coordinates is refused and the token-free template is sent instead (never forfeiting the turn) — `test_a_provider_that_encodes_coordinates_is_refused_and_falls_back` `[AE-27]` |
| M6-008e | Support landmark hints when a map area is agreed | DONE | `landmark_hint` names an agreed landmark (never a coordinate); `generate_hint` falls back to a generic template when `map_area` is empty; `test_a_landmark_hint_is_used_when_a_map_area_is_agreed` |
| M6-008f | Trigger any model provider only every N steps | DONE | The model provider runs only on every `every_n_steps`-th step; `test_a_model_provider_runs_only_every_n_steps` asserts it fires at steps 0 and 3 of six with `every_n_steps=3` |
| M6-009 | Implement hint consumption | DONE | `perception/consume.py` (100% branch); `test_consume.py`. `consume_hint` updates belief from an inbound hint, weighted by trust, never trusted blindly. All three sub-tasks below |
| M6-009a | Parse an inbound hint without executing it | DONE | `decode_hint` extracts directional words by regex — never `eval`/`exec`; a command-like hint changes belief only by the directional words it contains (none ⇒ no change); `test_a_command_like_hint_is_treated_purely_as_text` |
| M6-009b | Weight the hint by the sender's running trust score | DONE | `consume_hint` tempers the decoded likelihood through `trust_weighted` before `apply_evidence`, so a low-trust hint moves belief far less; `test_the_hint_is_weighted_by_trust`. Repeated contradiction lowers trust via `update_trust` (`M6-003f`) |
| M6-009c | Tolerate an absent, empty, or over-long hint | DONE | A missing, non-text, empty, or over-`max_words` hint contributes a uniform likelihood and leaves the belief unchanged — inbound leniency, never an error; `test_a_missing_empty_or_over_long_hint_leaves_belief_unchanged` |
| M6-010 | Prove the strategy layer under observation tests | DONE | `test_strategy_observations.py` drives the whole perception→strategy pipeline (scent + hint → belief → `choose_evasive_action`) under every observation shape; all five sub-tasks below, behaviour legal and deterministic throughout |
| M6-010a | Test with no scent and no hint | DONE | `test_no_scent_and_no_hint_still_yields_a_legal_action`: a uniform belief still resolves to a legal action |
| M6-010b | Test with contradictory scent and hint | DONE | `test_physical_evidence_wins_over_a_contradicting_hint`: scent says top-left, a hint lies bottom-right; the contradiction lowers trust and the Thief flees the scent — physical evidence wins. **Companion added 2026-08-06** (`test_evidence_priority.py`): the outcome test alone does not say *which* mechanism produced the outcome, and probing showed it is structural — a `0.04` trace beats a lie held at complete trust — so the ordering is pinned directly. The Cop repo reaches the **identical** ordering from a different data structure; both sides now test it, since belief never crosses the wire (`M6-016`) and drift could not otherwise be detected |
| M6-010c | Test with a saturated scent field | DONE | `test_a_saturated_scent_field_does_not_overflow_or_divide_by_zero`: every cell at 0.9 normalises to a legal move, no overflow, no division by zero |
| M6-010d | Test with the Cop adjacent and with the Cop far | DONE | `test_the_cop_adjacent_and_far_both_give_sane_legal_moves`: both legal; an adjacent western Cop drives a flee that increases distance from it |
| M6-010e | Test that repeated runs are byte-identical | DONE | `test_repeated_runs_are_byte_identical`: the belief tuples and the chosen action are identical across repeated runs |
| M6-011 | Benchmark the per-turn decision cost | DONE | `scripts/benchmark_decision.py` + `test_decision_benchmark.py`: the belief update plus policy runs in ~2 ms worst case at the 7×7 grid against a 30 000 ms response budget — four orders of magnitude of headroom. Both sub-tasks below |
| M6-011a | Measure worst-case belief update time | DONE | `worst_case_ms` measures a full decision at the negotiated grid (7×7) and at 20×20; `test_a_turn_at_the_negotiated_grid_is_orders_inside_the_timeout` asserts the worst case is under 1% of the response budget |
| M6-011b | Record the measurement in the research evidence | DONE | `scripts/benchmark_decision.py` writes `results/decision_benchmark.json`, and `PRD_strategy.md` records the figures and the computational-fairness reading — feeds `M9-006` |
| M6-012 | Document the perception and strategy layers | DONE | `PRD_scent_belief.md` covers emission (`M6-001`), the wire observation (`M6-002`/`M6-006`), belief + hint + trust (`M6-003`), the board field (`M6-007`), and the reference formulas + locked model (`M6-012`); `PRD_strategy.md` covers the belief-driven policy (`M6-004`) and the decision benchmark (`M6-011`). Both match the built behaviour. Sub-tasks below |
| M6-012a | Document the belief update rule and its trust factor | DONE | `PRD_scent_belief.md` §"Belief update formulas": the Bayes posterior with normalisation and zero-fallback, the trust-tempering `L_eff = t·L + (1−t)·uniform`, and the `update_trust` agreement/signal formulas — inputs and normalisation stated |
| M6-012b | Document the locked scent model and its hash | DONE | `PRD_scent_belief.md` §"The locked scent model" lists the exact `scent_model_record` members that are canonicalised and SHA-256 locked, and how a differing formula/constant/profile is refused by name `[AE-23]` |
| M6-013 | Keep the verbal layer strictly optional | DONE | Disabling every provider still produces a complete, legal game; `test_verbal_optional.py` + the fallback path in `verbal/generation.generate_hint`. Both sub-tasks below |
| M6-013a | Prove a full series runs at zero tokens | DONE | `test_a_full_series_plays_a_complete_legal_game_at_zero_tokens`: six sub-games of 35 steps run the whole loop (generate → consume → move) with no provider, so no token is spent `[AF-t21]` |
| M6-013b | Prove a provider outage never forfeits a turn | DONE | `generate_hint` catches any provider outage or bad output and falls back to the token-free template — an ordinary hint, indistinguishable to the opponent; `test_a_provider_outage_never_forfeits_the_turn` |
| M6-014 | Add regression vectors for the scent field | DONE | `test_scent_regression.py` pins golden vectors: the exact 5×5 emission field, the five-turn pure-decay sequence (`0.9→0.81→…→0.59049`), the repeated-emission STAY sequence, and a board deposit + STAY — so any change to the profile, the decay factor, or the board deposit breaks a test rather than drifting silently |
| M6-015 | Measure strategy quality against the baseline | DONE | `test_strategy_comparison.py` + `scripts/strategy_comparison.py`: belief-driven evasion survives **125** vs the blind baseline's **52** total steps (4 scenarios × 35), more than doubling survival, so it earns its place. Both sub-tasks below |
| M6-015a | Define the comparison protocol | DONE | A deterministic greedy pursuing Cop, four fixed start scenarios on the 7×7 grid, survival measured to a fixed step horizon — no randomness, so runs are reproducible |
| M6-015b | Record the result either way | DONE | `scripts/strategy_comparison.py` writes `results/strategy_comparison.json` and `PRD_strategy.md` records the table; the test asserts belief `>` blind, so a regression that lost the advantage would fail rather than hide. Feeds `M9-007a` |
| M6-015c | Re-state the evasion acceptance criterion in league points, not survival steps | PENDING | **Found 2026-08-07 by `M9-006`'s widened sweep.** `M6-015` asserts belief-driven evasion beats the blind baseline on *total survival steps*, and over its four fixed openings it does (125 v 52). Over all 24 perimeter openings the steps advantage narrows to 1.51x — and under Appendix F's actual scoring, which pays 10 for reaching the threshold and 5 for capture with nothing in between, the ranking **reverses**: blind 175, belief 140. The blind arm is bimodal (11 outright escapes, the rest caught in 2-7 turns); belief is consistent (median 29, stdev halved) but escapes only 4 times. Paired, belief wins 13 and loses 11. Not patched here because changing the strategy is a larger decision than a measurement batch; see `docs/RESEARCH-REPORT-Performance-Analysis.md` and `results/strategy_arms.json` (`metric_disagreement: true`) | `AF-002`/`AF-004` (both Fixed); `M9-006`; `M9-007a` |
| M6-016 | Prove belief and scent never leak beyond the agreed wire fields | DONE | `test_belief_and_scent_privacy.py`: the `TurnMessage` roster is pinned (only `step`/`sender`/`hint`/`smell_grid`/`commit`/`timestamp` + the optional claim fields — no belief/certainty/trust member), and a guard walks `protocol/` and `adapters/` proving the wire layer never imports the private inference modules (belief, consume, trust, hint, belief_policy), so belief cannot reach a message even indirectly |
| M6-017 | Record the belief model in the academic report | DONE | `README.md` §Report records the belief model: §1 (Dec-POMDP) now names the scent observation and the Bayesian belief that never holds the Cop's cell; §3 (implemented strategy) gives the **Bayes update** (`posterior ∝ b × likelihood`, zero-evidence → uniform), the scent and hint likelihoods, the **trust factor** (`L_eff = t·L + (1−t)·uniform`, trust falls on contradiction), and the **distance objective** (flee the most likely Cop cell), with the measured 125-vs-52 result `[AE-42]` |
| M6-018 | Offer the scent implementation to the opponent for parity | DONE | `perception/scent.py` depends on nothing in this project (only `from __future__`), so it is a self-contained reference unit offerable to an opponent verbatim — `test_scent_shareable.py` pins that. A peer that adopts it or reproduces the documented model produces byte-identical fields, which the `M6-005` lock verifies at negotiation. `PRD_scent_belief.md` §"Offering the scent implementation for parity" records the one-directional offer under `THIEF-002` `[book §6]` |
| M6-019 | Prove evasion improves survival over random legal movement | DONE | `test_random_control.py`: the deterministic baseline survives **52** vs a random legal walk's **39.6** (mean over five seeds) in the `M6-015` pursuit harness — chance is beaten before belief is added. Both sub-tasks below  **Cross-repo note 2026-08-06:** the Cop repo's equivalent (`M6-20`) was measured with a **paired** design — one non-reacting opponent, so every arm meets the identical trajectory on a given seed — plus an `oracle` ceiling arm, over 30 seeds. This row's number is an **unpaired mean over five seeds** with no ceiling arm, so it is the weaker of the two pieces of evidence. Not re-run here: this row is DONE and re-opening another team member's closed work mid-batch is not mine to do unilaterally. Logged as a candidate follow-up |
| M6-019a | Establish the random-legal-move control | DONE | A seeded `random.Random` legal-move walk over five fixed seeds (0–4), averaged for a stable comparison across the four fixed pursuit scenarios |
| M6-019b | Record survival rate for each policy | DONE | `PRD_strategy.md` §"Random-movement control" records the clean hierarchy random 39.6 < baseline 52 < belief-driven 125; feeds `M9-007a` |
| M6-020 | Handle the belief update when the Cop is provably adjacent | DONE | `test_belief_adjacent.py`: a `0.9` scent reading at an adjacent cell (the emission centre — proof the Cop stands there) collapses belief to a near-point-mass on that cell, yet it still sums to 1 and never divides by zero, and the Thief flees with a legal move that strictly increases distance from the Cop |
| M6-021 | Handle the first turn with no prior observation | DONE | `strategy/belief_policy.initial_belief(board, cop_start)` seeds belief as a point mass at the Cop's **public** start cell (this peer moves first, so on turn 1 the Cop is exactly there) rather than uniform; `test_belief_first_turn.py` proves belief begins at the start, sums to 1, and the first move flees it. Off-board start rejected |
| M6-022 | Keep scent physics identical to the locked model at run time | DONE | `perception/scent_lock.assert_scent_locked(agreed_hash)` recomputes the model hash from the code that actually emits and observes and compares it to the hash locked at negotiation, raising `ScentLockError` on any drift — to be called at sub-game start (where the agreed terms hold `scent_model_hash`); `test_scent_runtime_lock.py` `[AE-23]` |
| M6-023 | Bound belief memory across a long series | DONE | `test_belief_bounded.py`: after six sub-games of the step limit (210 updates) the belief is still a fixed 49-cell `7×7` grid and trust is still one scalar — every update returns a fresh fixed-size grid, so nothing accumulates a per-turn history |
| M6-024 | Prove hint generation never blocks the turn deadline | DONE | `test_hint_deadline.py`: token-free generation of a full 210-hint series runs in <100 ms (no external call), and a model provider is reached at most once every N steps (bounded, never every turn); a failing/absent provider falls back (`M6-013b`). A model provider carries its own LLM deadline via the gatekeeper (`M7-003`) |
| M6-025 | Test the strategy against a barrier-heavy board | DONE | `test_strategy_edge_cases.py`: 14 barriers (the Appendix F maximum) wall the Thief into a corridor, and `choose_evasive_action` still returns a legal move — the sane flee east from a western threat |
| M6-026 | Test the strategy when only `STAY` is legal | DONE | `test_strategy_edge_cases.py`: a corner with both neighbours barriered leaves only `STAY`; the policy returns `STAY` rather than raising, so capture resolves on the board, not in a crash |
| M6-027 | Document the trust-decay policy for repeated lies | DONE | `PRD_scent_belief.md` §"Trust-decay policy for repeated lies": trust falls by `rate` (0.2) per full contradiction, recovers by `rate` per corroboration, clipped `[0,1]`, so ~5 lies reach the floor and a liar can rebuild by telling the truth; pinned by `test_trust_decay.py` (repeated lies → floor monotonically, truthful hints → ceiling) |
| M6-028 | Add a determinism regression test across releases | DONE | `test_determinism_regression.py` pins the golden action sequence (`S, N, N, S, N`) the belief-driven policy makes for a fixed sequence of believed Cop cells, so any silent change to the ranking, tie-break, or metrics breaks the test rather than shipping unnoticed |

---

## M7 — Series orchestration, artifacts, gatekeeper and reporting

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M7-001 | Orchestrate the accepted six-sub-game series lifecycle | DONE | `orchestration/series.py` (100% branch); `test_series.py`. `run_thief_series` runs this team's Thief sub-games under one identity and aggregates the score. All four sub-tasks below |
| M7-001a | Run six sub-games under one series identity | DONE | `run_thief_series(series_id, …)` carries the `series_id` and each `sub_game_number` into every `SubGameResult`; `NUM_SUB_GAMES = 6` `[AF-t18]` |
| M7-001b | Implement the confirmed six-sub-game role schedule | DONE | The schedule is **injected** — `THIEF_SUBGAMES_NATURAL = (1,3,5)` / `THIEF_SUBGAMES_SWAPPED = (2,4,6)` (`U-021`), passed to `run_thief_series`, so a later correction is a one-line change; `test_the_swapped_schedule_is_injected_not_hard_coded` (`C-012`) |
| M7-001c | Aggregate cumulative series score | DONE | Per-sub-game Thief scores (Appendix F table 17) sum to `SeriesResult.cumulative_score`; `test_a_natural_series_runs_its_thief_sub_games_under_one_identity` (10+10+5 = 25) |
| M7-001d | Apply the tie award on a cumulative tie | DONE | A tied sub-game already pays the table's `TIE_SCORE` via `thief_score(Outcome.TIE)`; `is_cumulative_tie(a, b)` detects a level series total, which reporting settles (`M7-017`); `test_a_cumulative_tie_is_detected` `[AF-t17]` |
| M7-002 | Build accepted declaration, config, log, and result artifacts | DONE | `reporting/` builders for all four artifacts (each module 100% branch; `test_artifacts.py`, `test_artifact_naming.py`). **Schemas follow the documented, unauthenticated template — the coordinator authorised building against it 2026-08-05 pending a `U-019` ruling**, so the exact field set may still change. Naming/identity are book-confirmed. All sub-tasks below Status qualifier: (U-019-provisional). |
| M7-002a | Emit `declaration_<game_id>.json` | DONE | `reporting/declaration.build_declaration`: `_schema`/`schema_version`/`declaration_type`/identity/`links`/`timezone`/times/`num_sub_games`/`max_tokens_per_game`/`groups`, each group carrying members, both repos, `mcp_servers`, `llm_model`, `hardware_spec`, `signature`; validates the group and hardware key sets Status qualifier: (U-019-prov.). |
| M7-002b | Emit `config_<game_id>_g<NN>.json` | DONE | `reporting/config_artifact.build_config`: the seven documented sections plus `agreed_between`, identity, `sub_game_number`, and the `config_sha256` lock over the quantitative content Status qualifier: (U-019-prov.). |
| M7-002c | Emit `log_<game_id>_g<NN>.json` | DONE | `reporting/log_artifact.build_log`: `summary` + the step-by-step commit-reveal `records` (each `payload`/`nonce`/`commit`) + `mutual_agreement`, sufficient to recompute every commitment Status qualifier: (U-019-prov.). |
| M7-002d | Emit `result_<game_id>.json` | DONE | `reporting/result_artifact.build_result`: per-group blocks, per-sub-game lines, and the cumulative `final_result`; this is the emailed report Status qualifier: (U-019-prov.). |
| M7-002e | Share one `game_uid` across all four artifacts | DONE | `MatchIdentity(game_id, game_uid)` is the one identity, `match_filenames` derives all four filenames from the single `game_id` (`AF-021`), and every builder now stamps the shared `game_uid`/`game_id` inside its artifact from that identity (`AR-001` / `AF-§3`) |
| M7-002f | Carry four repository links in the result artifact | DONE | `build_result` collects the four links (two per group, from each group's `repos`) into `links.repositories` and refuses anything other than four; `test_the_result_carries_four_repo_links_and_per_game_commit_and_tokens` `[AE-49]` Status qualifier: (U-019-prov.). |
| M7-002g | Carry the per-game commit hash and total tokens | DONE | Each result sub-game requires `github_commit` and `tokens`; a missing commit is refused (`test_a_result_missing_the_per_game_commit_is_rejected`) `[AE-53]` `[AE-54]` Status qualifier: (U-019-prov.). |
| M7-003 | Implement the centralized external-call gatekeeper | DONE | `services/gatekeeper.py` (now token-bucket-based) + `services/token_bucket.py`; `test_gatekeeper.py`, `test_token_bucket.py`, `test_external_gatekeeper.py`. All four sub-tasks below |
| M7-003a | Route every external call through one gatekeeper | DONE | `test_external_gatekeeper.py` walks `src/` and fails on any direct import of a Gmail/LLM API (googleapiclient, smtplib, openai, anthropic, …), so the Gmail (`M7-005`) and verbal (`M7-004`) paths must route through the one gatekeeper `[G§5.1]` |
| M7-003b | Implement the token bucket | DONE | `services/token_bucket.TokenBucket` implements `AE-28` exactly — `tokens ← min(C, tokens + r·Δt)`, admit iff `tokens ≥ 1`, consume on admit — wired into the gatekeeper's rate decision (`requests_per_minute` tokens refilling at `rpm/60`/s); `test_token_bucket.py` (100% branch) `[AE-28]` |
| M7-003c | Queue overflow rather than rejecting | DONE | Overflow is **queued, not rejected** — `submit` returns `False` and enqueues to `queue_depth`, and only a genuinely full queue raises `GatekeeperError`; `drain` releases as rate and concurrency allow `[G§5.3]` |
| M7-003d | Read every limit from configuration | DONE | `Gatekeeper.from_match` reads `requests_per_minute`/`concurrent_requests`/`queue_depth` from the signed match object's `rate_limiter_gatekeeper` (Appendix F table 19 `Minimum`s); no hard-coded rate `[G§7.2]` `[AF-t19]` |
| M7-004 | Implement accepted private verbal-provider modes | DONE | `verbal/providers.py` (100% branch); `test_providers.py`. The default is the zero-token template (`M6-008`); `gated_model_provider` wraps an operator's model (Ollama/API/CLI) behind the **one** gatekeeper (`M7-003a`), and a mocked model routes through the gate. Sub-task below |
| M7-004a | Fall back deterministically on provider failure | DONE | With the gate at capacity `guard` raises, and a failing model raises; either way `generate_hint` falls back to the token-free template, so a blocked or broken provider never stalls a turn; `test_a_blocked_provider_falls_back_to_the_template`, `test_a_failing_model_falls_back_to_the_template` |
| M7-005 | Send the mutually agreed final JSON report through Gmail | DONE | `reporting/email_report.py` (100% branch); `test_email_report.py`. Compose + gated send + 429 backoff, transport **injected** and mocked in tests. The **live `gmail.send` adapter (OAuth, credentials) is `U-009`/`M7-013`** and not built here. Sub-tasks below Status qualifier: (mocked; live adapter = `U-009`). |
| M7-005a | Restrict the OAuth scope to `gmail.send` | DONE | `GMAIL_SEND_SCOPE = ".../auth/gmail.send"`; a test asserts no `readonly`/`modify` scope `[AE-30]` |
| M7-005b | Keep `credentials.json` and `token.json` git-ignored | DONE | `.gitignore` covers `credentials.json`, `token.json`, `*credentials*.json`, `*token*.json` `[AE-39]` `[AE-40]` |
| M7-005c | Send JSON as an attachment only | DONE | `compose_report` attaches the result as `application/json` (`result_<id>.json`); the body carries no report — `test_the_report_is_a_json_attachment_to_the_confirmed_address` `[AE-33]` `[AE-34]` |
| M7-005d | Send to the confirmed reporting address | DONE | `REPORTING_ADDRESS = "rmisegal+uoh26finalgame@gmail.com"` (`AF-020`; Table 20 `rimesegal` is a typo) is the default recipient |
| M7-005e | Back off on HTTP 429 | DONE | `send_report` catches `RateLimitError` (429), sleeps the backoff, and retries to the limit, then fails loudly; `test_a_429_is_backed_off_and_retried` `[book §12]` |
| M7-005f | Run the full mutual audit before agreeing a result | PENDING | Result agreement follows the mutual audit — owned by `M7-016` `[AE-36]` |
| M7-005g | Send independently of the opponent | DONE | `send_report` takes no opponent and never waits on one — a side that does not send scores nothing `[AE-32]` `[AE-35]` |
| M7-006 | Implement the Quota Manager and DOS Detector gates | DONE | `services/send_gates.py`. `:2096` requires **three** gates before Gmail -- Quota Manager, Token Bucket, DOS Detector -- and only the middle one existed here, so a report could reach the API having passed **one gate of three** |
| M7-006a | Implement the daily quota counter | DONE | `QuotaManager`, a per-day counter that rolls over. `:2083`: "the **final line before account blocking**: if the quota is exhausted, no further requests are sent" |
| M7-006b | Implement the DOS detector and pipeline lock | DONE | `DosDetector` locks on a burst and **stays locked**. `:2087` says what it guards: "a bug or an infinite loop **in the agent's code**" -- our own runaway, not a hostile peer -- so a lock that cleared after a quiet spell would let the same loop resume |
| M7-006c | Prove fail-fast ordering across the three gates | DONE | Fail-fast, first refusal short-circuiting. **An API difference caught here that copying would have missed**: this repository's `TokenBucket.allow` *consumes* a token, so `attempt` inspects with `available` and only `send` calls `allow`. A naive check would have burned a token on every request a later gate refused -- a silent, gradual throttle for sends that never happened |
| M7-007 | Declare games already played against each opponent | PENDING | Appendix E rules 37/38: every game start carries an accurate count of prior counted games against that opponent, derived from emitted result artifacts rather than hand-entered. A false declaration is absolute disqualification, so the count must be reproducible from the artifact set |
| M7-007a | Derive the count from emitted result artifacts | PENDING | No hand-entered figure enters the declaration |
| M7-007b | Exclude warm-up games from the counted total | PENDING | `[AE-52]`; warm-ups are permitted but uncounted |
| M7-008 | Attach every game's configuration artifact to the repository | PENDING | Appendix F.2 items 3 and 4: each game's configuration artifact is named from its `game_id` and committed, so any past game's exact configuration remains retrievable |
| M7-008a | Commit each game's config under a `game_id`-derived name | PENDING | Artifacts from different games cannot collide |
| M7-008b | Prove any past game's config is retrievable from the repo | PENDING | A retrieval test walks the committed set |
| M7-009 | Account for LLM tokens across a series | PENDING | Per-game and per-series totals counted, sealed at Step-0, and reported `[AE-54]` |
| M7-010 | Emit warm-up games as uncounted | PENDING | A warm-up produces artifacts but never enters the counted total `[AE-52]` |
| M7-011 | Persist artifacts atomically | DONE | `reporting/emit.write_artifact` writes to a temporary file **in the same directory** then `os.replace`, so the visible file is either the old one or the complete new one, never a prefix. Same-directory is load-bearing: `os.replace` is atomic only within a filesystem. The failure this closes is **silent** -- a truncated artifact looks present, and rule 19's audit reads it as a technical mismatch ("score of 0 for the falsifying group") with nothing distinguishing it from a deliberate forgery |
| M7-012 | Validate every emitted artifact against its schema | PENDING | An artifact that fails its own schema is never sent |
| M7-012a | Validate the declaration artifact | PENDING | Required identity, hardware, and timing fields present |
| M7-012b | Validate the config artifact | PENDING | Every Appendix F parameter present with a legal value |
| M7-012c | Validate the log artifact | PENDING | Every step carries commitment, nonce, move, and hint |
| M7-012d | Validate the result artifact | PENDING | Scores, four links, commit hash, and token totals present |
| M7-012e | Reject an artifact set whose `game_uid` values disagree | PENDING | All four must share one identity `[AF-§3]` |
| M7-013 | Implement the OAuth setup path | PENDING | First run creates a token; later runs refresh without human action |
| M7-013a | Run the consent flow once and store the token locally | PENDING | `token.json` created, never committed `[book App. A]` |
| M7-013b | Refresh the access token automatically | PENDING | The refresh token gives months of autonomy |
| M7-013c | Fail closed when no credential is present | DONE | `send_report` refuses when the credential path is absent. A skipped report is indistinguishable from a successful one in a log that only records errors |
| M7-013d | Document the five setup steps for a fresh machine | PENDING | Reproducible by a teammate `[G§2.1]` |
| M7-014 | Compose the report email | PENDING | MIME message with a JSON attachment and a machine-stable subject |
| M7-014a | Attach the result artifact as a file | PENDING | Attachment only; body text is never the report `[AE-34]` |
| M7-014b | Use a deterministic subject naming the game | DONE | **The subject was deterministic but unassignable.** It named the game (`UOH26 Final Result — <game_id>`) and carried no team code, while rule 45 (Mandatory) ties **automatic report assignment** to the 8-character code, sanction "organizational failure that will prevent automatic report assignment". Now `[<team_code>] UOH26 Final Result <game_id>`, with a non-8-character code refused |
| M7-014c | Base64url-encode and send through the API | PENDING | `users().messages().send` with `userId="me"` |
| M7-015 | Prove reporting under failure | DONE | All three failure modes covered by `send_report` |
| M7-015a | Retry after a 429 with backoff | DONE | Backoff on 429, **changed from constant to doubling**. Both honour Appendix F table 19's `Minimum` of 5s, so the original was not wrong -- this is a deliberate strengthening, recorded as such in the test. A fixed delay against a provider still throttling spends every retry at the rate it already refused |
| M7-015b | Surface a permanently failed send loudly | DONE | `ReportSendError` after the retries, naming the last error |
| M7-015c | Never send twice for one game | DONE | **A real gap: `send_report` could be called twice for one game.** Now keyed on `game_id` against a caller-held set. Rule 35 scores a conflicting report 0 for **both** teams, and a duplicate is the easiest way to produce one by accident |
| M7-016 | Implement result agreement with the opponent | DONE | `orchestration/settlement.py`, built on this repo's own `protocol.crypto.audit_records`. Four states with four remedies: `AGREED`, `CONFLICT` (rule 35, 0/0 both), `AUDIT_FAILED` (rule 19, 0 for the falsifying group) and `UNANSWERED` |
| M7-016a | Exchange the computed outcome after the audit | DONE | `agree(audit, ours, theirs)` **takes the audit first**, so agreement is unreachable without one. Rule 36 makes the audit "a mandatory condition before agreement on the JSON result" -- a precondition a caller can forget is not a precondition. An empty series does not pass |
| M7-016b | Detect and record a disagreement | DONE | A conflict keeps **both** claims in `settlement_record`. Adopting their number to keep the peace files a result we do not believe and destroys the evidence an auditor needs. **Silence is its own state**, not consent -- otherwise a crashed peer decides our report |
| M7-016c | Refuse to report an unagreed result | DONE | `require_reportable` gates reporting, and the audit-failure message differs deliberately: their forgery is *their* rule 19 loss, and sending our own contradicting report would convert it into a **shared** rule 35 loss. A test asserts the three refusals carry three distinct messages |
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
| M8-001 | Build a live Thief local-truth GUI through the SDK | DONE | View-model truth-boundary tests |
| M8-001a | Render the belief heatmap | DONE | Deeper colour means higher probability `[PRD-gui]` `[ADR-0009]` |
| M8-001b | Render the turn banner | DONE | Green `YOUR TURN`, grey `LOCKED` after commit |
| M8-001c | Lock input while the banner is grey | DONE | Out-of-turn input is ignored |
| M8-001d | Prove the objective board is never renderable | DONE | `[AE-8]` `[AE-9]` |
| M8-002 | Build replay UI on the accepted verifier | DONE | Valid/malformed/reordered/tampered replay tests |
| M8-002a | Load a saved match log and step forward/back | DONE | `[AE-20]` mandatory `[PRD-replay]` |
| M8-002b | Recompute every step's hash and compare | DONE | Uses the M4 construction |
| M8-002c | Void the whole match on the first mismatch | DONE | A single tampered step yields `TAMPERED` |
| M8-002d | Record why the book's chapter-7 verifier is not used | DONE | Book p. 74 computes `SHA256("{nonce}|{move}")`, which cannot verify a chapter-5 commitment |
| M8-002e | Document the replay UI workflow and states | DONE | Screens, controls, and both verdict states described `[G§10.2]` |
| M8-003 | Run bidirectional games against a neutral compliant-opponent harness | PENDING | Unknown-opponent E2E evidence |
| M8-003a | Rehearse against a stub that shares no source with this repo | PENDING | Independently authored; imports no project module |
| M8-003b | Prove both proposal and acceptance directions | PENDING | Neither direction needs a profile file edited |
| M8-003c | Rehearse against a real classmate agent before the counted league | PENDING | Warm-ups are permitted and uncounted `[AE-52]` |
| M8-004 | Harden secrets, identity, input validation, and dependency boundaries | PENDING | Security/privacy review and tests |
| M8-004a | Validate every inbound field before use | PENDING | Malformed peer input cannot reach domain code `[G§6.3]` |
| M8-004b | Bound memory and queue growth under sustained load | PENDING | No unbounded queue or leak over a long series |
| M8-004c | Apply Nielsen usability heuristics to both UIs | PENDING | Visibility of status, error prevention, recovery `[G§10.1]` |
| M8-005 | Exercise crash, timeout, mismatch, and tamper recovery end to end | IN PROGRESS | Failure-injection evidence |
| M8-005a | Inject crash, timeout, mismatch, and tamper faults | IN PROGRESS | Each produces a defined, logged outcome |
| M8-006 | Build the GUI view-model behind the SDK | DONE | No widget touches domain or protocol code directly `[G§4.1]` |
| M8-006a | Expose a read-only snapshot for rendering | DONE | The view cannot mutate game state |
| M8-006b | Update the view on state change rather than polling | DONE | Redraw follows the state machine |
| M8-006c | Keep the GUI out of coverage requirements | DONE | Omitted per the guidelines' coverage config `[G§6.2]` |
| M8-007 | Render the board and own position | DONE | Own cell, known barriers, and turn number are visible |
| M8-007a | Render known barriers only | DONE | A barrier appears only once disclosed `[AE-15]` |
| M8-007b | Render received hints as text | DONE | The verbal channel is visible to the operator |
| M8-007c | Show the current score and step count | DONE | Operator can see progress toward the threshold |
| M8-008 | Implement replay navigation | DONE | Step forward, step back, and jump to a step |
| M8-008a | Recompute verification on every navigation | DONE | The verdict is derived, never cached from load time |
| M8-008b | Show the per-step verdict alongside the board | DONE | Operator sees where a match failed |
| M8-008c | Load a malformed log without crashing | DONE | Corrupt input yields a clear error, not a stack trace |
| M8-008d | Detect a reordered log | DONE | Step sequence is validated, not assumed |
| M8-009 | Run the security review | IN PROGRESS | Secrets, identity, input validation, and dependencies all reviewed |
| M8-009a | Confirm no secret is readable from any artifact | IN PROGRESS | Artifacts are shared; secrets must not travel in them `[AE-39]` |
| M8-009b | Confirm no private field crosses the wire | IN PROGRESS | Leakage vector per private field class |
| M8-009c | Review third-party dependencies and pin them | IN PROGRESS | `uv.lock` is authoritative `[G§8.4]` |
| M8-009d | Confirm the LLM path cannot influence a move | IN PROGRESS | Even with a provider enabled `[AE-25]` |
| M8-010 | Run the resource and endurance pass | PENDING | A full six-sub-game series runs without degradation |
| M8-010a | Run a long series and watch memory | PENDING | No unbounded growth across sub-games |
| M8-010b | Confirm clean shutdown releases every resource | PENDING | Sockets, files, and threads all closed |
| M8-011 | Document both interfaces | DONE | Screens, states, and workflows described `[G§10.2]` |
| M8-011a | Document the live GUI workflow | DONE | Turn banner states and what each means |
| M8-011b | Document accessibility considerations | DONE | Colour is not the only signal `[G§10.2]` |
| M8-012 | Prove the replay app on a foreign log | DONE | It verifies a log this peer did not write |
| M8-012a | Verify an opponent-produced log | DONE | The audit is mutual; both logs must verify `[AE-36]` |
| M8-012b | Detect a foreign log that was tampered | DONE | The detection path is not self-only |
| M8-013 | Rehearse the full failure matrix end to end | IN PROGRESS | Every fault class has an observed outcome, not a predicted one |
| M8-013a | Rehearse an opponent crash mid-series | IN PROGRESS | The series still produces artifacts |
| M8-013b | Rehearse a tunnel drop mid-turn | IN PROGRESS | Terminal outcome is defined, not a hang |
| M8-013c | Rehearse a config mismatch at negotiation | IN PROGRESS | The match is refused before play `[AE-11]` |
| M8-014 | Freeze the wire profile before the counted league | PENDING | No wire change after the first counted game without a coordinator decision |
| M8-015 | Capture the required submission screenshots | DONE | Belief-map GUI and replay `Verified OK` `[AE-42]` |
| M8-015a | Capture the belief-map GUI screenshot | DONE | Required README content |
| M8-015b | Capture the replay `Verified OK` screenshot | DONE | Required README content |
| M8-015c | Capture a `TAMPERED` screenshot from a corrupted log | DONE | Demonstrates the detection path |
| M8-015d | Make every screenshot reproducible from a stored fixture | DONE | A grader can regenerate them |

---

## M9 — League evidence, submission and release

| ID | Thief-owned task | Status | Exit evidence |
|---|---|---|---|
| M9-001 | Capture required league/game artifacts and repository commit evidence | DONE | Reviewed evidence bundle |
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
| M9-006 | Complete parameter research and sensitivity analysis | DONE | Guidelines §9.1: systematic one-at-a-time experiments across the negotiable parameters, with the measured effect of each on match outcomes documented in tables |
| M9-006a | Sweep the negotiable board and movement parameters | DONE | Grid size, barrier quota, step limit, survival threshold |
| M9-006b | Sweep the scent parameters within their fixed bounds | DONE | Sensitivity to `ρ` and field size, noting both are `Fixed` for play |
| M9-006c | Record each parameter's measured effect on outcome | DONE | Experiment tables with run counts, not anecdotes |
| M9-007 | Publish the results-analysis notebook and result visualisations | DONE | Guidelines §9.2/§9.3: a notebook compares strategies and configurations, uses LaTeX for equations, cites academic references, and emits labelled high-resolution charts |
| M9-007a | Compare the baseline against belief-driven evasion | DONE | Survival rate and mean survived turns over repeated runs |
| M9-007b | Emit labelled, accessible, high-resolution charts | DONE | Clear axes, legend, caption `[G§9.3]` |
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
| 2 | Basic MCP infrastructure over localhost | `M5-002`, `M5-002e` | complete — `M5-002e` observed a message sent by a real second interpreter over HTTP and read back from its transcript (`test_localhost_two_processes.py`) |
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
| 2 | `M5-002` FastMCP server and client | `M4` substance (built) | DONE — both adapters ship under `adapters/` and `fastmcp` is a live dependency |
| 3 | `M5-002e` localhost end-to-end | item 2 | DONE — the book stage-2 gate is observed running two real interpreters over HTTP |
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
