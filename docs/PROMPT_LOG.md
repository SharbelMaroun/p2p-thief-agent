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

- **Date:** 2026-08-06 · **Tool:** Claude Opus 5 (agentic CLI) · **NotebookLM: BOTH notebooks reached** · **Companion-repository batch (docs only; no Thief code written)**
- **Goal:** carry the replay-verifier findings into this repository. The Cop repository built its verifier this session; this repository's `M8-002` family stays PENDING, but the *sources* the batch settled bind both sides equally and leaving them unrecorded here is how the two repositories drift.
- **Notebooks (step 3):** the **book** answered that rule 20's sanction is a "**Threshold condition** for confirmation of logs and submission of the project" (p. 129/272) — the project cannot be accepted without a replay app, which makes `M8-002` the highest-consequence row left here. It also confirmed rule 36's "comprehensive mutual log audit" (p. 131/276) and p. 39/102's "each side reconstructs the opponent's data through the revealed nonces", so verifying an **opponent's** log is mandatory, not optional. The **reference** described its own viewer: `src/police_thief/gui/replay.py`, `verify_record` in `gui/replay_data.py`, and an auto-located opponent log path.
- **Output:** `docs/PRD_replay.md` re-authored — its two stated blockers (ADR-0006 canonicalization, ADR-0003 schema versions) are no longer blockers, and the settled requirements are written out with citations. `docs/SPECIFICATION_CONFLICTS.md`: `C-016` reclassified.
- **Correction made:** `C-016` recorded the ch. 7 vs ch. 5 hash constructions as an open **CONFLICT**. `:1757` (p. 58/146) resolves it in the book's own voice — "the sketch simplified the input for the sake of the illustration; in practice the signature covers all components of the step — Intent, Move, State and Nonce — as detailed in the protocol in Chapter 5". Reclassified **RESOLVED**; the required action (build from `protocol/crypto.py`, never the ch. 7 sketch) is unchanged. The Sources column now cites p. 58/146.
- **Carried finding worth acting on when `M8-002` is built:** a digest check alone is not sufficient. A record's *visible* `step` and `move` are not covered by the commitment, so a forger can leave the sealed payload intact, rewrite only what the board displays, and collect a green stamp over a game nobody played. This was a real hole in the companion implementation, found by a foreign-log test. `:1691` requires the viewer to re-encode "the Nonce and the move **appearing in the log**", so the visible fields must be cross-checked against the sealed payload. Recorded in the acceptance criteria.
- **Method note:** this entry exists because "Cop-only work" is not an exemption from the both-repositories steps. On 2026-08-06 eight consecutive batches skipped them and two later batches had to rediscover this repository's state from scratch.

- **Date:** 2026-08-06 · **Tool:** Claude Opus 5 (agentic CLI) · **NotebookLM: BOTH notebooks reached** (the code notebook took 6 attempts) · **Rows CLAIMED in `TODO.md` and pushed before starting**
- **Goal:** the replay verifier — first M8 work in this repository, which stood at 0/58. Rule 20's sanction is a "threshold condition for confirmation of logs and submission of the project" (p.129/272), so a repository with no replay application fails a threshold rather than losing a mark.
- **Re-authored, never copied.** `THIEF-002` forbids reading the companion repository, and the rule earned its keep again: this repository's `protocol.crypto.verify` **raises** where the companion's returns a flag, and its commit is `sha256(f"{canonical_json}|{nonce}")` built from a string rather than concatenated bytes. A copy would have swallowed both.
- **Notebooks (step 3):** the **book** settled the sanction structure — rule 19 is "any mismatch **in the digest**" (p.129/271), while a missing step is "contradictory reports" under rule 35 (p.131/275) and an illegal state jump under rule 5; and it said detecting a reorder is **not explicitly required**. The **reference** confirmed it checks no sequence at all: `verify_record` verifies each record "with no reference to its place in the sequence", `normalize_log` neither sorts nor re-indexes, no code rejects a duplicate or missing step; step sequence there is *passive*, each step "a cryptographic island". Verified in `inst/` (step 4) including `DEV-SPEC.md`.
- **Output:** `src/p2p_thief_agent/replay/` — `load.py`, `verify.py`, `sequence.py`, `cursor.py` — at **100% branch**, with five test modules including a foreign-log writer that imports nothing from this package. 927 pass, 99.45%. Eleven rows DONE; M8 moves 0 → 11 of 58.
- **`sequence.py` has no companion original.** It answers `M8-008d` by detecting reordered, deleted and duplicated records — which every digest survives — and deliberately **reports rather than banners** them. Folding them into the verdict would apply the wrong sanction and would red-banner an opponent whose log is merely ordered differently, a false accusation with "no appeal process" (`:1769`). Recorded as `U-026`. The companion repository was missing this entirely and has now been fixed from the same finding.
- **`C-016` reclassified** CONFLICT → RESOLVED: `:1757` footnotes the ch. 7 sketch in the book's own voice as "simplified … for the sake of the illustration", naming Chapter 5 normative, and `DEV-SPEC.md:435` annotates its copy the same way. `M8-002d` is closed by `test_replay_authority.py`, which pins both differences (argument order *and* payload-versus-bare-move) separately so a future half-correction still fails.
- **Problem hit — the code notebook refused questions for five attempts** across three tab instances including a fresh one, with no error shown. The cause was not quota: the `type` action times out on long strings and leaves the box **empty**, so `Enter` submits nothing. Chunked typing works. The failure is indistinguishable from a server-side block, which is why it cost five attempts.
- **Method note:** this batch was restarted from step 1 after an earlier attempt stalled at step 3 with the notebook unreachable. Steps 5–7 were not begun until step 3 actually succeeded.

- **Date:** 2026-08-06 · **Tool:** Claude Opus 5 (agentic CLI) · **NotebookLM: BOTH notebooks reached** · **Rows CLAIMED and pushed before starting**
- **Goal:** the replay *view* and the submission screenshots. `M8-002`, `M8-002e`, `M8-006` a/c, `M8-008b`, `M8-015` b–d.
- **Notebooks (step 3):** the **book** listed the required screen elements — `nonce`, `move` and original `commit` per entry (p.56/142), a verdict indicator, and controls to move "back and forth in time" (p.56/141) — and said the **board is not required**. It also settled that only **`Verified OK`** is a mandatory capture, that the book **does not specify whose log** the screenshot shows, and that **`assets/` is not mandated**: the requirement is only that the images "be displayed within the README.md academic report" (p.81/189). The **reference** gave the widget layout and its boundary — dumb widgets handed "dictionaries of ready-made strings" — plus its palette and a **per-step** verdict recomputed on each advance. Verified in `inst/` (step 4) including `DEV-SPEC.md`.
- **Output:** `replay/view_model.py` at **100% branch**, `ui/replay_app.py` (coverage-omitted per `M8-006c`), two committed fixtures, `scripts/capture_replay_screenshots.py`, and both images embedded in the README report. 940 pass, 99.46%.
- **Re-authored, not copied** (`THIEF-002`). The view-model is built on this repository's own `replay` package, whose `verify` raises rather than returning a flag — which shows up in the pictures: this repository's `TAMPERED` capture carries the expected-versus-recomputed digests in its reason line, where the companion's says only that the digest did not match. Same requirement, two genuinely different screens.
- **Problem hit — the first captures were shifted**, desktop visible along one edge and the title bar along the top: Tk reports logical pixels while the Windows GDI works in physical ones, so on a scaled display every window coordinate is off by the scale factor. `SetProcessDpiAwareness` fixes it, and that is what makes `M8-015d`'s "a grader can regenerate them" hold on a different machine rather than only on this one.
- **A deliberate refusal:** the capture drives the real widget tree and fails loudly rather than drawing a picture of what the app would look like. A rendered image would satisfy the row while being a fabricated exhibit — the one thing a verification screenshot must never be.
- **Recorded as choices, not requirements:** the `assets/` location, the `TAMPERED` capture, and showing our own log rather than an opponent's. All three were assumptions before step 3; the book leaves all three open.

- **Date:** 2026-08-06 · **Tool:** Claude Opus 5 (agentic CLI) · **NotebookLM: BOTH notebooks reached** · **Rows CLAIMED and pushed before starting**
- **Goal:** the live GUI and the belief-map screenshot. `M8-001` a–d, `M8-015a`, `M8-006b`, `M8-007` a–c, `M8-011` a/b.
- **Notebooks (step 3):** the **book** gave rules 8 and 9 verbatim — the second carrying **project disqualification** — and settled that the live GUI may never show the opponent's true position **even after the audit reveal**, when this process legitimately knows it; the replay viewer is where that belongs. Locking is mandatory ("the interface enforces the lock"), Figure 9 supplies the labels, and the belief-map screenshot **must come from a live match** rather than a reconstructed state. The **reference** supplied the structural pattern: a snapshot function fixes what crosses to the GUI, so the opponent's position "is not part of the View object". Verified in `inst/` (step 4) at `:3311`, `:3312`, `:1647`, `:1669`.
- **Output:** `live/local_truth.py` + `live/view_model.py` at **100% branch**, `ui/live_app.py` (coverage-omitted), `scripts/capture_live_gui_screenshot.py`, `assets/live-gui-belief-map.png` in the README. 970 pass, 99.4%. Fourteen rows DONE; M8 is 35/58.
- **Re-authored, and the roles invert (`THIEF-002`).** Our own marker is `T`; the inference is about the police and reads `C?`. A copy of the companion repository's screen would label our own cell `C` and guess at a thief — backwards in a way that looks correct at a glance. The belief is also a **matrix** here (`perception.belief` works in `Sequence[Sequence[float]]`) rather than a cell map, so `LocalTruth.probability` indexes rows and tolerates a short or ragged matrix instead of assuming a dict.
- **`M8-001d` is enforced by the type, not by care.** `LocalTruth` has a closed field set built from explicit keyword arguments; `test_local_truth_boundary.py` fails if a field is added or if the live package imports anything that knows an objective coordinate. Rule 9 costs the project rather than a game, the failure would be silent, and no screenshot taken afterwards can prove what was on screen during the match.
- **The capture drives a real match** — a second operating-system process, turns over a socket, and the returned scent folded into a real belief matrix. A hand-built snapshot would have been quicker and would have been an illustration rather than evidence.
- **Carried finding:** belief converges within a few updates because scent carries no bluff, so a capture taken late shows one red cell and sixty-three reading `<1%`. Captured at step 2, where the map still shows an inference in progress. Rounding those small values to `0%` would print a board claiming the police are nowhere, so the label degrades to `<1%` instead.

