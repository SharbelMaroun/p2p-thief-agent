# Prompt Engineering Log

> **KEEP WITH WARNING.** This is provenance, not authoritative evidence. Prompts and
> their outputs cannot confirm a requirement.

- **Document version:** 1.00 · **Status:** LIVING DOCUMENT — update with every significant AI-assisted step (guidelines §8.3)
- **Purpose:** record all significant prompts used to build the project: context/goal, the prompt, output received, refinements made, and best practices derived.

> Entry template:
> **P-###** · date · tool/model · **Goal** · **Prompt (essence)** · **Output** · **Refinement** · **Lesson**

---

## P-001 — Source-document digestion
- **Date:** 2026-07-23 · **Tool:** Claude (agentic CLI)
- **Goal:** make the 160-page rulebook PDF usable as build context.
- **Prompt (essence):** "Analyze `police_thief_p2p_Summary.md`" → then "pass page after page and make a summary for each single page, so a builder model won't lose context because the file is too big."
- **Output:** `Material/police_thief_p2p_PerPage_Condensed.md` — 160 pages compressed ~6× (262 KB → 43 KB) with page anchors (P1–P160), a master quick-reference of binding Appendix-F parameters, and all formulas/code kept verbatim.
- **Refinement:** front-loaded a "Master Quick-Reference" section so a builder that reads only the top still gets every binding value and disqualification trap.
- **Lesson:** for long specs, per-page anchors + a front-loaded binding-values table beat prose summaries; keep formulas and config exact, compress narration.

## P-002 — Reference-simulator analysis
- **Date:** 2026-07-23 · **Tool:** Claude (agentic CLI)
- **Goal:** understand what the lecturer's `Game-P2P-Cop-Chase` engine provides vs. what remains our work.
- **Prompt (essence):** "Analyze the SimulatorEXM-Repo the lecturer gave us"; "run it so I can see it"; "how does the LLM work inside it without an API key?"
- **Output:** full architecture map (sdk/peer/domain/infra/shared/gui layers); a live headless match (thief survival 35 steps, audit 36/36 verified, 0 tokens); the finding that the default banter provider is a zero-token template and the LLM is never used for moves.
- **Refinement:** identified deviations where the book wins (subtractive vs. multiplicative scent decay) — later codified as ADR-5.
- **Lesson:** run reference code and read its config before designing; explicitly log where a reference deviates from the binding spec.

## P-003 — Core documentation suite
- **Date:** 2026-07-24 · **Tool:** Claude (agentic CLI)
- **Goal:** produce the mandated pre-code docs (guidelines §2.2, §2.5).
- **Prompt (essence):** "Should we start building the requested md files?" + decision answers: *clean reimplementation*, *core docs first*.
- **Output:** `docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md` v1.00 (requirements, C4 architecture + ADRs, phased roadmap).
- **Refinement:** the approach decision (clean reimplementation vs. build-on-engine) was asked explicitly before writing — it changes the whole PLAN.
- **Lesson:** resolve architecture-defining decisions with the human *before* generating docs, not after.

## P-004 — Work-breakdown expansion (620 tasks)
- **Date:** 2026-07-24 · **Tool:** Claude (agentic CLI)
- **Goal:** granular, checkable task list for the whole project.
- **Prompt (essence):** "Rebuild all the md files under docs so the TODO has 600+ tasks."
- **Output:** `TODO.md` v2.00 — 620 sequential tasks (T001–T620), 9 phases, per-area "Done when" gates, priorities P0/P1/P2; PRD gained a traceability matrix; PLAN gained a module→task inventory.
- **Refinement:** IDs made globally sequential and grep-verifiable (`grep -c '^- \[ \] \*\*T'`); count checked mechanically, no duplicates.
- **Lesson:** make generated task lists mechanically verifiable (stable IDs, one task per line) so completeness claims can be checked, not trusted.

