# PRD — Distributed Cops-and-Robbers over a P2P Network

- **Document version:** 2.11
- **Changelog:** v2.11 — compliance audit vs. all 3 Material sources: result JSON carries **all four repo links** (rule 49), scent-model pre-game crypto-lock made explicit (rule 23), UI-documentation task added (guidelines §10), task counts reconciled. v2.10 — review pass: Acknowledge protocol step, barrier-capture + honest capture answer, NL-only hint rule, 6-sub-game series + league integrity.
- **Status:** DRAFT — awaiting team approval before development (guidelines §2.5)
- **Owners:** `<team members — fill in>`
- **Course:** Orchestration of AI Agents, University of Haifa — Final Project
- **Binding sources:** game rulebook `police_thief_p2p` (Appendix F = single source of truth for numbers) and `software_submission_guidelines-V3` (code-quality rubric).
- **Companion:** `PLAN.md` (architecture), `TODO.md` (635-task WBS). Requirement IDs trace to tasks in §9.

> **Clean reimplementation.** The lecturer's `Game-P2P-Cop-Chase` engine is a study reference only; nothing is copied. Our solution meets the full specification on its own.

---

## 1. Overview & Context

### 1.1 Problem
Build two **autonomous AI agents — a Cop and a Thief — that compete on a shared grid over a real peer-to-peer network with no central server and no referee.** Each agent perceives only partial, possibly-deceptive information and must prove its own honesty cryptographically. Modeled as a **Dec-POMDP**.

### 1.2 Audience
- **Primary:** the course examiner (runs each agent, plays it in a live league, grades league result + code quality).
- **Secondary:** opposing teams' agents, which must interoperate with ours byte-for-byte over MCP.

### 1.3 Deliverables
- **Two separate GitHub repositories** (Cop, Thief), cross-linked, shared with the lecturer.
- Agents that negotiate, play, seal every move, audit, and auto-report.
- Full docs (this PRD, PLAN, TODO, 5 per-mechanism PRDs), README academic report, research notebook, screenshots.

---

## 2. Goals & Success Metrics

Judged on **two independent axes**:

| Axis | Measures | Source |
|---|---|---|
| **League result** | Does the agent win vs. real opponents? | rulebook |
| **Code quality** | Is the software professional-grade? | guidelines |

### 2.1 League success (rulebook's four metrics)
| Metric | KPI / acceptance |
|---|---|
| **Coordination** | full P2P game over MCP, 0 deadlocks, 0 protocol errors |
| **Adaptation** | belief map beats random baseline on capture/survival rate |
| **Integrity** | 100% games pass mutual SHA-256 audit; 0 self-caused forfeits |
| **Architecture** | 0 crashes on opponent failure; every failure → defined end state |

### 2.2 Code-quality acceptance (hard, auto-checkable)
- Files **≤150 lines** of code · coverage **≥85%** · **0 Ruff violations** (`E,F,W,I,N,UP,B,C4,SIM`; ignore `E501`; line 100)
- **`uv` only** (`pyproject.toml`+`uv.lock`; no pip/venv/requirements.txt)
- **0 secrets** in code; `.env-example`; `.gitignore` excludes `credentials.json,token.json,*.key,*.pem,.env`
- **0 hardcoded config values**; SDK-first; Gatekeeper for all external calls; version tracking from 1.00.

### 2.3 League acceptance thresholds
- **≥2 games vs ≥2 different teams** completed + reported (minimum to pass); max **10** games per team.
- Official matches run the **6-sub-game series** (Fixed, Appendix F Table 18).
- Both teams agree each result; each sends its own signed JSON report; conflicting reports → 0 for both.

---

## 3. Functional Requirements

### 3.1 Board & physics (Appendix F) — [T061-110]
- **FR-1** Grid **7×7** (min); origin top-left `(0,0)`; Thief `(3,3)`, Cop `(0,0)` (negotiable).
- **FR-2** Moves **N,S,E,W,STAY**; one orthogonal step or stay; **no diagonals**.
- **FR-3** Cop barriers: quota **14** (min), one step away, permanent, **truthfully declared**.
- **FR-4** Capture: Cop on Thief cell + claim, **a barrier placed on the Thief's cell**, OR Thief has no legal move. The Thief must answer a capture claim **honestly** — a lie is exposed by the audit and forfeits. Thief wins by surviving **35** steps (min).

### 3.2 Perception — [T229-267]
- **FR-5** Each move emits a **5×5 scent field** (center **0.9**), **multiplicative decay 0.10/turn**; only the field crosses the wire, never a position.
- **FR-6** Each agent keeps a **belief map** updated from scent + hints (trust factor) and diffused each turn.
- **FR-7** Hints are **natural language only**, **≤15 words**, truthful or bluff (flagged by `intent`/`verdict`). Encoding coordinates or numeric location protocols in hints is **forbidden** (Appendix E rules 26–27 — disqualification). Landmark vocabulary follows the agreed `map_area`.

### 3.3 Trust & integrity (no referee) — [T343-378]
- **FR-8** Seal each step: `commit = SHA256(canonical_json(state,move,intent,nonce))`; send only the commit. The opponent **acknowledges** the lock before any reveal — full sequence **Commit → Acknowledge → Reveal → Final-Reveal** (rulebook Fig. 6).
- **FR-9** Reveal nonces at end; **mutual audit** re-verifies every step; mismatch = **technical forfeit** (0).
- **FR-10** Pre-game **Step-0**: signed hardware spec (OS/CPU/RAM/GPU) + code commit hash + token budget.

### 3.4 Decision (our creative core) — [T176-228]
- **FR-11** Move chosen **purely by Python**; the LLM is **never** consulted for the move.
- **FR-12** LLM (optional) writes only the hint; default = zero-token template; providers configurable.