- **Date:** 2026-08-07 · **Tool:** Claude Opus 5 (agentic CLI) · **NotebookLM: BOTH notebooks reached** · **Rows CLAIMED and pushed before starting**
- **Goal:** first M9 work — parameter research, statistics and charts. `M9-006` a–c, `M9-007` a/b.
- **Notebooks (step 3):** the **book** named the mandated artifact as a **Markdown** research report (p.142/265), not a notebook, and set the standard — "based on numbers and not on guesses" (p.142/266). It defined Appendix F's statuses, which fixed the sweep ranges to *upward from each Minimum*, and confirmed learning curves are RL-conditional with no substitute specified. The **reference** described its own aggregation path (`run_series`, and an in-process `FakeTransport`). Verified in `inst/` (step 4), including guidelines §9.1–§9.3 and the Fixed/Minimum/Negotiation split.
- **Output:** `analysis/` at **100% branch**, `scripts/run_experiments.py` + `render_charts.py`, 3 result files, 6 SVG charts, the mandated report. 995 pass, 99.4%.
- **THE FINDING: `M6-015`'s acceptance criterion measures a quantity the game does not score.** The shipped test asserts belief-driven evasion beats the blind baseline on **total survival steps** over four fixed openings — 125 to 52, and true. Widened to all 24 perimeter openings the steps advantage narrows to 1.51×, and under Appendix F's actual scoring (10 for reaching the threshold, 5 for capture, both `Fixed`, nothing in between) the ranking **reverses**: blind 175, belief 140. The blind arm is bimodal — 11 outright escapes, the rest caught in 2–7 turns — while belief is consistent (median 29, stdev halved) but escapes only 4 times. Paired, belief wins 13 and **loses 11**.
- **Not patched.** Opened as `M6-015c` with the evidence attached. Changing a strategy on the basis of one deterministic Cop on one board would be exactly the "guess" the book's standard forbids; what the measurement supports is that the *criterion* is wrong, not that the *strategy* is.
- **Why the scenario set was widened rather than repeated.** This harness is fully deterministic, so running it forty times returns the identical answer forty times. That inflates `n` without adding a single bit of evidence — the one way a run count can lie, and precisely the failure `M9-006c` ("run counts, not anecdotes") is guarding against. Enumerating the perimeter is a genuinely larger sample.
- **Re-authored, not copied** (`THIEF-002`). The statistics module pairs on *scenarios* rather than seeds because there is no randomness here, and the whole report is in survival rather than capture. The companion repository measured the **scored** quantity from the start and its claim stands; this one measured steps. Same project, two choices, and only one of them was right — which is the finding above.

- **Date:** 2026-08-07 · **Tool:** Claude Opus 5 (agentic CLI) · **NotebookLM: BOTH notebooks reached** · **Rows CLAIMED and pushed before starting**
- **Goal:** the security block — `M8-009` a/c/d. The fault-rehearsal rows (`M8-005`, `M8-013`) stay open; see below.
- **Notebooks (step 3):** the **book** confirmed **rule 25 is a Recommendation with no mandatory sanction** — a reading this repository's README already carried (`AE-025`) and which is now backed by the quote. It gave Table 2's technical-loss row as `0 | 0` and the full forbidden-field list. The **reference** gave the pattern: the move is chosen in pure Python *before* the model is called, so no path exists rather than none being taken. Verified in `inst/` (step 4).
- **Output:** `test_llm_move_boundary.py`, `test_artifact_secrets.py`. 1013 pass, 99.52%. Four rows DONE.
- **The layout made `M8-009d` easy to state and hard to break.** Move deciders live in `strategy/`, the language layer is a separate top-level `verbal/` package, so the assertion is a transitive closure between two packages rather than a rule about file names. The **reverse** direction is asserted too, for a different reason: if hint generation imported the evasion policy it could *report* the intended move, and rule 26 confines the verbal channel to natural language.
- **`M8-009a` scans the built product, not the tree.** The artifacts are generated at runtime and then leave the machine, so a secret in one would never be committed and the repository scanner would pass. Built with the real builders — and the fixtures deliberately carry repository URLs, an MCP server map, a model name and a signature, which are the fields most likely to smuggle something.
- **Left open honestly:** `M8-009b` (no private field crosses the wire) — this repository already has `protocol/config_integrity.check_no_private_fields`, so the row needs the wire-level test wired to it rather than new machinery; and `M8-005`/`M8-013` a–c, the fault rehearsals, which need the companion's failure-matrix treatment re-authored here.

- **Date:** 2026-08-07 · **Tool:** Claude Opus 5 (agentic CLI) · **NotebookLM: BOTH notebooks reached** · **Row claimed and pushed before starting**
- **Goal:** finish `M8-009b` — "confirm no private field crosses the wire", condition "leakage vector per private field class".
- **This repository already had half the answer, and the half it had was wrong for every other channel.** `config_integrity.check_no_private_fields` correctly refuses any private field in the **shared config**. Run over a legitimate *declaration* group it refuses that too — `['llm:llm_model']` — but rule 24 and `:2229` make `llm_model` **mandatory** there. One guard cannot serve both.
- **Notebooks (step 3):** the **book** gave the declaration's required disclosure list per group and the never-shared list (`my_port`, `thief_class`/`police_class`, LLM `provider`, `step_deadline_seconds`, `recipient`), plus the turn message's contents. The **reference** confirmed it from code and supplied the deciding detail: `mcp_servers` URLs contain the local port, so the matcher had to work on **keys, not values**, or it would refuse the mandatory disclosure. Verified in `inst/` (step 4) at `:2897`, `:2901`, rule 2.
- **Output:** `protocol/outbound_fields.py` at **100% branch**, `test_outbound_fields.py` with one vector per class per channel. 1035 pass, 99.53%.
- **Extends `config_integrity` rather than restating it.** Two lists of private keys would drift, and the drift would stay silent until a match was already disqualified — so the classes are merged at runtime and a test asserts every key the original guard knew is still caught.
- **Both guards are pinned as correct-for-their-channel**, deliberately: `check_no_private_fields` is right for the shared config and wrong for the declaration, and a test asserts both statements so neither gets "fixed" into agreeing with the other.
- **Gate findings fixed the designed way.** Ruff wanted the `Error` suffix. The secret scanner flagged the test vectors — correctly, since a key-shaped literal beside `api_key` is exactly what a leak looks like — so they now use the scanner's own placeholder convention instead of an allowlist entry that would weaken it permanently.

- **Date:** 2026-08-07 · **Tool:** Claude Opus 5 (agentic CLI) · **NotebookLM: BOTH notebooks reached** · **29 rows claimed and pushed before starting**
- **Goal:** finish M8. Seventeen rows here, twelve in the companion, taken as one batch.
- **Notebooks (step 3):** the **book** established that **rule 53 permits changing the code between games**, so `M8-014`'s freeze is a chosen policy scoped to the observable surface, not a rule; that **Nielsen comes from the guidelines §10.1, not the book**; the validation principle "never trust an unverified move" (p.12/50); and Table 19's five resource rows, all **Minimum** with `queue_depth` 100. The **reference** supplied the defect: its inbound queues are unbounded, bounded only outbound. Verified in `inst/` (step 4).
- **Output:** bounded mailboxes; `test_resource_endurance.py`; `test_inbound_validation.py`; `test_failure_matrix.py`; `test_profile_freeze.py` + a frozen record; `docs/INTERFACE_REVIEW.md`. 1089 pass, 99.31%. **M8 is 57/58.**
- **A real defect found by the field sweep: `ControlMessage.kind` was never validated.** `CONTROL_KINDS` was declared and never enforced, so an unrecognised kind reached the phase machine as a string nobody handled — and rule 5 makes an illegal state transition "a logical error leading to loss". `TurnMessage` validated its `sender` from the start; this class simply never got the matching check. A scenario test would not have found it; a systematic sweep of every field did.
- **The validation tests are re-authored, not mirrored, and the difference is the point.** The companion checks JSON Schema files; this repository uses dataclasses with an `_known_only` filter. That is a **stronger** guarantee and is now pinned as such: a schema can *reject* an unknown member, `_known_only` **drops** it, so a smuggled objective coordinate never reaches a constructor at all.
- **Both repositories independently froze the same wire digest** — `73c9963f…` — computed from two separately written neutral stubs. Agreement between two implementations is worth more than either freeze alone.
- **The interface review names three gaps** rather than claiming ten passes: no keyboard path, no error surface in the live GUI, and no undo anywhere — the last deliberate, since a committed move is cryptographically bound.

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

## P-028 — The Gatekeeper, and a word the ledger should not have claimed
- **Date:** 2026-08-01 - **Tool:** Claude Opus 5 (agentic CLI) + NotebookLM (both notebooks)
- **Goal:** `M5-003`/`M5-004f` - queue depth and the backpressure signal.
- **Prompt (essence):** run the full eight-step workflow for the next feature in both ledgers.
- **Output:** `services/gatekeeper.py`. The guidelines settled the design in one line - **"Overflow is queued, not rejected"** - which is the opposite of the usual instinct: a busy gate returns `False` and keeps the work, and only a genuinely full queue fails, loudly. `queue_status()` exists because the guidelines require a gatekeeper to expose depth and stats.
- **Refinement:** step 2 changed the plan before any code was written. Idempotency was already implemented - the receive-side intake had been deduplicating and rejecting replays since `M4-04` - so the feature narrowed to backpressure alone. The book then narrowed it further: chapter 9.3.1 aims the Gatekeeper at **outbound** Gmail and LLM calls to avoid a `429`, not at the inbound peer mailbox. Building it as an inbound queue would have been a plausible, useless answer.
- **Lesson:** the ledger's own row said "FIFO queue depth", and the book notebook marked FIFO **inferred, not stated**. The word was removed rather than kept, because a task title that cites book authority for something the book never says is how an invented requirement becomes permanent. Check the wording of the requirement, not just the requirement.

## P-029 — The Watchdog, and closing the M5-004 reliability set
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) — book PDF + reference sim (NotebookLM tool unavailable in this environment; coordinator authorized proceeding on the local authoritative sources instead)
- **Goal:** `M5-004c`/`M5-004d`/`M5-004e` — the system-wide freeze detector and the guarantee that a mid-turn disconnect terminates rather than hangs.
- **Prompt (essence):** synchronize with GitHub, verify the reported state, then continue real M5 runtime work in order.
- **Output:** `services/watchdog.py` — `Watchdog.check(now)` returns `ALIVE`/`SHUTDOWN`, trips on `elapsed > watchdog_timeout_sec` exactly as the book's §8.4.2 page-83 code does, and on a trip runs `persist_state()` **then** `controlled_shutdown()` once, fail-closed against a heartbeat arriving after teardown. Time is injected, so the freeze is proven by passing a number. `M5-004e` was proven at the loop level: a new `test_sub_game` case drives a dropped send from `AWAITING_REVEAL` to a terminal `Outcome.TECHNICAL_LOSS` whose audit is still built.
- **Refinement:** the reference simulator implements **no** watchdog at all — a book-mandated resilience pattern it skipped — so there is no wire or interop question here and the book is the sole authority. The boundary was taken from the book code verbatim (`elapsed > timeout`, so the exact threshold is still `ALIVE`), which deliberately differs from `Deadline`'s `>=`; each mechanism uses the comparison the book gives it. Teardown was placed in a `finally` so a controlled shutdown releases its connections even when persistence fails.
- **Lesson:** a subsystem the reference omits is not a licence to invent — it narrows the authority to exactly one source and makes matching it verbatim the safest defence. Most of `M5-004e` was already built by the turn loop and sub-game; the honest work was proving the awaiting-reveal path with a test, not rebuilding it.

## P-030 — Step-0 attestation: git commit, token budget, and pre-move ordering
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) — book PDF + reference sim (no NotebookLM tool; coordinator-authorized to use the local authoritative sources)
- **Goal:** `M4-006a`/`b`/`c` — seal the exact running git commit and the agreed LLM token budget before the first move, and make the pre-move ordering checkable.
- **Prompt (essence):** continue the M4 completion pass in ID order on the `Amr` branch.
- **Output:** `sealed_spec_record` now binds `github_commit` (`AE-53`) and `token_budget` (`AE-54`) into the step-0 commitment, refusing an empty commit or a nonsensical budget. `shared/git_info.running_git_commit` resolves the running HEAD through an injected runner, fail-closed on anything but a 40-hex SHA. `protocol/attestation.require_pregame_attestation` raises when a move (step ≥ 1) is sealed before the step-0 `system_spec` record — the ordering test rule 24 wants.
- **Refinement:** verified against the reference sim's `peer/sealing.py` — its step-0 seal carries spec/model/code_version/group/sub-game but **not** the git commit or token budget, so those two are book-mandated additions the sim omits, not a wire divergence (the opponent re-hashes whatever is revealed). Attempted to widen the public SDK surface with the new symbols, but that pushed `sdk/__init__.py` past the 150-line cap; reverted the SDK edits and kept the exports on `protocol/__init__`, where the tests already import them — the file-length gate caught the overreach.
- **Lesson:** "expose everything through the SDK" is not free — the line-count gate is a real constraint, and the honest move was to keep the surface where it belongs rather than pad the hub. The live wiring of the guard into the running sub-game is deferred to the M5 Step-0 runtime hook and recorded as such, rather than claimed here.