## P-005 — Per-mechanism PRDs
- **Date:** 2026-07-24 · **Tool:** Claude (agentic CLI)
- **Goal:** the specialized PRDs required per algorithm/mechanism (guidelines §2.3).
- **Prompt (essence):** "Write the 5 per-mechanism PRDs" + "what else did the instructions ask for?" (surfaced the prompt-log requirement → this file).
- **Output:** `PRD_commit_reveal`, `PRD_scent_belief`, `PRD_strategy`, `PRD_p2p_mcp`, `PRD_gatekeeper_reporting` — each with theoretical background, requirements, I/O contract, metrics, constraints, alternatives-considered, success criteria, test scenarios.
- **Lesson:** mirror the rubric's required section list exactly; verify with a section-presence grep.

## P-006 — Review pass against sources (v2.10)
- **Date:** 2026-07-24 · **Tool:** Claude (agentic CLI)
- **Goal:** re-read Material sources and audit docs for gaps.
- **Prompt (essence):** "Read the md files under Material, check docs, enhance/fix what you find."
- **Output:** four confirmed gaps fixed across all docs: (1) the **Acknowledge** step of the commit-reveal sequence (Commit→Ack→Reveal→Final-Reveal) was missing; (2) **barrier-on-thief-cell capture** + honest capture answer missing from FR-4; (3) **NL-only hint rule / no coordinate protocols** (Appendix E rules 26–27) missing; (4) official **series = 6 sub-games** (Appendix F Table 18) + league integrity rules (one counted game per opponent, conflicting reports → 0/0) missing. Also added: mermaid state/sequence diagrams, threading model, coding/testing standards, `world` config section, addendum tasks T621–T632.
- **Lesson:** always re-audit generated docs against the binding source with targeted greps on suspected weak spots (protocol steps, fixed parameters, prohibition rules) — summaries drop steps that "feel" implicit, like an ack.

## P-007 — Full compliance audit vs. all three sources (v2.11)
- **Date:** 2026-07-24 · **Tool:** Claude (agentic CLI)
- **Goal:** verify every doc claim against the condensed spec, the full rulebook translation, and the submission guidelines.
- **Prompt (essence):** "Check if everything is made according to `police_thief_p2p_PerPage_Condensed.md`, `police_thief_p2p_Summary.md` and `software_submission_guidelines-V3_Summary.md`."
- **Output:** rule-by-rule sweep of Appendix E (55 rules) + Appendix F tables + guidelines §1–20 against PRD/PLAN/TODO/5 PRDs. Three confirmed gaps fixed: (1) **rule 49** — the game-end JSON needs **four** repo links (two per team), docs said "both"; (2) **rule 23** — the scent-model pre-game crypto-lock was only implicit in the signed `game.json`, now explicit in NET-7 + scent PRD; (3) guidelines **§10** UI documentation (workflows, accessibility, Nielsen heuristics) had no task. Plus stale "620-task" references reconciled to 635. New tasks T633–T635 (Addendum B).
- **Lesson:** suspicious grep targets for audits are *counted things* ("both", "two", "all") — a source that says "four links" while the doc says "both links" is exactly the class of bug summaries introduce; verify every quantity against the primary source, not the derived one.

---

## Best practices derived so far
1. **Binding values live in one table** — quote Appendix F, never paraphrase numbers.
2. **Decide, then generate** — architecture-defining choices go to the human first.
3. **Mechanical verifiability** — sequential IDs, one item per line, grep-checkable counts and section lists.
4. **Reference ≠ spec** — log every reference-code deviation and let the book win (ADRs).
5. **Audit passes are prompts too** — schedule an explicit "find what's missing" pass after any large generation; it found 4 real gaps here.

## P-008 — M0–M1 reconciliation and scaffold

- **Date:** 2026-07-25 · **Tool:** OpenAI Codex implementation agent
- **Goal:** reconcile main with useful Sharbel planning, preserve stronger Appendix
  E/F and JSON-template evidence, and create a behavior-free uv package scaffold.