### 3.5 Networking (P2P) — [T131-175, T305-342]
- **FR-13** Each agent = FastMCP **server + client**; Cop/Thief in **separate processes/config dirs**; no shared state.
- **FR-14** Servers exposed via **tunnel** (ngrok/Localtonet) for league; localhost for dev.
- **FR-15** Pre-game **negotiation**: exchange + verify SHA-256 over `game.json`; refuse on mismatch.

### 3.6 Observability — [T460-489]
- **FR-16** **Live GUI** shows only **local truth** (own pos, belief heatmap, turn banner) — never the full board.
- **FR-17** **Replay Viewer** re-verifies every commit (`Verified OK`/`TAMPERED`). **Mandatory.**

### 3.7 League & reporting — [T408-459, T545-557]
- **FR-18** Play a **series of 6 sub-games** per opponent (Appendix F Table 18, Fixed; dev examples may use 1); roles alternate; aggregate scores with tie rule (tie = **2**). Only **one counted game per opponent** — warm-ups uncounted; a win vs a **new** opponent earns the diversity bonus (**10**); declare prior games-played **truthfully** at each game start (false declaration disqualifies); both teams must **agree the result** — conflicting reports → 0 for both.
- **FR-19** Emit the **4 signed JSON artifacts** (declaration/config/log/result); the game-end result JSON carries **all four GitHub links — two per team** (ours + opponent's, rule 49), every per-game commit hash, and total tokens consumed.
- **FR-20** Auto-email result JSON via **Gmail API (OAuth2, `gmail.send`)** through a **Gatekeeper**; both teams send separately.

### 3.8 Scoring (Fixed) — [T101-110]
Capture: Cop **20** / Thief **5**. Survival: Cop **5** / Thief **10**. Tie **2**. Technical loss **0/0**.

---

## 4. Non-Functional Requirements (ISO/IEC 25010)
- **NFR-1 Reliability:** deadlines on every wait; watchdog (60s) + tracker (30s); failure → defined end state, never a silent hang. [T387-398]
- **NFR-2 Performance:** default game offline ~0 tokens; move computation instant. [T268-290]
- **NFR-3 Security:** least-privilege OAuth; no secrets in repo; keys via env. [T446-459]
- **NFR-4 Maintainability:** SDK-first; files ≤150 lines; DRY; docstrings; ≥85% coverage. [T498-511]
- **NFR-5 Portability:** Python 3.13+, `uv`, cross-platform; relative imports only. [T507-508]
- **NFR-6 Interoperability:** canonical JSON so any team verifies our commits byte-for-byte. [T349]

---

## 5. Assumptions, Dependencies, Constraints
- **Assumptions:** opponents obey the rulebook + Appendix F; both sides load byte-identical `game.json`.
- **Dependencies:** `fastmcp`, Gmail API + OAuth, a tunnel service, `uv`, `ruff`, `pytest`.
- **Constraints:** Appendix F values are minimums (raise by agreement, never lower); "Fixed" values immutable; where the reference engine differs from the book, **the book wins** (e.g. scent decay multiplicative).

---

## 6. Out of Scope
- Reinforcement learning (allowed, not required). · More than 2 agents; continuous space; central server. · Reusing the reference engine's source.

---

## 7. Timeline & Milestones (layered, rulebook Ch.10)
| Stage | Deliverable | Milestone | Tasks |
|---|---|---|---|
| 0 | Docs + scaffold | PRD/PLAN/TODO approved; CI green | T001-060 |
| 1 | Base logic | **M1** move + capture (local) | T061-130 |
| 2 | MCP infra | **M2** message A→B (localhost) | T131-175 |
| 3 | Blind strategy | **M3** shortest path to target | T176-228 |
| 4 | Language + scent | **M4** belief + truth/lie hints | T229-304 |
| 5 | Cloud + tunnel | **M5** remote game via tunnel | T305-342 |
| 6 | Security | **M6** commit-reveal + audit + Step-0 | T343-407 |
| 7 | Reporting shell | **M7** Gmail JSON + GUI + Replay OK | T408-497 |
| 8 | Quality/research/submit | pre-submission gate | T498-620 |

---

## 8. Per-mechanism PRDs (guidelines §2.3 — write next, T004-008)
`PRD_commit_reveal.md`, `PRD_scent_belief.md`, `PRD_strategy.md`, `PRD_p2p_mcp.md`, `PRD_gatekeeper_reporting.md`.

---

## 9. Requirements Traceability Matrix
| Requirement | Milestone | Verified by | Tasks |
|---|---|---|---|
| FR-1…FR-4 (board/physics) | M1 | unit tests, local demo | T061-130 |
| FR-13…FR-15 (P2P/MCP/negotiation) | M2, M5 | integration tests | T131-175, T305-342 |
| FR-11…FR-12 (strategy) | M3, M4 | benchmark vs baseline | T176-228 |
| FR-5…FR-7 (scent/belief/hints) | M4 | unit tests, belief-accuracy plot | T229-304 |
| FR-8…FR-10 (crypto/Step-0) | M6 | audit tests, tamper test | T343-407 |
| FR-16…FR-17 (GUI/replay) | M7 | screenshots, tamper demo | T460-489 |
| FR-18…FR-20 (league/reporting) | M7 | 4 artifacts validate, email sent | T408-459, T545-557 |
| NFR-1…NFR-6 (quality) | all | CI gates (ruff/cov/line/secret) | T498-620 |
| v2.10/v2.11 additions (Ack step, NL-only hints, 6-game series, league integrity, 4 repo links, scent-lock, UI docs) | M2, M6, M7 | protocol + hint-validation + artifact tests | T621-T635 |