## P-031 — Finishing M4: adversarial vectors, constant-time compare, boundary guard
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) — book PDF + reference sim (no NotebookLM tool; coordinator-authorized local sources)
- **Goal:** close the remaining M4 gaps in ID order — `M4-008`, `M4-009a–e`, `M4-010a`, `M4-011a/b`, `M4-012`, `M4-013` — and reconcile the built-but-`PENDING` rows.
- **Prompt (essence):** continue working in order on `Amr`.
- **Output:** `crypto.verify` now compares digests with `hmac.compare_digest`, never `==` (`M4-012`, book §8). `test_audit_vectors.py` proves all five tampering classes are caught — mutated move, mutated intent, substituted nonce, single-byte change, and a renumbered/reordered step (the step is bound in the hashed payload, so order is irrelevant). `test_crypto.py` pins that two identical moves commit differently (`M4-010a`, `AE-18`). `test_protocol_boundary.py` walks `protocol/` and fails on any transport import (`M4-013`) and asserts `.gitattributes` pins `eol=lf` (`M4-011a`). `test_sdk.py` asserts the SDK reaches commit/seal/verify/audit/handshake (`M4-008`).
- **Refinement:** the reconciliation mattered as much as the code — eight M4 rows (`001`, `003`, `004`, `005`, `014`, `015`, `016`, `017`) were built and tested in earlier commits but left `PENDING` on a Stage-C gate that turned out to already be satisfied, so they were flipped to DONE with their existing test evidence rather than left to rot as false negatives. Formal M4 milestone closure was **not** self-issued — that stays the coordinator's verdict.
- **Lesson:** "detect a reordered step sequence" sounds like it needs an ordering check, but the honest answer is that binding the step index inside the commitment makes order un-forgeable — the test proves the property the design already had, rather than adding machinery for it.

## P-032 — The Log Manager subsystem, and two small M3 leftovers
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) — book + reference sim (no NotebookLM tool; local sources)
- **Goal:** `M5-008` (log manager) after clearing the in-order M3 leftovers `M3-005b`/`M3-008`.
- **Prompt (essence):** keep working in order on `Amr`.
- **Output:** `services/log_manager.py` — an append-only, per-match structured log recording sent/received messages, phase transitions, and commitments, with nonces withheld until `open_audit()` (`AE-18`). Append-only by construction: no edit/delete method, append-mode file, `entries` returns a copy; the file name carries the `game_uid` so matches never collide and a reopen appends rather than truncates. `record_transition` is shaped for `run_turn`'s `on_transition` hook. Also added the `M3-008` field-whitelist test (a Cop-truth field on `ThiefLocalState` now breaks the suite) and reconciled `M3-005b` (its boundary test already existed).
- **Refinement:** the reference sim has no dedicated Log Manager — it keeps a single in-memory `records` list written out at emit time, and that list holds only the peer's *own* sealed records. The book (ch. 9) wants sent *and* received messages logged for the mutual audit, so this is a book-driven subsystem, not a sim mirror. Discovered `services/__init__` had never exported the watchdog added earlier this session; fixed that omission alongside exporting the log manager.
- **Lesson:** exporting a subsystem is part of building it — the missing watchdog export would have surfaced only when something tried to import it from the package. Re-exporting each service as it lands keeps the boundary honest.

## P-033 — The orchestrator gateway and the five subsystem ports
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) — book + reference sim (no NotebookLM tool; local sources)
- **Goal:** `M5-001` — one gateway coordinating the five subsystems, with an import-graph guard and no decision logic in the gateway.
- **Prompt (essence):** keep working in order on `Amr`.
- **Output:** `orchestration/ports.py` defines the five ports (`DecisionModule`, `LogPort`, `DeadlineTracker`, `WatchdogPort`, and `PeerTransport` reused for the MCP connector); `orchestration/gateway.py` holds one of each and wires them — `on_transition` fans a phase out to the log and the watchdog, `play_sub_game` delegates every move to the Decision Module. A guard (`test_orchestrator_boundary.py`) walks `src/` and fails on any subsystem-to-subsystem import.
- **Refinement:** the guard immediately found a real violation — the Watchdog imported the Deadline Tracker for the shared limit reader. Rather than duplicate the reader or weaken the guard, the shared `read_limit` and the four reliability-limit constants were extracted into `services/limits.py`, which is infrastructure, not a subsystem, so both the Deadline Tracker and the Watchdog depend on it without depending on each other. The reference sim has no such gateway — its `PeerRuntime` is a monolith holding transport, state, belief, and rules together — so this is the book's ch.9 pattern, not a sim mirror.
- **Lesson:** the import-graph guard earned its place on the first run by catching a coupling that reads as harmless ("it's just a constant") but is exactly the peer-to-peer link the Orchestrator pattern exists to forbid. A boundary test is only worth having if it can fail; this one did, and the fix improved the design.

## P-034 — The Deadline Tracker subsystem
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) — book + reference sim (no NotebookLM tool; local sources)
- **Goal:** `M5-009` — track in-flight outbound requests, reap them on expiry, clear the queue on a technical loss.
- **Prompt (essence):** keep working in order on `Amr`.
- **Output:** `services/deadline_tracker.py` — `RequestTracker` registers each outbound request under a key with a deadline from the agreed limits, `reap(now)` removes and returns everything past expiry (a failure to act on, never awaited), and `clear()` drops every pending request cleanly when a technical loss is declared. It builds on the `Deadline`/`RetryPolicy` primitives — same subsystem, so no cross-subsystem import — and also satisfies the gateway's `DeadlineTracker` port. `test_deadline_tracker.py` (8 cases), injected time throughout.
- **Refinement:** kept the tracker distinct from the primitives rather than folding it into `deadlines.py`, which would have pushed that file past the 150-line cap. Extended the M5-001b import-graph guard to map `services.deadline_tracker` into the Deadline Tracker subsystem, so a future cross-import from it would still be caught rather than silently exempt.
- **Lesson:** adding a module to a subsystem means teaching the boundary guard about it — otherwise the new module is invisible to the check and a coupling could slip in unnoticed.

## P-035 — Opponent-rejection handling: retry transport, never a rejection
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) — book + reference sim (no NotebookLM tool; local sources)
- **Goal:** `M5-010` — a content rejection is scored, not retried forever, while a transport fault is retried.
- **Prompt (essence):** keep working in order on `Amr`.
- **Output:** `orchestration/delivery.deliver` retries only `TransportError` (bounded by the agreed policy) and lets `PeerRejectionError` propagate on the first occurrence, so a decided loss is never re-tried as a network blip. `test_delivery.py` proves both directions; a new `test_sub_game` case proves a rejection reaches a terminal `Outcome.TECHNICAL_LOSS` (`M5-010b`).
- **Refinement:** the distinction itself (disjoint `TransportError`/`PeerRejectionError`, `signals_refusal`) already existed in the client, and the turn loop already routed both to a terminal loss — so the genuine gap was the *retry asymmetry*, and only that was built. It was placed in the orchestration layer, not the MCP-connector subsystem: importing the retry primitive (`services.deadlines.attempt`) into `peer/` would have been a subsystem-to-subsystem link the M5-001b guard forbids. The gateway/orchestration layer is the correct home for coordinating the connector with the deadline policy.
- **Lesson:** the boundary guard shaped the design again — "where does retry-delivery live?" has one correct answer once you respect that the connector and the deadline tracker may only meet at the orchestrator.

## P-036 — Driving the mailbox: the loop this ledger never had a row for
- **Date:** 2026-08-02 · **Tool:** Claude Opus 5 (agentic CLI) · **NotebookLM: BOTH notebooks used**
- **Goal:** `M5-019` — the autonomous over-wire play loop, built symmetrically with the companion repo.
- **Prompt (essence):** work the eight-step process; pick up where the handoffs left off.
- **Notebooks (step 3, both, as required):** the *reference* notebook answered how a peer actually runs unattended — `cli.py` exposes `peer --role <thief|police>`; the FastMCP server is a passive mailbox; the driver is `PeerRuntime`, which **polls its own inboxes** at `[network].poll_interval_seconds` (0.5 s); the loop is verbatim `negotiate → turn loop (wait green → think → move → seal → send) → end-of-game audit`; `receive_turn` "does not compute the next turn; it only deposits the message"; and **the Thief moves first**, with the Cop choosing "immediately after the decoding of the incoming (hint) message". The *book* notebook answered what is required — section 8.3 mandates a strict **state machine**, not a bare polling loop; rule 6 verbatim "Mandatory to implement a deadline-tracking mechanism to prevent deadlocks while waiting for the opponent"; rule 7 a watchdog for process crashes; the loop must emit a heartbeat and on a missing pulse `persist_state()` then `controlled_shutdown()`.
- **Output:** `orchestration/polling.py` (`poll_for_turn`, `turn_receiver`) and `adapters.take_turn`; 24 tests across `test_polling.py`, `test_turn_receiver.py`, `test_take_turn.py`, `test_autonomous_play.py`. Both new source files at 100% branch. The end-to-end test plays a whole sub-game whose only turn source is the mailbox. 529 tests, 99.05% branch, all gates green.
- **Refinement:** the two notebooks appeared to disagree — the reference *polls* while the book mandates a *state machine* — and the resolution is that they answer different questions: polling is only how a queued message is picked up, while `PhaseMachine` still decides what may legally follow. The Thief case is the asymmetric one and was written down rather than assumed: this peer **opens**, so step 1 never waits and the poller becomes load-bearing from step 2 — the mirror-image mistake (a Thief that waits) deadlocks against a Cop correctly waiting for it, and the companion repo's harness had exactly that error before it was caught by a failing test.
- **What was NOT built, and why:** the `serve` CLI (`M5-019e`). `build_server(...).run()` blocks, so it needs a threaded server plus autonomous negotiation sequencing. A **passive** `serve` was rejected in the companion repo on 2026-08-01 as proving connectivity rather than a game; that decision is honoured here rather than quietly reversed, so the row is explicitly PENDING with its two remaining parts named.
- **Lesson:** this ledger had **no row at all** for the play loop — the companion repo named it only inside a blocked row's prose, and here it was named nowhere, so the single most load-bearing missing piece in the repo was invisible to any grep for open tasks. A gap described in prose is not a tracked gap, and a gap tracked in the *other* repo is not tracked here.

## P-037 — Ledger reconciliation: what was already done, and what only looked done
- **Date:** 2026-08-02 · **Tool:** Claude Opus 5 (agentic CLI) · **NotebookLM: not needed — no new behaviour**
- **Goal:** audit every open `M5` row against the code actually in the repository, on the suspicion that several were closed long ago and never recorded.
- **Prompt (essence):** clear the stale ledger, then build the `serve` CLI.
- **Output — two rows closed on evidence, four confirmed genuinely open:**
  - `M5-016` backpressure → **DONE**. `services/gatekeeper.py` plus nine tests, one of which (`test_a_full_queue_refuses_loudly_rather_than_discarding`) states this row's Definition of Done almost verbatim. Not one line of new code was needed.
  - `M5-012a`…`f` → **DONE / SUPERSEDED**. The parent `M5-012` was closed on 2026-08-01 and its sub-rows were left behind, still reading `PENDING` under a `DONE` parent.
  - `M5-011`, `M5-013a/b`, `M5-018` → **checked and confirmed open**, with the evidence of the check written into each row so nobody repeats it. `M5-011` is a *consolidation* task rather than new runtime code; `M5-018` is specifically the **SDK** boundary and is not the same guard as `M5-002b`.