- **Prompt (essence):** inspect all branches and five predicted conflicts; port only
  source-backed material; consume the Cop-owned contract without inventing it; add
  SDK-first tests and professional quality gates; stop before runtime behavior.
- **Output:** five-conflict reconciliation, direct source hashes, narrowed unknowns,
  ten ADR placeholders, provider-neutral secrets policy, `p2p_thief_agent` scaffold,
  tests, lockfile, and quality scripts. At that review time the Cop proposal had not
  yet appeared; this statement was superseded by P-009.
- **Refinement:** used the official guideline PDF for the exact Ruff/version policy,
  observed the SDK test fail before implementation, and rejected branch claims that
  weakened verified values or overstated LLM movement guidance.
- **Lesson:** parallel agents can audit branches, sources, and external dependencies,
  but shared protocol bytes must wait for the designated proposal and an actual hash
  comparison.

## P-009 — Independent contract-readiness review

- **Date:** 2026-07-26 · **Tool:** OpenAI Codex implementation/review agent
- **Goal:** review immutable Cop candidate `84339c2` without integration, correct stale
  Thief status/source claims, add CI, and make the M1 handoff fail closed.
- **Prompt (essence):** obey the coordinator audit; preserve `Material/`; inspect Cop
  through Git only; do not copy shared files or begin gameplay; make four atomic
  commits; align M0–M9 and require exact acceptance metadata/hashes.
- **Output:** corrected source/provenance status, path-by-path candidate NO-GO review,
  GitHub Actions quality gates, M0–M9 Thief ledger, and exact-byte handoff checklist.
- **Refinement:** separated Cop-local manifest integrity from cross-repository parity
  and treated generated JSON examples as unauthenticated observations.
- **Lesson:** a proposal's existence is not acceptance; consumers need a pinned commit,
  version, manifest self-hash, exact path list, per-file hashes, and explicit
  coordinator verdict before trusting or copying bytes.

## P-010 — Book and JSON-template evidence reconciliation

- **Date:** 2026-07-27 · **Tool:** OpenAI Codex implementation/review agent
- **Goal:** verify the supplied Moodle, reporting, configuration, identity,
  canonicalization, scheduling, and schema claims against project book v3.0.0 and the
  four local JSON examples.
- **Prompt (essence):** treat the book and supplied templates as new evidence; identify
  which assertions are binding, partial, or unsupported; update project controls
  without editing Cop-owned shared contract files or beginning gameplay.
- **Output:** source-page verification, a claim-by-claim reconciliation, confirmed
  Moodle/PDF and README evidence requirements, a narrowed shared/private config
  boundary, common artifact-identity requirements, and explicit open conflicts for
  role scheduling, schema compatibility, result-byte identity, and hash scope.
- **Refinement:** separated sorted compact UTF-8 serialization in the Chapter 5 commit
  example from the still-undefined full `config_sha256` algorithm; did not infer OAuth
  credential storage, UUID grammar, or mandatory `links` fields from generated data.
- **Lesson:** examples can confirm field presence, but only authoritative prose can
  establish requiredness and semantics; byte-level cryptographic rules need explicit
  scope and shared test vectors.

## P-011 — Proposed pre-game gate resolution audit

- **Date:** 2026-07-27 · **Tool:** OpenAI Codex implementation/review agent
- **Goal:** determine whether supplied simulator mechanics, schema labels, commits,
  and hashes satisfy the coordinator's M1 gate.
- **Prompt (essence):** treat `REQUIRED_TERMS`, `validate_agreement`, odd/even
  `role_for()`, canonical JSON settings, schema labels, and supplied fixed hashes as a
  proposed technical resolution before gameplay.
- **Output:** exact template-value verification, current simulator-tag verification,
  revised Cop-candidate review, a separation of match artifacts from repository
  parity evidence, and a corrected provisional-copy → parity/conformance → final-freeze
  handoff sequence.
- **Refinement:** verified that `7cf3fc9` is historical simulator tag `v1.11`, that the
  two supplied hashes are absent from the files, and that simulator
  `validate_agreement` checks missing terms but does not itself perform signature
  exchange or cross-repository parity.
