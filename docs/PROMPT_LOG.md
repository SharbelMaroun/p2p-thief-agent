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