- **Refinement:** the negative results were recorded as deliberately as the positive ones. I had guessed in conversation that `M5-011` and `M5-018` were probably already satisfied; both turned out to be real work, and saying so in the rows costs a sentence and saves the next session an hour. A reconciliation pass that only records the good news is how a ledger drifts in the *other* direction.
- **What was NOT done, and why:** the `serve` CLI. Step 3 of the standing process failed — the reference notebook would not accept a query across two attempts with a reload in between, the input clearing without submitting. The standing order is explicit that a tool failure is not permission to skip the step, so the feature was **not started**: no step 4, no implementation. Only this reconciliation, which needs no notebook because it records evidence already in the repository, went ahead.
- **Lesson:** "clear the stale rows" is worth doing on its own schedule, not only when something else is blocked — six rows were wrong in one direction or another, and every one of them would have misled a reader about what remained. But the reason it happened *today* is that a blocked feature left room for it, which is an argument for treating reconciliation as scheduled work rather than filler.

## P-038 — Launching a peer: the bind address that only fails on a second machine
- **Date:** 2026-08-02 · **Tool:** Claude Opus 5 (agentic CLI) · **NotebookLM: BOTH notebooks, different questions**
- **Goal:** `M5-019e` — host the mailbox as a long-running process and tolerate either start order.
- **Notebooks (step 3):** each was asked what only it could answer, rather than the same question twice. The **reference** (123 source files) gave the *code*: `start_peer_server` runs `server.run(...)` on a `daemon=True` thread after an `_ensure_port_free` pre-check, the CLI's `_run_peer_inner` does nothing but `SimulationSdk(...).run_peer(role)`, `connect_timeout_seconds` (60) / `retry_interval_seconds` (1.0) drive a connect-retry loop because "start order doesn't matter", and the runtime waits for the counter-signature before step 1. The **book** (PDF + four templates) gave the *authority*: rule 10 verbatim, the pre-game-declaration key set, and that Step-0 must be **exchanged and mutually signed**.
- **Output:** `adapters/serving.py` (`serve_in_background`, `ensure_port_free`, `port_answers`) and `services/readiness.py` (`wait_for_peer`), 18 tests, `ADR-0009`. 547 tests, 99.08% branch, all gates green.
- **Refinement:** the notebooks **disagreed**, and the disagreement was the whole value of asking both. The reference binds `127.0.0.1`; the book prints `host="0.0.0.0"` with the comment "so a tunnel can expose it publicly", and rule 10 sanctions failure to tunnel with "Inability to compete against opponents". The reference is not wrong — it runs both peers on one machine — but copying it would produce a peer that passes every local test and is invisible through the tunnel, failing only at the two-machine rehearsal where it reads as a network fault. The book outranks the simulator, so `DEFAULT_BIND_HOST` is `0.0.0.0` and a test pins it, because it is a one-word change nothing local would catch. Readiness was also kept deliberately separate from `deadlines`/`watchdog`: startup is the one phase where an unreachable peer is expected and harmless, and that leniency must not leak into the match, where rule 6 requires the opposite.
- **Problem hit:** the first `ensure_port_free` set `SO_REUSEADDR` on its probe socket out of habit, and the check silently never fired — on Windows that option lets a socket bind a port another process already holds, which is exactly what the function exists to detect. Caught by a test that held a port and asserted the raise. A detection probe wants the strictest bind available, not the most permissive.
- **What was NOT built:** `M5-019f`, the negotiation-to-first-move sequencing. A `serve` that comes up and mailboxes without playing is the passive server rejected on 2026-08-01, so no `serve` command is wired until that row closes. **Thief-specific:** once negotiation completes this peer must send step 1 without waiting, because it opens every cycle.
- **Lesson:** when the reference and the book disagree, the reference is usually solving a smaller problem — here, one machine instead of two. The hierarchy exists for exactly that case, and the tell is that the reference's choice is *convenient* rather than *wrong*.

## P-039 — The scent lock leaves the signed terms, and the unnamed ring becomes negotiated
- **Date:** 2026-08-05 · **Tool:** Claude Opus 5 (agentic CLI) · **NotebookLM: BOTH notebooks reached (Chrome extension)**
- **Goal:** close `U-025` — the eight `5x5` cells at squared distance 5 that book Figure 4 never names — and make the rule-23 lock something that survives contact with a real opponent.
- **Notebooks (step 3):** each was asked what only it could answer. The **reference** (123 source files) gave the code: scent lives in `src/police_thief/domain/smell.py` (`SmellField`, `deposit`, `snapshot`), it emits **all 25 cells** with its own tests asserting a snapshot length of 25, and it carries **no standalone scent hash** — the pheromone terms ride inside `config_sha256` over the whole terms dict, with `min_center_intensity` among them. The **book** notebook was asked what rule 23 requires and what Figure 4 actually prints.
- **Output:** `perception/scent.py` takes the ring as a validated parameter (`DEFAULT_OUTER_RING_DELTA`, no book authority); `perception/scent_lock.py` gains `scent_lock_fields`/`verify_peer_scent_lock` and drops `with_scent_lock`; `accept_offer(expected_scent_lock=…)` and `negotiate_match` publish and compare it. 27 tests; 774 pass, 99.63%.
- **Refinement — the previous design would have refused everyone.** `with_scent_lock` stamped the hash **into the signed terms**, and `differing_terms` compares the union of both key sets, so any opponent that did not send `scent_model_hash` was refused by name. The reference sends none. The lock therefore moved beside the terms and became lenient in one direction only: silence is accepted, a **differing** lock is refused. Rule 23 sanctions a deviation from the formula, not the absence of a message. The second change is that the lock now covers an **agreed** model rather than this peer's private constants — hashing a constant only proves we did not edit our own file.
- **Problem hit — the book notebook fabricated the emission table.** It reported that Figure 4 prints all 25 cells, with diagonals `0.42` and the unnamed ring `0.14`, and stated outright that no cell is unspecified. `inst/police_thief_p2p_Summary.md:947-955` contradicts every part: five classes, 17 cells, diagonals `0.20`. It had been asked explicitly not to infer or interpolate. Taking it would have overwritten a correct table in both repositories — and the tests would have been rewritten alongside it, so nothing would have caught it.
- **What was NOT changed:** `min_center_intensity`. The reference **requires** it and `validate_agreement` fail-fast aborts without it, while this peer still refuses an offer carrying it (`U-023`). That is a real mutual incompatibility with any simulator-built classmate, but it is a separate authority question and bundling it into a scent change would have buried it.
- **Lesson:** verifying a notebook answer against `inst/` is step 4 for a reason, and the reason is not thoroughness — it is that a wrong answer arrives in exactly the same confident shape as a right one. Beyond that: an unknown no source can answer is not a blocked task but a design input. `U-025` was never waiting on a ruling; the book had already said to negotiate the model and lock it.

---

## Closeout — what prompting actually taught this project (`M9-024`)

Written at the end of M9 rather than as a running note, because the pattern only became
visible across batches. Four lessons, each paid for.

**1. The eight-step method exists because skipping step 3 is invisible until it is expensive.**
The costly failures were never wrong code — they were work built on an assumption nobody had
checked. `M7-014c`'s base64url trap, Appendix F obligation 4, the fact that ISO/IEC 25010 is
not in the book at all: each came from asking, and none would have surfaced from reading our
own repository. The batch where I ran steps 3 and 4 once and then wrote three waves on that
one answer is the batch that shipped the shallow-clone false negative.

**2. A notebook answer is a lead, not a source.** Step 4 exists because the book notebook has
fabricated at least twice — an emission table that does not exist, and prose that contradicts
its own formula. The scent decay is the sharpest case: `inst/:930` says $(1-\rho)$ "reduces
by 90%" while the formula beside it retains 90%. Implementing the prose would have decayed
ten times too fast. Verifying against `inst/` caught it; trusting the summary would not have.

**3. Asking two notebooks different questions is worth more than asking one twice.** The book
answers *what is required*; the code notebook answers *what the reference does*. The most
useful findings came from the gap between them — the reference hard-codes `github_commit` to
`"unknown"` while rule 53 makes it Mandatory; the reference commits no artifacts while
Appendix F obligation 4 requires the config. Neither notebook could have told me that alone.

**4. The prompt that produced the most value was the shortest.** "in the commits you done,
there is a commit at least that faild the github actions." I had reported green twice from
local runs. That prompt found four red builds and, underneath them, a security gate reporting
"0 findings" on a shallow clone — 441 objects where a full clone has 1744. No amount of
elaborate instruction would have caught it; a direct challenge to a claim did.

**What I would tell the next person.** Ask the sources before writing, verify the answer
against the primary text before trusting it, and check the thing that reports success
actually looked at anything. Local green is not green.

## 2026-08-08 — "make them win": the live loop plays the measured policy at last

The prompt was "analyze how my cop and thief plays, and make them win in every game." The
analysis found the live adapter playing the **blind baseline** — no belief, no barriers,
empty `smell_grid`, `incoming` ignored — while every published number described a policy the
wire never ran. Worse were the two audit-fatal defects around capture claims: a default
`answer_claim` that denied every correct claim (a standing lie rule `[AE-021]` scores as a
forgery), and a timing hole where even an honest answerer would compare the claim against
the cell we had already fled to. Both are now closed from one shared closure, answered from
the pre-move cell, with `claim_response` on the wire the same turn.