- **Lesson:** runtime preflight, match cryptography, and repository supply-chain
  integrity are three different gates; one hash or one validation function cannot
  substitute for the others.

---

> **Provenance note for P-012 … P-018.** These entries were reconstructed on
> 2026-07-28 from commits, diffs, and the documents they produced, because the log had
> fallen 17 commits behind. They are **not transcribed from the original sessions**:
> the "Prompt (essence)" lines record the evident task, not verbatim wording, except
> for P-017 and P-018 which were written in the session that performed them. Model
> attribution is taken from the `Co-Authored-By` commit trailers, not from memory.

## P-012 — Read-only review of Cop candidate `e0df5ba`

- **Date:** 2026-07-28 · **Tool:** Claude Sonnet 4.6 (agentic CLI)
- **Goal:** decide whether the newest remotely available Cop candidate could be copied.
- **Prompt (essence):** review the candidate path by path from Git objects only, without
  copying or modifying any Cop-owned file.
- **Output:** `CONTRACT_REVIEW.md` path-by-path table over 18 controlled files, crediting
  the genuine fixes (`rate_limits.json` moved local, `agreed_between` required,
  `--compare-root` added) while raising a P0: `config/game.json` embeds match-specific
  participant IDs, so controlled bytes cannot stay frozen across real matches.
- **Refinement:** every file was read as `<commit>:<path>` so the mutable Cop working
  tree could not contaminate the review.
- **Lesson:** review an immutable commit, never a working tree; and credit real progress
  explicitly, so a NO-GO verdict stays about the remaining defect rather than reading as
  blanket rejection.

## P-013 — Coordinator NO verdict and the role-alternation reversal

- **Date:** 2026-07-28 · **Tool:** Claude Sonnet 4.6 (agentic CLI)
- **Goal:** absorb the coordinator's `ACCEPTED_FOR_PROVISIONAL_PARITY: NO` and correct an
  overclaim the Thief had made one commit earlier.
- **Prompt (essence):** record the verdict authoritatively and propagate it across every
  gate document.
- **Output:** `COORDINATOR_VERDICT_2026-07-28.md` plus propagation through `PLAN.md`,
  `TODO.md`, `CONTRACT_HANDOFF_CHECKLIST.md`, `CONTRACT_REVIEW.md`, and
  `GATE_RESOLUTION_REVIEW.md`.
- **Refinement:** commit `cc78798` had just promoted six-sub-game role alternation to
  `CONFIRMED` from course material; commit `422643c` reverted it. `LS-001` returned to
  `UNKNOWN` and `U-021` was reopened, because the source was not an authenticated Moodle
  announcement or original lecturer message.
- **Lesson:** the sharpest failure mode is promoting a plausible claim to `CONFIRMED`
  from an unauthenticated source. Simulator behaviour plus convincing course text is
  still not lecturer confirmation, and a same-day reversal is cheaper than a contract
  built on the overclaim.

## P-014 — Option B decision and opening contract-independent M2

- **Date:** 2026-07-28 · **Tool:** Claude Sonnet 4.6 (agentic CLI)
- **Goal:** find work that could legitimately proceed while the contract gate stayed shut.
- **Prompt (essence):** record the Option B interoperability decision and open the domain
  work that depends on no shared-contract byte.
- **Output:** `OPTION_B_INTEROP_DECISION.md` pinned to simulator commit
  `960499fd…4677b54`, recording future endpoints and the commit-reveal shape as a
  decision only, with runtime explicitly deferred.
- **Refinement:** the M2 carve-out was justified against a specific test — it uses only
  Appendix E/F `CONFIRMED` rules and takes every board, barrier, and position input
  explicitly — rather than by general impatience.
- **Lesson:** a blocked gate does not block everything. Separating "depends on the
  contract" from "depends only on confirmed rules" converted a full stop into real
  progress, provided the boundary is stated and testable.

## P-015 — M2 core domain by TDD