Method note: the notebooks were asked *different* questions again (code: how the reference's
live brains choose moves; book: turn order, scoring rows, strategy restrictions), and the
book answer — simultaneous commit-reveal — reconciled with the lecturer's "Thief moves
first" as message order versus move resolution, recorded as `C-025` instead of being treated
as a contradiction. One measured reversal: Bayes-recursive belief calcifies on trail history
(the companion's grid lost a tracked target 40/40 → 0/40 on that change alone), so the live
loop rebuilds belief fresh per observation — which is exactly what the `M6-015` harness arm
measures, keeping the live policy and the published numbers the same object.

## 2026-08-08 (ii) — the sixth attempt: a negative result that finally localises the gap

Continuation of the "make them win" batch. Method first: both notebooks again, different
questions — the code notebook confirmed the reference never predicts or adapts ("deliberately
simple", students "expected to upgrade the strategy"), the book notebook confirmed adaptation
during play is permitted and *graded* (a success metric, p. 94/211) and that the audit
"verifies only that an agent kept its commitment... without limiting strategic freedom"
(pp. 38/101, 59/148). That cleared the design legally before a line was written.

The measurement discipline paid three times. Committing the pursuer archetypes (previously
scratch code) immediately corrected the published record — the committed herding/anticipating
are stronger, so shipped's honest row is 23/8/5, not 23/23/8. The grid then killed the sixth
attempt honestly (23/4/4 argmax-fed; worse with an uncertainty set; worse on robustness
configs). And the one probe worth all of it: truth-fed, the same machinery escapes **24/24
against every archetype** — so the planner is provably correct and the entire six-attempt
graveyard has a single measured cause, the estimator's ~1-cell error. Attempt #7 is therefore
perception (model-matched scent inversion), with a known measured prize.

Lesson recorded: **when an attempt fails, feed it truth before burying it.** Five previous
failures were buried with their mechanism unmeasured; the truth-fed probe cost two minutes and
converted failure #6 from "another dead heuristic" into the diagnosis that redirects #7.

## 2026-08-08 (iii) — attempt #7: invert the physics, bank the ceiling

Sharbel: "yes do attempt 7." Method held: both notebooks, different questions. The code
notebook revealed the reference's `BeliefGrid` runs diffuse-then-observe with a model-matched
smell step — which also explained *why* my earlier Bayes-recursion failed (I recursed without
the diffusion motion model). The book notebook confirmed the physics is a signed contract but
the inference engine is "a free strategic component expected of every team" (pp. 48/121,
94/211). Design followed authority, not the other way round.

The result is the cleanest of the project: the residual between consecutive observations is
exactly the newest emission stamp (non-negative terms, the clip never bites), so profile
matching localises the emitter with zero error for the true cell. Factorial grid: decoder
alone 18/24 vs anticipating, planner alone 4/24, **together 24/24/24 — 240 league points,
robustness included, equal to the truth-fed ceiling as a legal agent.** Six failed attempts,
one diagnostic, one fix.

Lesson: **the fix for a strategy problem was two layers below the strategy.** Six attempts
tuned the policy; the winning change never touched it. The diagnostic that redirected the
work (feed the failed thing truth) cost two minutes; the six policy attempts cost days.

## 2026-08-08 (iv) — "ok go": the first real match, and why rehearsals beat reasoning

The batch was the local two-process rehearsal. Method first: the code notebook supplied the
reference's exact offer roster (flat terms + identity + signature + nonce, **no config hash
on the wire**) — which dissolved the U-024-adjacent fear that our two repos' different
`config_sha256` conventions would refuse each other: neither needs to send one. The book
notebook drew the evidence boundary before we could over-claim: a localhost match is an
engineering rehearsal; the league requires "an accessible address, not only localhost"
(p. 97/215) plus the GUI/replay screenshots (p. 81/189).

Then the rehearsal found four bugs that fifteen hundred green tests had not: the playable
path skipped negotiation; the serve receive checked the inbox once instead of waiting; the
companion replied to a decided game (their survival, our technical loss, 0/0 on
reconciliation); and our local log hard-coded the winner. Every one was invisible to
single-process tests because each lives precisely in the seam between two processes that
no single test harness occupies. Static reading caught the first one before any run; the
other three each cost one run to name themselves.

Lesson: **a rehearsal is a test whose fixture is reality.** The final run — negotiated,
35 commit-reveal turns, both sides SURVIVAL at 35, `Verified OK — 35 steps re-verified` —
is worth more than any number this project has produced, because it is the first one an
opponent's machine helped compute.

## 2026-08-08 (v) — "go do 1 and 2 and 3": evidence, runbook, and the cross-check

The counted-game gap closed in three moves. The wire log now carries what negotiation
actually established (real opponent, real config lock, derived game id, sub-game number)
instead of placeholders — and the strongest moment of the batch was watching both
repositories derive the **same** game id (`game-9934e8338307`) from the same shared file
through two independently written canonical-JSON implementations. The match runbook
(`docs/MATCH_RUNBOOK.md`) is one page a classmate can follow cold; its troubleshooting
section is simply the list of our own rehearsal failures, which is what makes it credible.
And the final validation crossed implementations: the Cop's revealed log replayed
`Verified OK` under **this** repository's verifier — each side's cryptography checked by
the other side's tool, which is the audit model working exactly as the book intends.

Notebook discipline held: the code notebook supplied the reference's id-derivation and
log-naming conventions before we hardened ours; the book notebook supplied the match-day
duty list (Step-0, tunnels, history declaration, byte-identical lock; rule-51 report and
screenshots after) that became the runbook's skeleton, with the template's exact
summary-field roster — which caught one missing key (`audit`) in the Cop's new writer.

## 2026-08-08 (vi) — eleven games, and what process archaeology costs

The battery itself vindicated everything: 11/11 outcome agreement, 22/22 Verified OK,
a negotiated 50-step horizon honoured exactly, and the first wire capture (corner
start, turn 21) proving the claim path in the direction that used to carry a
hard-coded winner. The Thief escaped everything else, including a one-cell start —
it opens, and one step of head start against a barrier-dependent pursuer is decisive.

The operational lessons cost more than the games. Three, each paid for in reruns:
**killing a shell does not kill its children** — orphaned `tail -F` processes from
dead monitors held the progress log open for an hour of "file in use" mysteries;
**a detached process you lose track of keeps working** — a forgotten driver raced
the real battery and truncated its files, manufacturing impossible-looking evidence;
and **redirected stdout is block-buffered** — result markers only flushed at process
exit until PYTHONUNBUFFERED, so every wait read as a timeout. None of these is a
game bug; all of them are exactly the operational texture a league match-day has,
which is why the runbook now exists.

## 2026-08-08 (v) — the waller grid, and a boundary named honestly

Tournament hardening under the full eight-step gate. The blind spot was structural:
every pursuer ever measured here only moves, while the book arms the Police with
fourteen walls and two wall-capture rules. `scripts/experiment_wallers.py` closes the
blind spot; what it found is a boundary, and the honest record is the point.

Against the reference-shaped waller (greedy chase plus finishing walls) survival is
23/24 — a classmate bolting walls onto the default brain changes nothing. Against an
interception waller it is 8/24, and the number refused to move for three separately
designed and measured defenses: a wall-pressure guard leading the ranking, a regime
switch on the first disclosed wall, and risk-first promotion. Mechanism, not mystery:
the seal cascade fires at two exits, but an interceptor collapses the escape space
from beyond walling range — by the time any in-range refusal can act, the pocket is
shut. The companion repository proved the same theorem from the other side the same
day: its interception stack converts every evasion archetype 40/40. What shipped is
what measured well: the interceptor as a fourth plannable pursuer model, the graded
wall-pressure guard (free everywhere, decisive against lesser wallers), and the live
fail-safe that turns a strategy exception into a sealed STAY rather than a frozen
technical 0/0. The dead designs are recorded so nobody rebuilds them.

Process note: the first version of the ranking comment claimed the re-measurement
before it existed ("the waller conversions fell") — written prospectively, caught
against the grid, corrected to the measured truth. A comment that predicts a result
is an invented requirement wearing measurement's clothes.

## 2026-08-08 (vi) — the replay board, and our own log breaking our own viewer

GUI enhancement under the full gate (notebooks first: rule 9 binds the live interface
only, the replay is the "Retrospective Witness", and the reference's own viewer draws
both true positions from the two logs). The viewer now reconstructs the chase — fading
trails, barriers as placed, a ring on the cell we were caught on — with Play
auto-advance, and the screenshots are taken from the real rehearsal match, both logs
cross-loaded. The finding that outlives the feature: our OWN emitted log broke our own
row table and sequence checker, because both read step/sender/move at the record's top
level while the sealing keeps them in `payload` — every fixture had the flat shape, so
the defect was invisible until a real artifact arrived. Fixed with payload fallbacks;
the sender column now fills from the log's declared role.

Style addendum, same day: both windows moved onto a dark-navy chrome with glowing pill banners, rounded cells, and neon trails (`ui/style.py`) — pure tkinter, no theme dependency. The verdict colours and the heat ramp were deliberately left alone: reference-matched, test-pinned meaning is not styling. The styled replay window crossed the 150-line cap and split its evidence panels into `ui/replay_panels.py` rather than widening the gate.


## 2026-08-08 (v) — an external audit, and the documents that had rotted

**Prompt.** An independent examiner was asked to evaluate both repositories before submission
with a hostile brief: trust nothing either repo says about itself, reproduce every claim, hunt
Appendix E sanctions first, and find at least ten real problems. Then: fix them.

**What the gates said.** Everything declared passed: `uv sync --frozen`, `ruff` clean, 1591
tests at 95.58% branch, file lengths, secret scan over the tree and all 2050 history objects.
The contract checker correctly stayed fail-closed at `PENDING`. **No disqualification-level
violation** survived direct attack, and the commit-reveal and scent-lock digests reproduced
byte-identically against the companion — `416a57e1…` from both repositories independently.

**The reproduction that failed.** `results/strategy_comparison.json` claimed belief survival
125; re-running `run_comparison()` returned **140**. The code had improved (the `M6-032` wall
pressure term) and the committed result had not been regenerated — so the README quoted a
number the repository could no longer produce. Every other result file reproduced exactly,
which made the one that did not easy to see and easy to have missed.

**The section that argued against its own data.** README §4 still told the story of the metric
disagreement: belief losing the league on points, 140 against blind's 175, `M6-015c` opened as
an unresolved finding. That was corrected in the *research report* and the *academic report* on
2026-08-07 when the ranking fix landed — `results/strategy_arms.json` now carries
`metric_disagreement: false` and belief winning 235 to 175 — and the README section was simply
never brought along. Three documents told two different stories and the flag designed to catch
exactly this was already reading `false`.

**The chart that contradicted its own bars.** `chart-metric-disagreement.svg` was titled "The
two metrics rank the strategies in opposite directions" while drawing 235 against 175 in the
same direction. The title and caption were hard-coded strings in `render_charts.py`; they are
now **derived from the data** the bars come from, so the picture cannot disagree with itself
again.

**Overclaimed independence, corrected.** `THIEF-002` was written as "developed with no read and
no write access to the companion Cop repository". The discipline it describes is real and is
why the protocol and strategy layers genuinely diverge — but both repositories are written by
the same team and share about thirty support files, one of them byte-identical including its
dated discovery note. The rule that matters (rules 1 and 2) is about **run-time** separation
and is structurally enforced; the sentence was claiming something stronger and different.
`docs/SHARED_MATERIAL_AND_AUTHORSHIP.md` now itemises exactly what is shared, and `THIEF-002`
is restated as governing wire *inputs*.

**Lessons.** (1) *Regenerating results is not updating the report.* (2) *A conclusion written
into a chart title is a claim nothing re-checks* — compute it. (3) *When three documents cover
one finding, the one without a test is the one that rots.* (4) *State the discipline you
actually practise*; a stronger claim is not a safer one, because a grader reads what is written.


## 2026-08-08 (vi) — the audit's leftovers, and one finding the audit got wrong

**Prompt.** "Fix all the rest" — the smaller findings left open after the first audit pass:
a submission-tag test that could not fail, the missing §11 cost analysis, the `ast.Import` hole in the rule-8/9 boundary guards, and a `target-version` that disagreed with `requires-python`.

**The notebooks were asked first, and one answer retired a finding instead of closing it.**
The audit had flagged "no results-analysis notebook in either repository" against guidelines
§9.2. Asked directly, the book **does not require a Jupyter file**: it names the deliverable
`RESEARCH-REPORT-Performance-Analysis.md` under `/docs`, which is the file both repositories
already ship, and the pinned reference contains no notebook either — its analysis is markdown
plus plain Python. The finding was an **invented requirement**: a real rule read through the
word "notebook" rather than through what the source says the artifact is. It is now written
into the research report itself so nobody "fixes" it later by adding a file that satisfies
nothing. A reviewer who manufactures requirements wastes exactly the time the review cost.

**A test that switches itself off when the risk appears is worse than no test.**
`test_submission_tag.py` asserted `main() in (0, 1)` — true of any function returning an int
— and `isinstance(tag_exists(), bool)`. Worse, one case returned early the moment a tag
existed, so the suite went quiet at exactly the point the "tag names a commit nobody
reviewed" failure becomes possible. Rewritten to build **real throwaway Git repositories** and
drive the checker at every branch, including the correctly-tagged case the old suite could
never reach, plus one unconditional assertion that this repository is tagged and annotated.

**The boundary-guard hole is the most serious thing found today**, and it was in both
repositories. The walkers enforcing rules 8 and 9 — sanction: disqualification of the
*project* — matched only `ast.ImportFrom`, so a plain
`import p2p_thief_agent.orchestration as o` inside `live/` would have passed the one test that
exists to stop it. A guard that checks one of the two ways to write the same statement is not
a guard.

**The cost section was missing entirely, and the book wanted a different argument than
expected.** Rule 54's token figures were emitted, but guidelines §11 asks for a cost analysis
and there was none. Asked directly, for a zero-token agent the book does not want a fabricated
dollar table: it wants the **minimal-resources** case, because computational fairness is
graded — the book asks whether an agent on a phone races a workstation fairly. So §3.5 states
the zero-token position as a strategy, with what it costs (no rhetorical sophistication, no
claim to an LLM-driven strategy) rather than only what it saves.

**Fixing the lint target cost more than it looked.** `target-version = "py310"` against
`requires-python = ">=3.11"` was suppressing 8 real findings. All were fixed rather than
ignored; consolidating a `datetime` import kept `adapters/serve.py` inside the 150-line cap
instead of widening the gate to fit the change.


## 2026-08-08 (vii) — the scent kernel was wrong, and our own reading rule is why

**Prompt.** A classmate team's analysis of our repositories, forwarded by Amr, claimed our
5x5 emission kernel disagrees with theirs: diagonal `0.42` not `0.20`, mid-side `0.20` not
`0.14`, and the eight-cell ring `0.14` rather than a negotiated residual. Asked to check it
before changing anything.

**Three of their four claims did not survive checking.** Their `game_id`/`game_uid` finding
was wrong -- we do derive both deterministically in `adapters/serve.py`; they read the
`MatchIdentity` dataclass and not the call site. Their report-signature proposal (spaced
separators, a Hebrew consensus key) appears nowhere in the book and its spaced separators
would contradict the canonical-JSON rule the book *does* state, so it is one team's private
convention. Their open question -- whether a scent mismatch could surface as an audit hash
mismatch -- is answered by the code: `smell_grid` rides in the **public** turn fields, never
inside the sealed payload, so the worst case is a clean pre-game refusal, never a both-zero
audit.

**The fourth claim was right, and it was ours to have caught.** Fit `tau = 0.9*exp(-k*d^2)`
through the only two values every reading agrees on -- centre `0.90`, cross `0.62` -- and the
remaining classes follow with **no free parameter**: `0.427`, `0.203`, `0.140`, `0.046`. That
is their kernel to two decimals, four for four, and it is exactly what Figure 4's caption
describes: a hill decaying radially. Our table matched at the centre, the cross and the
corners and was wrong in the middle -- the same curve **shifted inward by one radial class**.
The shift also explains the thing we had treated as a gap in the book: the eight "unnamed"
cells were unnamed only because the shift had consumed the class that owns `0.14`. The book
PDF, asked directly, confirms all six classes and states that every one of the 25 cells
carries a value.

**The worst part is that we had already been told.** On 2026-08-05 `U-030`/`U-025` were closed
against these exact numbers, with the reasoning written into the ledger: *"A NotebookLM answer
claimed Figure 4 prints all 25 cells with diagonals at 0.42 and the ring at 0.14; the book
summary contradicts it on every point... a notebook answer is not a source."* But the notebook
holds the **PDF**, and `inst/police_thief_p2p_Summary.md` is a **translation**. The rule we
were applying -- *a restatement of a source is not the source* -- was the right rule, pointed
backwards. It cost a wrong emission kernel in both peers for three days, and it would have
cost a refused game against any classmate who read the figure correctly.

**What changed.** The kernel in both repositories, the lock digest (`416a57e1...` ->
`e6aef097...`, still identical across the two peers), the stored scent vectors, the regression
matrix, both PRDs, both unknown registers, and every measured result -- belief sits directly
on the emission field, so nothing downstream was still valid. The tournament headline
survived the change: the served stack still captures 40/40 against all five archetypes on
both board sizes, equal to the referee-truth oracle.

**And one test that should have existed from the start now does.** `test_scent.py` pins the
*curve* -- every class within 0.01 of `0.9*exp(-k*d^2)` -- not just the table. It needs no
source to argue with, and it fails on a one-class shift by twenty times its own tolerance.
The old suite pinned the table to itself, which is why five scent tests passed for three days
over the wrong physics.

**Step 3 was completed only half.** The book notebook answered and is the authority that
settled this. The **code notebook froze** across three attempts -- original tab, reload, and a
brand-new tab, each rejecting even a four-character probe -- so "what does the reference
emit?" is unanswered. Recorded rather than skipped silently: the reference uses subtractive
decay over Chebyshev distance, a different model that cannot arbitrate Figure 4's radial
values, which is why the correction proceeded on the book's authority alone.


## 2026-08-09 — a readout instead of a switch, and a toggle that was wired to nothing

**Prompt.** Sharbel, before a friendly series: "the email sender should be disabled now". Then,
after I proved it four different ways: *"why didn't we implement all these things with a toggle
for the email sender?"*

**The question found a real defect, though not the one it was aiming at.** Both config
templates carried `[email] mode = "draft"` — and **no code in either repository has ever read
it**. Neither is `[email].recipient` read: it appears only in the *forbidden-keys* guard that
keeps private fields off the wire, and as a parameter name in `SendReceipt`. A switch wired to
nothing is worse than no switch, because it invites someone to believe reporting is off
because a file says `draft`. Removed from both templates, with a comment explaining the
removal so nobody helpfully adds it back.

**Why the answer is a readout and not a toggle.** Sending is impossible today for three
structural reasons: no credential exists, no CLI verb reaches the sender, and the play path
never calls it. A boolean is *weaker* than any of those — it can be defaulted wrong, typo'd, or
read from the wrong file. The right fix was never to add a fourth thing to trust; it was to
make the three existing facts **visible**, because proving them took four greps across two
packages, and "I think it's off" is not what anyone should run on with an opponent waiting.

`preflight` prints one screen: version, private config, both endpoints, port, match config with
its Appendix F verdict, the scent-lock digest, and whether reporting is `ARMED` or `DISABLED`
with the credential path it looked at. Exit 1 on any failure, so it can gate a script.

**The reference contributed the check I had not planned.** Asked directly, it has no preflight
*command* — its equivalents are fail-fast gates inside `run_peer`: `validate_agreement(cfg)` in
`peer/sealing.py` for the agreed terms, and **`_ensure_port_free(host, port)`** in
`infra/mcp_server.py`, which exists because a previous agent still holding the MCP port fails
as a bare `WinError 10048` mid-startup. Our own rehearsals lost runs to exactly that, and the
symptom was the *opponent* appearing absent. That check is now the fourth line of the readout,
and its test holds a real socket to prove it fires.

**Every check is tested in both directions.** A preflight that only prints green is the same
failure as the dead toggle it replaced, so each case is driven to both verdicts: credential
present *and* absent, port free *and* held, match config valid *and* below the Appendix F
floor, private config readable *and* missing.

**One test had to be fixed for the right reason.** The "no dead toggle" test first matched the
raw file text and failed — on the comment *explaining the removal*. It now parses the TOML and
checks the document, not the prose. A test that fails on its own rationale is pinned to the
wrong thing.

**Step 3 was completed, but only after four freezes.** The code notebook rejected input on the
first attempt and answered after a reload; the book notebook then froze and did **not** recover
across two reloads, so its question — the book's pre-match checklist — went unanswered. That
half is covered from `inst/` directly, which is the source the notebook only summarises: rules
11 and 12 (config symmetry and the Appendix F floors), 23 (the scent lock), 24 (the Step-0
hardware declaration), 39–40 (no secrets), and 53 (the commit hash). Recorded rather than
skipped silently.


## 2026-08-09 (iii) — the wait that never ran

**Prompt.** The first real match attempt against `amireman`. Our Cop started, its own mailbox
came up, and then it died instantly:

    HandshakeError: our offer could not be delivered: negotiate failed in transport:
    Server error '502 Bad Gateway' for url 'https://...trycloudflare.com/mcp'

**The 502 was his — the bug was ours.** His tunnel was routable with nothing behind it, which
is a normal state for a peer that has not started yet. `serve_match` exists to tolerate exactly
that: it waits up to `connect_timeout_seconds` (120) for the opponent before negotiating. The
wait never ran.

**Why.** The readiness probe was `port_answers(host, port)` — a TCP connect to the host and
port parsed out of the opponent's URL. Through a tunnel that host is a **Cloudflare edge**, and
it accepts on 443 whether or not the opponent's process exists. Proved live: against an
endpoint returning 502, `port_answers` returned `True`. So the probe reported "he's up", the
wait was skipped, and the very first `negotiate` hit the 502 that the wait was there to absorb.

The old probe's docstring defended the choice: TCP "rather than an MCP call" so that "not up
yet" stays distinguishable from "refused the match". **That reasoning is right and is kept** —
what was wrong is that a socket connect stopped meaning "the peer exists" the moment a CDN sat
in front of it. It was correct on localhost, where the only thing that can accept a connection
is the peer itself, and **every rehearsal was on localhost**.

**The fix.** `peer_answers(url)` asks the endpoint instead of the socket: 502/503/504 mean *no
origin behind the tunnel*, and any other answer — including the `406` an MCP endpoint returns
to a bare GET — means *present*. The distinction the old docstring cared about survives
intact: a peer that answers and refuses is up, and what it thinks of the match is negotiation's
business.

The Thief carried the same defect with an extra edge: it parsed the port out of the URL and
**defaulted to 80** when an https URL named none, so it was probing the wrong port of the right
CDN.

**A test earned its keep within a minute of being written.** The malformed-URL case failed —
`urllib.request.Request()` raises from the *constructor*, which sat outside the `try`, so the
probe crashed instead of reporting "not ready". A readiness check that raises turns "the
opponent is late" into a crash. Moved inside the try.

**Lesson, and it is the same one twice in a day.** The schema bug and this one were both
correct in every environment we had ever run, and both were exposed within minutes of a real
tunnelled opponent. Localhost is not a small-scale model of the league — it removes the exact
component (a CDN between the peers) that both bugs lived in. The friendly series has now paid
for itself twice without a single game being played.

## 2026-08-11 — a guard with tests and no caller, found by a second opponent's file

**Prompt.** Group `uoh-ay26` (Aisha Abu Dahesh, Yousef Asadi) proposed a friendly and sent a
`game.json` plus their Police endpoint, `https://cop.uohay26game.com/mcp` — the peer *this*
repository dials. "We want to play a friendly game with this group."

**Two gates refused their file; every other gate passed it.** `schema_version` was `"1.00"`
where this build implements `1.2`, and `agreed_between` was `["cop", "thief"]` — the two
*roles*, not the two group ids, so `validate_participants` could not find `sharNamr`.
Everything else was clean: 14 signed terms including the simulator-profile
`min_center_intensity`, every Appendix F `Fixed` value correct, every `Minimum` at or above its
floor, and a `world` block (`Haifa`, 15 words) the terms projection requires.

**`p2p-thief preflight` printed `ready` for it.** The readout validates the terms projection,
and the projection reads neither field. Worse, this repository already *had* the check:
`check_config_schema_version` in `protocol/config_integrity.py`, `SUPPORTED_CONFIG_SCHEMA_VERSIONS
= {"1.2"}`, exercised by `test_config_shape.py` — and **not called from anywhere on the runtime
path**. It was written, tested, exported in `protocol/__init__.py`, and dead. Tests prove a
function works; they do not prove anything calls it.

Both checks now run inside `_match` via `_wire_gates`, and the same fix went into the companion
Cop, which had no equivalent function at all. The fixture `_private()` used `group_id = "t"`,
which was safe only while nothing compared it to `agreed_between`; it now defaults to a real
participant, and three new tests drive both checks to their failing verdict — including the
literal `["cop", "thief"]` shape that arrived.

**What each notebook contributed.** Code notebook: the reference loads `game.json` through
`ConfigManager.__init__` (`src/police_thief/shared/config.py`), ships `schema_version: "1.3"`
in its own copy for both roles, and validates through `_check_version` against
`SUPPORTED_CONFIG_VERSIONS` (`shared/version.py`), raising `ConfigVersionError`. It runs **no**
explicit `group_id in agreed_between` test — the field is policed only because it sits inside
the SHA-256-signed terms, so a reference-shaped peer accepts `["cop", "thief"]` right up until
it meets one that does not. Book notebook: warm-ups are excluded from the rule 37/38
declaration and the rule 51 report and count toward neither `max_games_per_team` nor
`min_games_to_pass` (p. 70/166, 70/169), verified against `inst/police_thief_p2p_Summary.md:2028`
and rule 52 at `:3442`. So reporting stays off, and a friendly does not spend the single
counted meeting rule 52 allows against this group.

**Evidence.** Two OS processes played the corrected file end to end on localhost: negotiated,
21 turns, `CAPTURE`, both sides reporting the same outcome, and `replay` printing
`Verified OK — 21 steps re-verified`. Their endpoint answered `502` — Cloudflare up, their
tunnel down — so no game has been played against them yet.

## 2026-08-12 — the game we won and lost: leaving before the audit

**Prompt.** "Add the logging" — plus the opponent's message: *"Opponent unreachable mid-match
— resolving as technical loss: submit_audit timed out … 502 Bad Gateway. Technical loss
recorded."*

**We played group `uoh-ay26` and survived all 35 steps.** Our log says `survival`, replays
`Verified OK — 35 steps re-verified`, and cost zero tokens. Their log says `technical_loss`.
Rule 35 scores conflicting reports **0/0 for both**, so a clean win became nothing.

**Nothing was wrong with the game. We left before the conversation was over.** `serve_match`
wrote the log and returned the instant the horizon was reached; the CLI then exited and the
mailbox died with it. Their Cop called `submit_audit` a moment later, met a live tunnel with
no process behind it, and correctly recorded a technical loss. Rule 36 makes the mutual audit
"a mandatory condition before agreement" — and an agreement needs two peers present. A peer
that stops listening the moment *its own* result is decided can never satisfy it, and forces
an honest opponent to record a loss against a game it actually played.

`adapters/post_match.py` now holds the mailbox open for `audit_send_timeout_seconds` (60)
after the last move, draining until an audit lands or the window closes. The wait is bounded
on purpose: the opponent may legitimately never audit, and waiting forever converts their
fault into our hang, which is exactly what rule 6's watchdog exists to prevent.

**A second defect fell out of the first, and it is the worse one.** The log hardcoded
`"confirmed": True`. It was never a claim about agreement — it meant "negotiation succeeded" —
but it *reads* as "the result was mutually agreed", and it was written unconditionally,
including in the game the opponent scored as a technical loss. An audit artifact asserting a
mutual agreement that never happened is the shape of a false declaration. `confirmed` is now
the return value of the audit wait.

**The logging, and why it was the same failure.** Earlier that night an offer from the same
opponent reached this peer and vanished, leaving only a column of `200 OK`. An MCP tool error
is an application-level result, so the HTTP layer reports 200 whether the call succeeded,
named a tool we do not have, or used the wrong argument name; our tools acknowledge on
*enqueue* while validation happens later at *drain*; and nothing wrote either down. The
rejection reason was computed into a `Delivery` and discarded by every caller but the turn
loop. `services/wire_log.py` appends one JSONL line per arrival and per verdict —
tool, queued, top-level key names, accepted, reason. **No payload**: a turn carries the sealed
commitment and, after reveal, the nonce, and writing those to an unmanaged file is a rule
18/39 hazard for a diagnostic nobody needed. The key *names* are what diagnose a shape
mismatch; the values never came into it. Every write failure is swallowed, because logging
that can refuse a turn is worse than no logging.

Verified end to end over two processes: `opponent audit received`, `CAPTURE after 21 steps`,
43 wire events including `submit_audit` received and validated. 1658 tests, 94.96% branch
coverage. `serve.py` also dropped under the 150-line gate it had been one line over.

**Still open, and it is the same bug with the roles swapped:** the companion Cop returns
immediately after `write_match_log` with no audit window, so sub-games 2/4/6 will fail exactly
this way against an opponent Thief that audits. Recorded rather than fixed tonight.


## 2026-08-12b — the mirrored `boxed_in` rule (`C-029`)

**Prompt.** Same review as the companion: can group `uoh-ay26` play us across all six
sub-games? Their Thief sends `win_claim` `{"type": "boxed_in"}` for the book's third capture
condition, and the companion Cop rejected the entire turn message over it.

**This repository did not have that defect** — `protocol/wire.py` validates only `sender` and
carries `win_claim` through uninterpreted — but that is luck, not design, and an unpinned
guarantee is one refactor from being lost. So the rule is stated here in the direction this
role actually faces: a `boxed_in` claim must **never capture us**. `_caught_by` reads only
`capture_claim` and checks it against our real cell; rule 22 makes a false capture
declaration disqualifying, and believing an unproven assertion would let an opponent end a
game it was losing by asserting a fact it cannot observe.

Both notebooks were asked and gave different halves of the answer: the book settles the
condition by Cop claim plus truthful answer (`inst/police_thief_p2p_Summary.md:810`, `:830`),
while the reference has no such signal at all (`win_claim` ∈ {`survival`, `None`},
`peer/turn_sender.py::take_turn`). Neither supports emitting it, so this side still emits only
`survival`, unchanged.

Five tests, no status changes, no behaviour change — `THIEF-002` forbids closing anything
here on the companion's evidence, and nothing is closed. ruff and the 150-line gate are clean
in this repository.


## 2026-08-12c — length gate confirmed clean here

The companion repository had two `G-04` violations at `HEAD` and CI was red on that step.
This repository was checked at the same time and is clean: 148 source/script files and 183
test files, zero violations, so nothing was split and no code changed. Recorded because
"the other repo had a gate failure" is exactly the kind of thing that turns into an
assumption about this one, and the eight-step workflow says both repositories are checked
every time.


## 2026-08-12d — the identity accommodation on this side (`C-030`)

The companion's log entry carries the full investigation; this side's share: our serve
path builds identity in `adapters/negotiated.py::load_negotiation_inputs` via
`identity_from_private`, which sends the seven reference-shaped members and no
`git_commit_hash` — the member `uoh-ay26`'s `mutual_sign_off` regexes. Attached now from
`shared/git_info.py::running_git_commit` under `contextlib.suppress(GitInfoError)`. The
book's mandated home for the hash (sealed Step-0, `github_commit`) is untouched and stays
fail-closed; the accommodation is best-effort because an optional duplicate must never
refuse a match. Three tests pin presence, untouched mandated members, and the non-fatal
fallback. The evening friendly's game-1 log here replays `Verified OK` at 35 steps —
the voided sign-off was their reading of our identity, not our evidence.


## 2026-08-12f — series complete; consensus tolerance adopted (`C-031`)

This role's share of the night: survival at 35 in all three Thief games, every audit
accepted by the opponent's verifier — because `sealed_spec_record` has carried the
reference-verbatim step-0 members all along, which is precisely what the companion's
Police builder lacked (companion `C-041`). Adopted the `series_consensus` tolerance
mirroring companion `C-040`: `AuditPayload` parses the claim, refuses it if it smuggles
records, and the inbound handler acknowledges it vacuously. Four tests. Step-3 disclosure
as in the companion's log: no fresh notebook queries — both fixes implement agreements
already established and verified earlier today.


## 2026-08-12g — companion `C-042`: this repository's record shape was the standard

The opponent's converter crashed on the companion Police's sealed records -- missing
`state` -- while this repository's records converted cleanly in every game they ever
parsed. The companion now seals this repository's exact shape (`state_str` format,
post-move, `verdict` mirroring `intent`). Nothing changed here; recorded because the
drift family (`C-039` wire-log arming, `C-041` step-0 shape, `C-042` record shape) is
three-for-three the same lesson: two repos implementing "the same" record independently
drift until a third party parses both.


## 2026-08-12h — six Thief-role games, zero rejections, two rows move

Series `0812-2201` reproduced `0812-1934` exactly from this role: survival at the full
horizon in games 1/3/5, every audit accepted, and — new tonight — not one rejected wire
event anywhere in the series. `M8-003c` closes on this evidence (six live Thief-role
games across two complete series, both sides reading 90–30 in writing); `M5-005c`
narrows to its two M8 screenshots.


## 2026-08-13 — no code changed here; the companion's cheap region test, written down

**Prompt.** "Finish the test and docs", closing a session a power cut had interrupted. The
interrupted work was entirely in the companion Cop repository. This entry exists because
steps 6 and 7 of the standing order say *both* repositories, and because the finding has a
real consequence for the open evader experiment recorded above.

**Nothing here was damaged and nothing here was edited in `src/`.** `git fsck` clean, no
truncated file, no interrupted git operation; the suite is green at 1791 passed, 93.35%
coverage. The working tree's one modified file is a friendly game log, which is a separate
open question and was deliberately left untouched.

**What was recorded.** The open note from `2026-08-13`'s Cop work — that a pursuer scores
best with its distance term at zero, which is the mirror of this agent's distance-plus-
mobility ranking — now carries the two results that make the counter-experiment cheap.
Reachability between the two agents is one spread rather than a search, because flooding
the evader's component with the pursuer's cell walled off puts a cell adjacent to the
pursuer in that component exactly when a path exists. And `E - V + components` needs no
component pass when the scored region is a flood's own output, since that is connected by
construction. Both are graph facts, established without reading companion code, so
`THIEF-002` is intact.