- **Date:** 2026-07-28 · **Tool:** Claude Sonnet 4.6 (agentic CLI)
- **Goal:** implement coordinates, board, movement, barriers, and capture behind the SDK.
- **Prompt (essence):** build the domain in small red-green-refactor steps, one module per
  commit, gates green before each.
- **Output:** five commits producing `domain/` with immutable `Coordinate`/`Action`,
  origin-aware `Board`, barrier-aware movement, placement validation with the
  `DEFAULT_BARRIER_QUOTA = 14` minimum, and `evaluate_capture`; 92 tests at 99.25% branch
  coverage, re-exported through `p2p_thief_agent.sdk` per `PS-007`.
- **Refinement:** direction labels resolve per origin corner while orthogonal adjacency
  stays origin-independent, so barrier and trapping logic could not silently inherit a
  top-left assumption.
- **Lesson:** where a rule is confirmed but a convention is negotiated, make the
  convention an explicit input and keep the confirmed geometry independent of it.

## P-016 — Own-cell barrier correction

- **Date:** 2026-07-28 · **Tool:** Claude Sonnet 4.6 (agentic CLI)
- **Goal:** fix a barrier rule implemented more narrowly than the book allows.
- **Prompt (essence):** book Chapter 3.4 permits the Police to place a barrier on their
  own current cell or one orthogonally adjacent cell; correct the validator.
- **Output:** `validate_barrier_placement` accepts `target == police_position` or exactly
  one orthogonal step; the own-cell-rejection test was replaced by positive tests through
  both public APIs, keeping negative coverage for diagonal, multi-cell, off-board,
  duplicate, and quota-exhausted placement. `M2_DOMAIN.md` also recorded that barrier
  placement replaces movement, and downgraded capture-reason precedence to an explicitly
  implementation-chosen tie-break.
- **Refinement:** the same pass separated a confirmed rule (barrier replaces movement)
  from an invented one (capture precedence), instead of leaving both implicit.
- **Lesson:** when correcting a rule, re-audit the neighbouring claims written at the same
  time; an over-narrow reading rarely travels alone.

## P-017 — Review of Cop `0.2.0-proposed` and status reconciliation

- **Date:** 2026-07-28 · **Tool:** Claude Opus 5 (Claude Code)
- **Goal:** determine whether the newest 32-file Cop bundle resolves the seven coordinator
  blockers.
- **Prompt (essence):** "lets move forward with the project but dont make any assumption
  when ever you are uncertain ask me" — answered by asking which task to take and whether
  read-only access to the Cop repository was authorized, before touching anything.
- **Output:** integrity independently reproduced (32/32 file hashes, manifest self-hash,
  7/7 canonicalization vectors) but a NO-GO verdict: four of seven blockers unresolved,
  plus two new P0 defects — `SHARED_RULES.md` states a barrier rule contradicting both
  implementations, and the per-sub-game `links` pattern `g<NN>` is a placeholder used as a
  regex that rejects every real filename.
- **Refinement:** the vectors were re-derived in an independent implementation rather than
  read; that is what exposed the escaping gap and the Python-only canonicalization
  profile. The `g<NN>` defect was confirmed by running the pattern, not by reading it.
- **Lesson:** a clean manifest proves only that the declared bytes are the actual bytes.
  Executing a claimed rule finds defects that reading it does not.

## P-018 — Deterministic baseline strategy

- **Date:** 2026-07-28 · **Tool:** Claude Opus 5 (Claude Code)
- **Goal:** implement the contract-independent Thief policy permitted as a narrow
  exception.
- **Prompt (essence):** "lets move forward with the project and with the implementation
  but dont make any assumption when ever you are uncertain ask me", plus a mid-task
  instruction to commit as work landed rather than only at the end.
- **Output:** `strategy/metrics.py` and `strategy/baseline.py` behind the SDK, ranking
  candidates by strict criterion priority — discard dead ends, maximize threat distance,
  maximize mobility, maximize two-ply reach then minimize corner contact, fixed action
  order — across three commits; 139 tests at 99.36% branch coverage.
- **Refinement:** four design questions were put to the human first (branch base, threat
  input model, lexicographic versus weighted scoring, task scope). The first definition of
  "immediately trapping" proved nearly vacuous — the cell just vacated is always a legal
  way back — and was replaced by "every exit leads back to the origin". Two failing tests
  were found to encode wrong expectations and were corrected against the specified
  priority order rather than bending the policy.
- **Lesson:** lexicographic ranking beat a weighted sum precisely because no calibration
  data exists to justify weights. And when a test fails, decide whether the code or the
  expectation is wrong before changing either — here the policy was right twice.

---

> **Provenance note for P-019 … P-022.** Reconstructed on 2026-08-01 from the commit
> record, the documents each step produced, and the `Co-Authored-By` trailers, because
> the log had fallen behind between 2026-07-28 and 2026-08-01. Not transcribed from the
> original sessions: each "Prompt (essence)" records the evident task and the human's
> stated intent, not verbatim wording. P-023 onward were written in the sessions that
> performed them.

## P-019 — Replacing the copy model with a conformance model
- **Date:** 2026-07-28 · **Tool:** Claude (agentic CLI) · *reconstructed*
- **Goal:** decide what M1 actually has to prove, after a coordinator verdict rejected the previous premise.
- **Prompt (essence):** record the coordinator's `NO` verdict, revert the role-alternation claim it rejected, and stop treating byte-parity with the companion repository as the goal.
- **Output:** `THIEF-002` recorded as development-time independence from the Cop repository; the copy model superseded by an interoperability conformance model; the M2 domain built under the same contract-independent authorization; the deterministic Thief baseline strategy behind the SDK.
- **Refinement:** the reasoning that settled it: league play is against **unknown classmates**, so matching one companion repository byte-for-byte is evidence about that repository only. The Thief therefore authors its own wire profile and must prove itself against something neutral.
- **Lesson:** matching one specific peer is not interoperability. A conformance gate has to be defined against a spec and an independent stub, or it only ever proves that two copies of the same assumption agree.

## P-020 — Building the book's wire, then removing it
- **Date:** 2026-07-28 → 2026-07-29 · **Tool:** Claude (agentic CLI) · *reconstructed*
- **Goal:** implement the book's commit-reveal flow literally, including its live third phase.
- **Prompt (essence):** follow the coordinator's ruling and adopt the book's construction — rename the turn tool to `receive_move` and add the live `receive_reveal` step the book's figure 6 describes.
- **Output:** the book construction adopted, the tool renamed, `receive_reveal` implemented, live-reveal capability required in the profile, and commit-to-reveal ordering enforced before audit. Then, on receiving authoritative wire answers, **all of it was withdrawn**: the tool reverted to `receive_turn` and the live reveal was removed.
- **Refinement:** the withdrawal was not a partial edit. The whole Option-B protocol layer was replaced by the simulator wire in one deliberate commit, with the superseded modules, the Node stub, and the conformance tests written against the old profile archived rather than deleted, so the history stays inspectable.
- **Lesson:** the most expensive week of this project was spent implementing a documented flow that the wire does not use. The book describes what the protocol *means*; the reference shows what actually crosses the socket, and only the second one an opponent can observe. Ask the wire before building to it.

## P-021 — Re-aligning the protocol layer in six deliberate steps
- **Date:** 2026-07-29 · **Tool:** Claude (agentic CLI) · *reconstructed*
- **Goal:** move the entire protocol layer onto the simulator wire without losing reviewability.
- **Prompt (essence):** re-align commitment construction, message types, crypto, sealing, handshake, and outcome mapping to the simulator, one reviewable commit each.
- **Output:** six numbered commits (`M4 re-align 1/6` … `6/6`) followed by the breaking replacement commit, plus `SIM_WIRE_PROTOCOL.md` as the authoritative record and the lecturer's answers closing `U-021` and `U-014`.
- **Refinement:** numbering the commits `n/6` in advance made an eight-commit rewrite reviewable in pieces and made it obvious if a step was skipped.
- **Lesson:** a breaking change is safer as a labelled sequence than as one large commit — and archiving the superseded layer costs nothing next to the ability to answer "what did we used to do, and why did we stop?"