**The claim is deliberately narrow.** The experiment is still not run and still not
evidenced. Cheapening a measurement says nothing about whether the term is right for the
side being chased, and this agent has survived all nine live hunts it has played. It is
written down so the next attempt starts from the cheap formulation rather than
rediscovering the expensive one and abandoning it on cost.

**Method: step 3 was skipped.** Neither notebook was asked — the work was a unit test for
an internal parameter in the companion plus a documentation catch-up, and neither the
reference simulator's behaviour nor the book's requirements govern either. Steps 1, 2, 5,
6, 7 and 8 ran in full across both repositories.


## 2026-08-13b — the companion's naming defect, recorded here because this side names artifacts too

**No code changed here.** Steps 6 and 7 say both repositories, and this one has a real
stake in the finding rather than a courtesy mention.

**What was found next door.** The Cop repository derived `game_id` as
`game-<12 hex of the config sha>` and wrote its artifacts under that name, while its result
report used the agreed `G00N` label — so the report linked log files that did not exist.
No gate caught it because none compares an artifact's *name* against the report that
*points at* it; it surfaced only by diffing two teams' result files after the live G005
series.

**Both notebooks were asked.** The book: Appendix F table 20 names all four artifacts from
`<game_id>`, and that identifier is the label the two teams agree — explicitly **not** a
value derived from a hash of the configuration, whose only job is locking the config under
`config_sha256`. The reference: `derive_game_ids` in `domain/game_ids.py` computes a human
id from the agreed terms plus both group ids, so both peers reach it without an extra round
trip. Both rule out a digest-derived name.