## P-022 — Reconciling the documents with the re-alignment
- **Date:** 2026-07-31 · **Tool:** Claude (agentic CLI) · *reconstructed*
- **Goal:** find every document still describing the world before the wire re-alignment.
- **Prompt (essence):** check both repositories deeply against the instruction documents; the lecturer will not forgive missing points.
- **Output:** eight documents corrected; the M5 tool name fixed from the withdrawn `receive_move` back to `receive_turn`; the wire pinned to real reference output; Stage C conformance-profile acceptance recorded; `M5-002` adapters and the stage-2 localhost milestone closed.
- **Refinement:** the tool-name defect is the one worth remembering — a build instruction still said `receive_move` while the repository's own specification said `receive_turn`. Two agents built to those two documents would have been unable to connect at all.
- **Lesson:** a refactor is not finished when the tests pass. Documents that outlive a decision will be followed by whoever reads them next, and a stale build instruction is executable in the worst sense.

## P-023 — Closing the private-configuration boundary and the agreement gate
- **Date:** 2026-08-01 · **Tool:** Claude Opus 5 (agentic CLI) + NotebookLM
- **Goal:** `M5-002f` and `M5-014` — where the opponent's address comes from, and whether
  this peer will agree to play at all.
- **Prompt (essence):** "continue to work according to the unDone TODO file in 2 repos,
  and according to the 2 links in the notebookLM (please keep in touch with them and
  always ask them), and also according to the md files under `inst`".
- **Output:** `shared/private_config.py` reads `[network].opponent_url` from one explicit
  private TOML path and is the only door to an opponent address; `assert_no_network_address`
  is the lock on the other, refusing a shared match object that carries an address by
  member **name** or by **value**. `protocol/agreement.py` decides whether to play —
  signature, required terms, Appendix F floors, then every term compared against our own,
  refusing **by name** — and is wired into the live `InboundPeer` handler rather than left
  as an unused module.
- **Refinement:** the reference was consulted before writing, which settled the section and
  key names, the separate `config/police/` and `config/thief/` directories, and a flat "no"
  to whether the shared JSON ever carries a network address. That closed keys `ADR-0004`
  had left `PENDING`.
- **Lesson:** two checks, not one. A leak guard that only matches member *names* is evaded
  by renaming the key; one that only matches *values* is evaded by an unusual format. Either
  alone reads as thorough and is not.

## P-024 — A required term that would have refused the lecturer's own template
- **Date:** 2026-08-01 · **Tool:** Claude Opus 5 (agentic CLI) + NotebookLM (both notebooks)
- **Goal:** settle whether `min_center_intensity` belongs in the required agreed terms.
- **Prompt (essence):** "check the second notebook. always check in both of them when needed."
- **Output:** the book PDF's Appendix F table 16 has exactly three rows, all `Fixed`, and
  **no** minimum-centre row; the lecturer's own `agreed-config` template carries the same
  three keys and no fourth. This repository listed the term in `REQUIRED_TERMS`, so it would
  have rejected the very configuration template teams are meant to share, reporting it as a
  missing agreed term. Removed from `REQUIRED_TERMS`, kept in `AGREEMENT_TERMS` so it is
  still compared when a peer sends it, and pinned by a regression test.
- **Refinement:** the pinned simulator *does* require the key and its own config carries it,
  which is why the wrong reading looked defensible. The source-of-truth order decided it: a
  simulator behaviour contradicting both the book and the lecturer's template is not authority.
- **Lesson:** the constant had been written once, exported, and called by **no decision path**,
  so no test could catch it — it only became visible when wired into a live refusal. A constant
  that claims to encode a rule should be pinned to the document that states the rule.