**Why it matters on this side.** This repository writes the log for sub-games 1/3/5, so it
names artifacts on half of every series. If it derives `game_id` or `game_uid` from the
config hash, a series produces a set whose two halves disagree — which is the defect that
was just removed, reintroduced from the other end. **This side has not been audited yet**;
the companion was fixed first because that is where the defect was observed. Verify before
the counted game.

**Method.** Step 3 was attempted, blocked on a disconnected Chrome extension, and work
stopped there rather than proceeding — then both notebooks were asked once it was
reconnected. Steps 1, 2, 4, 6, 7 and 8 ran in full across both repositories.


## 2026-08-13c — the warning we wrote and did not act on, found live in the counted game

**Prompt.** "I stopped it, fix the thief repo."

Earlier today this repository's TODO and README gained a paragraph saying it writes the
logs for sub-games 1/3/5, had **not** been audited for the companion's artifact-naming
defect, and should be checked before the counted game. It was not checked. The counted
`G009` series then produced `log_game-5a7b4a6e58be_g01.json` from this side and
`config_G009_g02.json` from the companion, in the same series directory, along with two
declarations. Stopped at sub-game 2.

**The lesson is not "we had a bug".** It is that a warning recorded in the repository that
cannot act on it is worth nothing. The companion's fix was made where the defect was
observed; this half was left with a note. Two repositories that cannot see each other
produce one artifact set, so a fix in one is not a fix -- and the only mechanism that would
have caught it is the one now added: a test pinning the shared `game_uid` constant that
both sides must reproduce.

**Method note.** Step 3 was not re-run. Both notebooks were asked this same question
earlier in the session -- the book gave Appendix F table 20 and the prohibition on a
hash-derived id, the reference gave `derive_game_ids` and the terms-plus-groups mechanism
-- and the standing order says to ask each what only it can answer rather than send the
same question twice. This is the identical defect in the second repository, so the answers
already obtained govern it. Steps 1, 2, 4, 5, 6, 7 and 8 ran in full.

**Verified rather than assumed.** Before wiring `derive_game_uid`, all three
implementations were checked to produce `7b1d942e-5a9c-6e0c-312a-761dd7dec131` from the
same terms: this repository, the companion, and the value `uoh-ay26` sent us. The
canonical-JSON form is byte-identical across the two repositories
(`sort_keys=True, ensure_ascii=False, separators=(",", ":")`), which is what makes the
duplicated derivation safe under `THIEF-002`.

**The refusal earned itself immediately.** `series_game_id` raises when the label is
missing, and the first run raised -- the private toml had never carried
`[game].series_game_id`. That is the failure surfacing at launch instead of at grading,
which is the whole argument for refusing over defaulting.


## 2026-08-13d — G009 counted: three sub-games, three survivals, against a Police rebuilt to catch us

This repository played sub-games 1, 3 and 5 of the counted `G009` series against
`uoh-ay26`. All three ended in **survival at the full 35 steps**. The series went 60–40 to
`sharNamr`, and with `G008` that is two counted games against two groups, so `[AE-31]`'s
minimum is met.

**The part worth recording is who we survived against.** Twelve minutes after losing the
uncounted `G005` series 0–6, `uoh-ay26` pushed `68a69dbe`, whose message is "harden cop
pursuit against stale scent trails" and whose comment names our games: *"G005 g01/g03
exposed this exact failure: the apparent singleton was treated as certainty and the Cop
spent a whole turn walling the trail."* They raised `max_ambiguity` from 8 to 16, deleted
the early return that promoted an inferred scent centre to certainty, and rewrote their
motion test so any change in candidate support counts as ambiguity.

It changed nothing. Three full horizons against the hardened pursuer, exactly as against
the version it replaced. The `M6-031` decoder and the window-geometry inference are not
winning on an exploit that a patch closes — which is the claim, and this is the first
evidence for it against an opponent who had specifically tried.

**The naming fix, proven where it mattered.** Every artifact written here carries `G009`,
one declaration, zero hash-named files. Hours earlier the same series had to be aborted at
sub-game 2 because this side wrote `log_game-5a7b4a6e58be_g01.json` while the companion
wrote `config_G009_g02.json`. The replay produced a clean set from both halves.

**Method.** Steps 1–8 ran. Step 3 was not re-queried; both notebooks were asked earlier in
the session about artifact naming and nothing here turns on a question only they can answer.


## 2026-08-14 -- Barrier-aware evasion v2: closing the walling-Cop gap (experimental, default-off)

A post-real-game optimisation pass targeting the one measured weakness of the shipped
evasion: a Cop that combines interception with proactive barrier placement. The shipped
`choose_adaptive_action` is already 24/24 against every *mover* archetype but converts only
**8/24** against the interception waller, because its exact solver (`escape_search`) freezes
the barrier field and plans against movement alone.

**What was built (all isolated; production default unchanged).**
- `strategy/waller_models.py` -- the deterministic walling archetypes in `src` (byte-parity
  with the committed `experiment_wallers` grid, pinned by a test); every wall they propose
  passes `domain.barriers.validate_barrier_placement` (strategy proposes, the domain validates).
- `strategy/barrier_search.py` -- an exact escape solver that carries the barrier mask and
  quota inside the recursion, mirroring `escape_search`'s step order; with quota 0 it equals
  `escape_search` exactly (cross-checked in tests).
- `strategy/barrier_aware_policy.py` -- keeps the adaptive pick whenever it already survives
  the assumed waller, substitutes a walled-safe action only when the adaptive pick would be
  trapped, and falls back to the adaptive pick otherwise. `make_decide` gains a `strategy`
  selector; "current" (the default, and any unknown value) is the shipped policy byte for byte.
  Opt-in only via the private [strategy].policy key.

**The finding.** A first cut gated the planner on danger (a disclosed barrier or an imminent
seal). Measured, it recovered nothing (8/24 unchanged, zero overrides): against a walling
interceptor the escape space is lost before a wall is placed, so the gate opened too late.
Planning from the first move instead -- "always-on" -- converts the interception waller
8/24 -> 24/24 and the greedy waller 23/24 -> 24/24, on the decoded belief the live Thief
carries, at every search depth from 6 up. All four mover archetypes stay 24/24 (no
regression). The exact solver fed the true Cop cell escapes all 24 openings against both
wallers -- the ceiling this reaches, which refutes the earlier note that the wall-armed
equal-speed pursuer is structurally winning from these openings.

**Verdict.** SHIP_CANDIDATE, default still "current"; flipping the production default is the
coordinator's call. Latency (depth 8, worst decision) stays far inside the response budget.
Deterministic throughout (book section 6 sanctions deterministic minimax/expectimax), so
replay verifies the logged move and the audit is untouched.

**Method / source verification.** BOTH NotebookLM notebooks were queried (book
ff2216f4-1d49-4614-be95-a5ec6a8a264b, simulator f504d33d-45c7-42e0-8c97-c8cf6851c594): five
ask_question calls across both, with escalating timeouts and an explicit wait. Each returned
only NotebookLM's loading placeholder ("Exploring your material...", "Reading your inputs...",
"Processing material...", "Digging into details...") and never a settled grounded answer;
setup_auth needs an interactive browser login that cannot be driven headless. The required
rules were therefore verified against the higher-ranked source directly -- the official book
PDF (Source-of-Truth rank 1; the simulator notebook is rank 7). Book-confirmed: section 3.4
barrier placement one step from the Cop, permanent, capture on the Thief's cell or a fully
trapped Thief, mandatory truthful declaration, max_barriers 14, and a barrier replaces the
move that turn; section 6 explicitly endorses "look-ahead search (such as minimax or
expectimax against the opponent's belief)" and stresses it "remains deterministic and
transparent". The NotebookLM tool failure is recorded here rather than skipped.

## 2026-08-15 -- the imreeyal/anrbj666 conformance kit, and the one key that blocked us

**Prompt.** Sharbel forwarded the announcement of `github.com/Imreec/copthief-league-protocol`
and asked whether we are aligned with that group and can run a game.

**What was done.** Cloned the kit, ran its own `verify_vectors.py` (125 checks, 15 fixtures,
all pass), then wrote adapters that point **our** production functions at **their** JSON
fixtures. 17/17 CORE vectors pass in each repository. Fed their real cross-team greeting to
our real offer verifier: refused on `min_center_intensity`, accepted 14 terms once the key was
added to the shared match file. Adopted their sorted-pair `game_id`, disarmed the reporting
mode, and drafted the Stage-1 planning message.

**Output.** One blocker, and it was ours: an omitted optional term in one of three opponent
match files. No code changed -- the projection, the schema and `U-028` all already supported
the key.

**Refinement.** The first draft of the conformance check re-implemented their `ref_commit` and
compared it to their vectors, which proves only that two copies of the same function agree. It
was rewritten to import our shipped `commit_of` / `move_commit`, which is the only version of
the test that could have failed.

**Lesson 1 -- a fixture of a *real* inbound message is worth more than a spec.** Every
construction in their kit we already matched; the thing that found a defect was the archived
greeting from a real peer. We have shipped fixtures of our own shapes and none of a
classmate's. Their `cross-team-frame.json` is the pattern to copy.

**Lesson 2 -- verify the edit, not the intent.** Patching the two private TOMLs with a
PowerShell hashtable of replacement pairs silently corrupted one of them: `@(@('a','b'))`
flattens to `@('a','b')`, so `$pair[0]` indexed a *character* and the script replaced every
`s` in the file. It was caught only because the change was followed by a `tomllib` parse and a
line-level diff against a backup taken first, and reverted from that backup. The habit that
saved it -- back up, then assert the file still parses and only the intended lines moved -- is
worth more than the tool choice; the rewrite in Python asserts each search string occurs
exactly once before replacing.

**Lesson 3 -- disclose the skipped gate in the same message.** Step 3 was not run; the reason
is recorded in `TODO.md` beside the change rather than being available on request.

**Method.** Steps 1, 2, 4, 5, 6, 7 ran. Step 3 (both notebooks) did **not** -- see `TODO.md`
for why, and treat that as a weakened gate rather than a satisfied one.

## 2026-08-15b -- G008's naming, and the tag that named the wrong commit

**Prompt.** Sharbel: "fix the stale tags and the G008 naming while we wait".

**What was done.** Established that the six `G008` artifacts and the emitted result report are
each internally consistent and mutually contradictory, then asked before touching either,
because `G008` is counted, reported, and mutually agreed. Chose to document rather than
rewrite. Wrote `games/amireman-real-0813-0534/README.md` in both repositories, checked all
fourteen links resolve under the documented substitution, and re-verified all six logs. Moved
`v1.0-submission` in both repositories after committing the working tree.

**Output.** One new file per repository, one tag pointer per repository, no evidence altered.

**Lesson -- "fix" is not always "make it match".** The tidy option was to rename six files and
rewrite their `game_id`/`game_uid` so the report's links resolved. It would have produced a
cleaner-looking repository and a worse one: the artifacts are the record of a counted game
that has already been reported and agreed by the opponent, and evidence edited after reporting
cannot be distinguished from evidence edited because it was wrong. The cost of the honest
option is one paragraph a grader has to read; the cost of the tidy one is every other artifact
in the repository becoming slightly less believable. Asked rather than assumed, because the
two options were not a matter of taste.

**Lesson -- a gate that exists in one repository is not a gate.** `check_submission_tag.py`
lives only in the Thief repository and runs in neither CI, so a stale tag failed silently in
one repository and was unobservable in the other. The same asymmetry covers
`check_artifacts_committed.py`. Gate parity across the two repositories is worth its own pass.

**Method.** Steps 1, 2, 4, 5, 6, 7 ran; step 3 did not -- see `TODO.md` for the reason.