## P-025 — Auditing the documents against what was actually built
- **Date:** 2026-08-01 · **Tool:** Claude Opus 5 (agentic CLI)
- **Goal:** check every `docs/` file for claims the code had outgrown.
- **Prompt (essence):** "before this check if you updated all the md files under `docs` folder
  in both repos" — then, separately, whether the prompt log and README report sections were
  being kept current.
- **Output:** across both repositories seven documents were stale. `PRD_p2p_mcp` listed built
  features as "not yet built"; both `PLAN` files marked M5 untouched; `ADR-0004` still called
  the private keys open; the README still required Python 3.10. Recorded `C-022`: the book's
  per-turn `Reveal` phase says peers exchange the actual move, while the wire reference sends
  none — move, true position, verdict, and nonce stay private until the audit.
- **Refinement:** the audit was run as a grep for *claims of absence* ("not yet built", "does
  not exist", "still absent") rather than by re-reading every file, which found the stale rows
  directly. Hardcoded totals were replaced with durable statements rather than fresh numbers.
- **Lesson:** documents rot silently in the direction of *understating* progress, and a
  correction applied to a code docstring does not propagate to the document of record — in the
  companion repository an ADR still carried a claim its own code had already retracted.

## P-026 — Bringing the Thief level, and a defect the phase machine caught
- **Date:** 2026-08-01 · **Tool:** Claude Opus 5 (agentic CLI) + NotebookLM
- **Goal:** `M5-007` — the declared phase machine, the turn loop, and a whole sub-game, matching the companion peer's capability without copying it.
- **Prompt (essence):** bring the Thief level with the Cop, the same way; then a challenge asking whether the notebooks and `inst/` had really been consulted and every document updated.
- **Output:** `orchestration/` with the phase machine, `run_turn`, and `run_sub_game_over_wire`, plus a sub-game and audit crossing a real socket into a separate process. Two behaviours are genuinely **not** the Cop's mirror: this peer **opens**, because the book gives the Thief the first move of every cycle and a Thief that waited would deadlock against a Cop correctly waiting for it; and a `capture_claim` is **checked against local truth, never believed**, because the Thief is the peer that knows where it stood.
- **Refinement:** building the second implementation exposed a real defect in the first. Deciding and sealing sat inside `COMMITTING`, but the declared table gives `COMMITTING` exactly one exit, so a seal failure had **no legal transition** and stranded the machine mid-turn. The Thief's stricter version called `fail()` and the phase machine **refused it** — the machine caught the design error, which is the argument for having one. Both peers were corrected. Two test expectations also proved wrong rather than the code: because this peer opens, the opponent's messages land one turn later than their own numbering suggests.
- **Lesson:** re-deriving rather than copying is not ceremony — it is how the asymmetries surface. A mirrored Thief would have waited on step 1 and deadlocked, and would have trusted a claim it was uniquely able to check.

## P-027 — Deadlines and bounded retry
- **Date:** 2026-08-01 · **Tool:** Claude Opus 5 (agentic CLI) + NotebookLM (both notebooks)
- **Goal:** `M5-004a`/`M5-004b` — bound every wait so the peer cannot freeze.
- **Prompt (essence):** run the full eight-step workflow for the next feature in both ledgers.
- **Output:** `services/deadlines.py` — an injected-time `Deadline`, a `RetryPolicy` read from the shared signed match object, and `attempt`, which gives each try its own expiry and raises rather than quietly giving up. A slow attempt that overruns its own expiry is **not** retried: the retry budget does not rescue a missed deadline.
- **Refinement:** the reference supplied the exact key names and defaults, and all four turned out to already exist in the agreed match object — so this was reading agreed values, not inventing new ones. The book PDF added that table 19 marks the watchdog timeout `Negotiation` while the retry limits are `Minimum`, which the parameter baseline had not distinguished.
- **Lesson:** the limits belonging to the **signed** match object rather than private config is the point — a peer that could set its own timeout could stall an opponent legitimately. Reading them from the agreed bytes makes that impossible rather than merely impolite.
