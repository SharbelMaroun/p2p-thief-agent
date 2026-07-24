# TODO — Full Work Breakdown Structure (600+ tasks)

- **Document version:** 2.11
- **Changelog:** v2.11 — compliance audit vs. all 3 Material sources: T416 corrected (4 repo links, rule 49); addendum B T633–T635 added (4-link result artifact, UI documentation, scent-model lock test). v2.10 — review pass: statuses updated; addendum A T621–T632 (Acknowledge step, NL-only hint validation, 6-sub-game series, league integrity).
- **Status:** DRAFT — approve before development (guidelines §2.5)
- **Companion:** `PRD.md`, `PLAN.md`
- **IDs:** global sequential `T001…`. **Priority:** P0 blocker · P1 core · P2 polish. **Status:** `[ ]` todo · `[~]` in progress · `[x]` done.
- **Scope note:** tasks are written for the **canonical engine**; each applies to **both repos (Cop + Thief)** unless marked *(role-specific)*. Role-specific items differ only in default role + strategy class.
- Each sub-area has a **Done when** gate. Milestones (M1–M7) end each build phase.

---

# PHASE 0 — Documentation & Scaffold

### 0.A Documentation set · *Done when: all docs exist and are approved*
- [~] **T001** (P0) Finalize `docs/PRD.md` and get team sign-off *(v2.10 written; awaiting approval)*
- [~] **T002** (P0) Finalize `docs/PLAN.md` and get team sign-off *(v2.10 written; awaiting approval)*
- [~] **T003** (P0) Finalize `docs/TODO.md` (this file) and get team sign-off *(v2.10 written; awaiting approval)*
- [x] **T004** (P0) Write `docs/PRD_commit_reveal.md` (crypto mechanism)
- [x] **T005** (P0) Write `docs/PRD_scent_belief.md` (perception mechanism)
- [x] **T006** (P0) Write `docs/PRD_strategy.md` (decision mechanism)
- [x] **T007** (P0) Write `docs/PRD_p2p_mcp.md` (networking mechanism)
- [x] **T008** (P0) Write `docs/PRD_gatekeeper_reporting.md` (reporting mechanism)
- [ ] **T009** (P1) Create `docs/ADR/` and seed ADR-1…ADR-7 as separate records *(ADRs currently live in PLAN §8)*
- [x] **T010** (P1) Create `docs/PROMPTS.md` prompt-engineering log skeleton
- [ ] **T011** (P1) Draft `README.md` skeleton with the 6 required report sections
- [ ] **T012** (P2) Create `docs/GLOSSARY.md` (Dec-POMDP, stigmergy, commit-reveal, …)
- [ ] **T013** (P2) Add a docs index / table of contents
- [ ] **T014** (P0) Lecturer review checkpoint for all Phase-0 docs

### 0.B Repository setup · *Done when: both repos clone, cross-link, share with lecturer*
- [ ] **T015** (P0) Create Cop GitHub repo *(role-specific)*
- [ ] **T016** (P0) Create Thief GitHub repo *(role-specific)*
- [ ] **T017** (P0) `git init` + initial commit in each
- [ ] **T018** (P0) Add remotes; push `main`
- [ ] **T019** (P0) Share both repos with `rimesegal@gmail.com` (or make public)
- [ ] **T020** (P0) Cross-link: Cop README → Thief repo and vice-versa
- [ ] **T021** (P0) Add `LICENSE` file to each repo
- [ ] **T022** (P0) Add `.gitignore` (exclude `.env`, `token.json`, `credentials.json`, `*.key`, `*.pem`, `logs/`, `__pycache__/`)
- [ ] **T023** (P0) Add `.env-example` with dummy placeholders
- [ ] **T024** (P1) Configure branch protection on `main`
- [ ] **T025** (P1) Add PR template + CODEOWNERS
- [ ] **T026** (P1) Add issue templates mirroring these phases
- [ ] **T027** (P2) Add `CONTRIBUTING.md` (code standards, style)
- [ ] **T028** (P2) Add repo topics/description

### 0.C Python + uv scaffold · *Done when: `uv sync` works, empty pytest passes*
- [ ] **T029** (P0) Create `pyproject.toml` (name, version 1.00, py>=3.13, deps)
- [ ] **T030** (P0) Add `[dependency-groups] dev` (pytest, pytest-cov, ruff)
- [ ] **T031** (P0) Add `fastmcp` dependency
- [ ] **T032** (P0) Run `uv sync`; commit `uv.lock`
- [ ] **T033** (P0) Add `.python-version` (3.13)
- [ ] **T034** (P0) Configure `[tool.ruff]` (line-length 100, target py313)
- [ ] **T035** (P0) Configure `[tool.ruff.lint]` select `E,F,W,I,N,UP,B,C4,SIM`; ignore `E501`
- [ ] **T036** (P0) Configure `[tool.pytest.ini_options]` (testpaths, markers)
- [ ] **T037** (P0) Configure `[tool.coverage.run]` source=src, omit gui/mcp
- [ ] **T038** (P0) Configure `[tool.coverage.report] fail_under = 85`
- [ ] **T039** (P0) Create `src/<pkg>/__init__.py` with `__version__`
- [ ] **T040** (P0) Create `src/<pkg>/__main__.py` entry point
- [ ] **T041** (P0) Create `src/<pkg>/py.typed` marker
- [ ] **T042** (P0) Create `src/<pkg>/constants.py` stub
- [ ] **T043** (P0) Create `tests/conftest.py` + one passing smoke test
- [ ] **T044** (P1) Add `__init__.py` to every sub-package with `__all__`

### 0.D CI & quality gates · *Done when: pipeline green on empty scaffold*
- [ ] **T045** (P1) CI job: `uv run ruff check` (0 violations)
- [ ] **T046** (P1) CI job: `uv run pytest --cov` (gate ≥85%)
- [ ] **T047** (P1) CI job: file-size check (≤150 code lines/file)
- [ ] **T048** (P1) Pre-commit hook: ruff + line-count
- [ ] **T049** (P1) Pre-commit hook: block secrets / large files
- [ ] **T050** (P2) CI badge in README
- [ ] **T051** (P2) `scripts/check_line_limits.py`
- [ ] **T052** (P2) `scripts/sync_versions.py` (code↔config version)

### 0.E Config skeleton · *Done when: config loads + version validates*
- [ ] **T053** (P0) `config/police/` + `config/thief/` dirs (full separation)
- [ ] **T054** (P0) `config/<role>/game.json` skeleton (all Appendix-F sections)
- [ ] **T055** (P0) `config/<role>/game.toml` private skeleton
- [ ] **T056** (P0) `config/<role>/rate_limits.json`
- [ ] **T057** (P0) `shared/config.py` ConfigManager (load JSON overlay TOML)
- [ ] **T058** (P0) `shared/version.py` = 1.00 + runtime validation
- [ ] **T059** (P1) Config schema validation on load (missing key → fail fast)
- [ ] **T060** (P1) Unit tests for ConfigManager + version

---

# PHASE 1 — Base Game Logic (rulebook Ch.3) → M1

### 1.A Constants & types · *Done when: enums frozen + typed*
- [ ] **T061** (P0) `Role` enum (THIEF, POLICE)
- [ ] **T062** (P0) `MoveType` enum (MOVE, BARRIER, HOLD)
- [ ] **T063** (P0) `Direction` enum (N,S,E,W [+ diagonals disabled])
- [ ] **T064** (P0) `DELTAS` map (row,col per direction)
- [ ] **T065** (P0) `ORTHOGONAL` tuple + `directions_from_move_set()`
- [ ] **T066** (P0) Verdict constants (truth/lie), `NONCE_BYTES=16`
- [ ] **T067** (P1) Fixed protocol texts (fallback hint, caught hint, silence)
- [ ] **T068** (P1) Unit tests for constants/enums

### 1.B Board geometry (`domain/board.py`) · *Done when: all geometry tested*
- [ ] **T069** (P0) `Cell` type alias `tuple[int,int]`
- [ ] **T070** (P0) `Board.__init__(size, move_set)`
- [ ] **T071** (P0) `moves` / `diagonal` properties
- [ ] **T072** (P0) `in_bounds(cell)`
- [ ] **T073** (P0) `step(origin, direction, barriers)` → cell|None
- [ ] **T074** (P0) `neighbors(cell, barriers)`
- [ ] **T075** (P0) `legal_moves(origin, barriers)`
- [ ] **T076** (P0) `distance(a,b)` Manhattan (orthogonal)
- [ ] **T077** (P1) Reject off-board / barrier / non-allowed direction
- [ ] **T078** (P1) Property test: legal_moves ⊆ in_bounds
- [ ] **T079** (P1) Unit tests: edges, corners, blocked
- [ ] **T080** (P1) Edge case: fully surrounded cell → no moves

### 1.C Own state (`domain/own_state.py`) · *Done when: state transitions tested*
- [ ] **T081** (P0) `OwnGameState(role, start, board_size, move_set)`
- [ ] **T082** (P0) Track `position`, `visited`, `step_number`
- [ ] **T083** (P0) Track `barriers` set + `my_barriers` count
- [ ] **T084** (P0) `apply_move(move_type, direction)` mutation
- [ ] **T085** (P0) Barrier placement validity (1 step away, in bounds)
- [ ] **T086** (P1) Prevent placing barrier on own cell
- [ ] **T087** (P1) Update visited only on MOVE (not HOLD)
- [ ] **T088** (P1) Serializable snapshot for logging
- [ ] **T089** (P1) Unit tests for each transition
- [ ] **T090** (P2) Edge case: barrier quota exhausted

### 1.D Rules (`domain/rules.py`) · *Done when: all end conditions tested*
- [ ] **T091** (P0) `GameRules(max_steps)`
- [ ] **T092** (P0) `thief_result(state)` → 'survival'|None
- [ ] **T093** (P0) `is_captured(state, claim)` honest capture answer
- [ ] **T094** (P0) No-legal-move → thief caught
- [ ] **T095** (P0) Barrier-on-thief-cell → capture
- [ ] **T096** (P1) Survival threshold reached → thief wins
- [ ] **T097** (P1) Unit tests: capture on cell
- [ ] **T098** (P1) Unit tests: trapped thief
- [ ] **T099** (P1) Unit tests: survival at exactly max_steps
- [ ] **T100** (P2) Edge case: simultaneous end conditions

### 1.E Scoring (`domain/scoring.py`) · *Done when: matches Appendix F*
- [ ] **T101** (P0) `score_subgame(result, roles, scoring)`
- [ ] **T102** (P0) Capture → cop 20 / thief 5
- [ ] **T103** (P0) Survival → cop 5 / thief 10
- [ ] **T104** (P0) Technical loss → 0/0
- [ ] **T105** (P0) `aggregate(subgame_scores, tie_score)` series
- [ ] **T106** (P0) Tie rule → 2 each on series tie
- [ ] **T107** (P1) `winner_group` / `sub_games_won` computation
- [ ] **T108** (P1) Unit tests each outcome
- [ ] **T109** (P1) Unit tests series aggregate + tie
- [ ] **T110** (P2) Property: scores never negative

### 1.F Single-process harness · *Done when: M1 observed*
- [ ] **T111** (P0) Local game loop (no network) wiring board+rules+scoring
- [ ] **T112** (P0) Two `OwnGameState` (cop+thief) on one board
- [ ] **T113** (P1) Deterministic scripted moves for a demo game
- [ ] **T114** (P1) Assert capture ends game + scores
- [ ] **T115** (P1) Assert survival ends game + scores
- [ ] **T116** (P2) CLI flag to run the local demo
- [ ] **T117** (P0) **M1**: two agents move legally + capture on one board

### 1.G Phase-1 tests & quality
- [ ] **T118** (P0) `tests/unit/test_board.py`
- [ ] **T119** (P0) `tests/unit/test_own_state.py`
- [ ] **T120** (P0) `tests/unit/test_rules.py`
- [ ] **T121** (P0) `tests/unit/test_scoring.py`
- [ ] **T122** (P0) `tests/unit/test_constants.py`
- [ ] **T123** (P1) Coverage ≥85% for Phase-1 modules
- [ ] **T124** (P1) Ruff clean for Phase-1
- [ ] **T125** (P1) All Phase-1 files ≤150 lines
- [ ] **T126** (P2) Docstrings on all Phase-1 public functions
- [ ] **T127** (P2) Update `TODO.md` statuses
- [ ] **T128** (P2) Tag internal milestone `m1`
- [ ] **T129** (P2) Update README run instructions for demo
- [ ] **T130** (P2) Record Phase-1 decisions in ADR log

---

# PHASE 2 — MCP Infrastructure (rulebook Ch.2) → M2

### 2.A Protocol (`domain/protocol.py`) · *Done when: messages round-trip*
- [ ] **T131** (P0) `TurnMessage` dataclass (step, commit, reveal, hint, turn token)
- [ ] **T132** (P0) `to_dict()` / `from_dict()` canonical
- [ ] **T133** (P0) Turn-token semantics (holder is "green")
- [ ] **T134** (P0) Reveal message shape (move, hint, verdict; nonce withheld)
- [ ] **T135** (P0) Audit message shape (all nonces)
- [ ] **T136** (P1) Capture-claim / capture-response messages
- [ ] **T137** (P1) Scent-field payload `{'r,c': intensity}`
- [ ] **T138** (P1) Message versioning field
- [ ] **T139** (P1) Validation of inbound message schema
- [ ] **T140** (P1) Unit tests: serialize/deserialize round-trip

### 2.B MCP server (`infra/mcp_server.py`) · *Done when: server accepts calls*
- [ ] **T141** (P0) Create `FastMCP` instance per peer
- [ ] **T142** (P0) `@mcp.tool receive_turn(...)`
- [ ] **T143** (P0) `@mcp.tool receive_reveal(...)`
- [ ] **T144** (P0) `@mcp.tool receive_audit(...)`
- [ ] **T145** (P0) `@mcp.tool receive_negotiation(...)`
- [ ] **T146** (P0) Inbox queues per message type
- [ ] **T147** (P0) `mcp.run(transport=http, host, port)` from config
- [ ] **T148** (P1) Signature verification hook on inbound move
- [ ] **T149** (P1) Reject unverified/malformed calls gracefully
- [ ] **T150** (P1) Server start/stop lifecycle
- [ ] **T151** (P2) Port-in-use pre-check + friendly error

### 2.C MCP client (`infra/mcp_client.py`) · *Done when: calls opponent reliably*
- [ ] **T152** (P0) Connect to opponent URL from config
- [ ] **T153** (P0) `send_turn()` / `send_reveal()` / `send_audit()`
- [ ] **T154** (P0) Retry until opponent server is up (start-order agnostic)
- [ ] **T155** (P0) Connect timeout + retry interval from config
- [ ] **T156** (P1) `poll_turn(interval)` for inbound
- [ ] **T157** (P1) Audit send timeout handling
- [ ] **T158** (P1) Transport drain on shutdown
- [ ] **T159** (P1) Map transport errors → typed exceptions
- [ ] **T160** (P2) Backoff on repeated failures

### 2.D Transport abstraction · *Done when: SDK talks via one interface*
- [ ] **T161** (P0) `McpTransport` wrapping client + server inboxes
- [ ] **T162** (P1) Interface used by PeerRuntime (no direct MCP in domain)
- [ ] **T163** (P1) Fake/in-memory transport for tests
- [ ] **T164** (P1) Injectable transport (dependency injection)
- [ ] **T165** (P2) Transport metrics (latency, retries)

### 2.E Localhost integration · *Done when: M2 observed*
- [ ] **T166** (P0) Two processes on 8801/8802 exchange a message
- [ ] **T167** (P1) `tests/integration/test_mcp_match.py` (loopback)
- [ ] **T168** (P1) Assert A→B geometric payload received intact
- [ ] **T169** (P0) **M2**: message A→B over localhost verified
- [ ] **T170** (P2) Document ports + run steps in README

### 2.F Phase-2 quality
- [ ] **T171** (P1) Unit tests protocol + client + server (mocked)
- [ ] **T172** (P1) Coverage ≥85% (exclude live MCP I/O per omit)
- [ ] **T173** (P1) Ruff clean; files ≤150 lines
- [ ] **T174** (P1) Docstrings on tools + transport
- [ ] **T175** (P2) Update `PRD_p2p_mcp.md` with final shapes

---

# PHASE 3 — Strategy / Decision (rulebook Ch.6) → M3

### 3.A Brain base (`strategy/brains.py`) · *Done when: base contract tested*
- [ ] **T176** (P0) `Decision` dataclass (move_type, direction, hint, verdict, …)
- [ ] **T177** (P0) `BrainBase.__init__(llm, rng, trash)`
- [ ] **T178** (P0) `decide(state, belief, opponent_hint, …)` → Decision
- [ ] **T179** (P0) `_decide_move(...)` default (step per `_pick_move`, else HOLD)
- [ ] **T180** (P0) `_pick_move(...)` abstract
- [ ] **T181** (P0) Guarantee: move never asks the LLM
- [ ] **T182** (P1) Fallback to HOLD when no legal moves
- [ ] **T183** (P1) Timing/response_seconds capture
- [ ] **T184** (P1) Unit test base decide flow

### 3.B Thief brain · *Done when: evasion policy tested*
- [ ] **T185** (P0) `ThiefBrain` evade: maximize distance to belief peak
- [ ] **T186** (P0) Prefer unvisited cells on ties
- [ ] **T187** (P1) Avoid walking into dead-ends (barrier-aware)
- [ ] **T188** (P1) Corner/edge escape heuristic
- [ ] **T189** (P1) Bluff selection (truth/lie mix)
- [ ] **T190** (P2) Anti-oscillation (no A↔B loops)
- [ ] **T191** (P1) Unit tests thief policy
- [ ] **T192** (P2) Tunable weights via config

### 3.C Police brain · *Done when: chase + barrier tested*
- [ ] **T193** (P0) `PoliceBrain` chase: minimize distance to belief peak
- [ ] **T194** (P0) `_decide_move` barrier vs move decision
- [ ] **T195** (P0) Legal barrier placement (1 step away)
- [ ] **T196** (P1) Barrier quota management (don't self-trap)
- [ ] **T197** (P1) Cut-off / herding barrier placement
- [ ] **T198** (P1) Capture-claim trigger when on thief cell
- [ ] **T199** (P2) Predictive interception (belief look-ahead)
- [ ] **T200** (P1) Unit tests police policy
- [ ] **T201** (P2) Tunable barrier_chance via config

### 3.D Advanced strategy · *Done when: beats greedy baseline*
- [ ] **T202** (P1) Belief-weighted move scoring (not just peak)
- [ ] **T203** (P1) One-step look-ahead (expectimax vs belief)
- [ ] **T204** (P2) Multi-step look-ahead (depth-limited)
- [ ] **T205** (P2) Minimax against opponent belief model
- [ ] **T206** (P2) Trap-detection for thief
- [ ] **T207** (P2) Barrier-network planning for police
- [ ] **T208** (P2) Deception strategy (lie when scent already exposes truth)
- [ ] **T209** (P2) Risk/patience tuning via discount factor
- [ ] **T210** (P1) Benchmark harness: strategy vs random baseline
- [ ] **T211** (P1) Benchmark: strategy vs greedy baseline
- [ ] **T212** (P2) Record win-rate metrics for report

### 3.E Strategy injection · *Done when: swap brain via config*
- [ ] **T213** (P0) `strategy/__init__.py` exports (BrainBase, brains, resolve_brain)
- [ ] **T214** (P0) `resolve_brain(config, role, llm, rng)` factory
- [ ] **T215** (P0) Read `[strategy] thief_class/police_class` selector
- [ ] **T216** (P1) Dotted `package.module:Class` loader
- [ ] **T217** (P1) Fail-fast on non-BrainBase / bad selector
- [ ] **T218** (P1) Unset selector → default heuristic
- [ ] **T219** (P1) Unit tests factory (valid/invalid)

### 3.F Reproducibility
- [ ] **T220** (P1) Seed RNG from config `play.seed`
- [ ] **T221** (P1) Same seed → identical game
- [ ] **T222** (P2) Seed logged into artifacts

### 3.G Phase-3 quality
- [ ] **T223** (P1) `tests/unit/test_brains.py`
- [ ] **T224** (P1) `tests/unit/test_strategy.py`
- [ ] **T225** (P0) **M3**: shortest path to a known target, no manual help
- [ ] **T226** (P1) Coverage ≥85%; ruff clean; files ≤150
- [ ] **T227** (P2) Update `PRD_strategy.md` with final policy
- [ ] **T228** (P2) Record strategy ADR

---

# PHASE 4 — Language + Scent + Belief (rulebook Ch.4, Ch.6) → M4

### 4.A Smell field (`domain/smell.py`) · *Done when: matches book formula*
- [ ] **T229** (P0) `SmellField(board_size, grid_size, decay, min_center)`
- [ ] **T230** (P0) `_radial(center, intensity)` 5×5 emission
- [ ] **T231** (P0) Radial falloff from center 0.9
- [ ] **T232** (P0) `deposit(center, intensity)` max-merge into trail
- [ ] **T233** (P0) **Multiplicative decay** `τ←(1−ρ)·τ` (book, not subtractive)
- [ ] **T234** (P0) New-emission term `+Δτ` then `max(0,·)` clip
- [ ] **T235** (P0) `absorb(cells)` merge received field (max)
- [ ] **T236** (P0) `decay_all()` each full turn
- [ ] **T237** (P0) `intensity_at(cell)` / `strongest_cell()`
- [ ] **T238** (P0) `snapshot()` `{'r,c': intensity}` (never send position)
- [ ] **T239** (P1) Enforce `min_center` on deposit
- [ ] **T240** (P1) Clamp intensities to [0, 0.9]
- [ ] **T241** (P1) Unit test emission field values
- [ ] **T242** (P1) Unit test decay curve over N turns
- [ ] **T243** (P1) Unit test absorb/merge
- [ ] **T244** (P2) Validate against book worked example (0.9→0.81)

### 4.B Belief map (`domain/belief.py`) · *Done when: belief peaks near scent*
- [ ] **T245** (P0) `BeliefGrid(board_size, smell_trust, orthogonal)`
- [ ] **T246** (P0) Uniform prior init
- [ ] **T247** (P0) `observe_smell(cells)` Bayes update `×(1+trust·intensity)`
- [ ] **T248** (P0) `_normalize()` with degenerate reset
- [ ] **T249** (P0) `diffuse()` spread mass to neighborhood
- [ ] **T250** (P0) Neighborhood matches move set (von Neumann for orthogonal)
- [ ] **T251** (P0) `exclude(cell)` rule out (I'm here, no capture)
- [ ] **T252** (P0) `most_likely()` argmax
- [ ] **T253** (P0) `as_matrix()` for GUI
- [ ] **T254** (P1) Hint-based update (trust factor for verbal claim)
- [ ] **T255** (P1) Lower trust when hint contradicts scent
- [ ] **T256** (P1) Unit test observe→peak location
- [ ] **T257** (P1) Unit test diffuse conserves mass
- [ ] **T258** (P1) Unit test exclude + normalize
- [ ] **T259** (P2) Belief entropy metric for analysis
- [ ] **T260** (P2) Edge case: all-zero belief → reset uniform

### 4.C Hint decoding · *Done when: contradiction detection works*
- [ ] **T261** (P0) Parse opponent NL hint → direction/landmark cue
- [ ] **T262** (P1) Map landmark → board region (map_area aware)
- [ ] **T263** (P1) Compare claim vs scent field (expected intensity)
- [ ] **T264** (P1) Compute trust coefficient from contradiction
- [ ] **T265** (P1) Feed trust into belief update
- [ ] **T266** (P2) Track opponent's lie frequency (profiling)
- [ ] **T267** (P1) Unit test contradiction case ("north" vs SE scent)

### 4.D Trash-talk template (`strategy/trash_talk.py`) · *Done when: 0-token default*
- [ ] **T268** (P0) `TrashTalk(rng, max_words)` template provider
- [ ] **T269** (P0) Thief/police line banks
- [ ] **T270** (P0) Landmark vocab per map_area + generic fallback
- [ ] **T271** (P0) `say(...)` → (hint, verdict, reasoning, prompt)
- [ ] **T272** (P0) `_cap()` enforce ≤15-word limit
- [ ] **T273** (P0) Lie rate (~40% thief) → verdict
- [ ] **T274** (P1) Zero tokens / offline guarantee
- [ ] **T275** (P1) Unit test word cap + verdict
- [ ] **T276** (P2) Custom template subclass hook

### 4.E LLM providers (optional) · *Done when: error → template fallback*
- [ ] **T277** (P1) `LlmTrashTalk` wrapper (every_n_steps)
- [ ] **T278** (P1) `resolve_trash_talk(config, rng, llm)` factory
- [ ] **T279** (P1) `template` provider path (default)
- [ ] **T280** (P2) `ollama` asker (localhost:11434, stdlib http)
- [ ] **T281** (P2) `claude_api` asker (anthropic, small model, ~200 tok)
- [ ] **T282** (P2) `claude_cli` asker (reuse `claude -p`)
- [ ] **T283** (P1) System prompt pins map_area + word limit
- [ ] **T284** (P1) Strict-JSON parse `{message, verdict, reasoning}`
- [ ] **T285** (P1) Deadline-bounded call (thread + timeout)
- [ ] **T286** (P0) Any error/timeout → template fallback (never stall)
- [ ] **T287** (P1) Token accounting per call
- [ ] **T288** (P1) Log full system+user prompt for audit
- [ ] **T289** (P1) Unit test fallback on bad reply
- [ ] **T290** (P2) `.env-example` LLM keys documented

### 4.F Integration
- [ ] **T291** (P0) Wire smell+belief+hint into `PeerRuntime` turn
- [ ] **T292** (P1) Emit own scent each move; absorb opponent's
- [ ] **T293** (P1) Belief-driven move uses updated map
- [ ] **T294** (P1) Measure capture-rate lift vs Phase-3 baseline
- [ ] **T295** (P0) **M4**: belief updates + truth/lie hints working

### 4.G Phase-4 quality
- [ ] **T296** (P1) `tests/unit/test_smell.py`
- [ ] **T297** (P1) `tests/unit/test_belief.py`
- [ ] **T298** (P1) `tests/unit/test_trash_talk.py`
- [ ] **T299** (P1) `tests/unit/test_llm_provider.py` (mocked)
- [ ] **T300** (P1) Coverage ≥85%; ruff clean; files ≤150
- [ ] **T301** (P1) Docstrings on smell/belief math ("why")
- [ ] **T302** (P2) Update `PRD_scent_belief.md`
- [ ] **T303** (P2) Note scent-decay divergence-from-reference in ADR-5
- [ ] **T304** (P2) Update `TODO.md` statuses

---

# PHASE 5 — Cloud Exposure & Tunneling (rulebook Ch.2) → M5

### 5.A Tunnel setup · *Done when: public URL reachable*
- [ ] **T305** (P0) Choose tunnel (ngrok / Localtonet); document setup
- [ ] **T306** (P0) Script/instructions to expose `my_port` publicly
- [ ] **T307** (P0) Put public URL into opponent's `game.toml`
- [ ] **T308** (P1) Health-check endpoint / readiness probe
- [ ] **T309** (P1) Handle tunnel restart / URL change
- [ ] **T310** (P1) Document firewall/NAT prerequisites
- [ ] **T311** (P2) Fallback tunnel provider
- [ ] **T312** (P2) `.env-example` tunnel token placeholder

### 5.B Negotiation / handshake (`peer/handshake.py`) · *Done when: refuses on mismatch*
- [ ] **T313** (P0) `terms_from_config()` extract shared game terms
- [ ] **T314** (P0) Canonical-JSON of terms + SHA-256
- [ ] **T315** (P0) `validate_agreement()` (fail before opening port)
- [ ] **T316** (P0) Exchange signatures with opponent
- [ ] **T317** (P0) Verify opponent signature == our terms hash
- [ ] **T318** (P0) Refuse to play on any mismatch
- [ ] **T319** (P0) Agree shared `game_id` + `game_uid`
- [ ] **T320** (P1) Exchange identities (members, repos, MCP URLs)
- [ ] **T321** (P1) Agree `num_games` (both must match)
- [ ] **T322** (P1) Persist agreement for artifacts
- [ ] **T323** (P1) Unit test: matching terms → agree
- [ ] **T324** (P1) Unit test: mismatched terms → refuse
- [ ] **T325** (P2) Timeout handling during handshake
- [ ] **T326** (P2) Re-negotiation on new sub-game

### 5.C Remote play robustness · *Done when: full remote game completes*
- [ ] **T327** (P1) Latency tolerance (timeouts from config)
- [ ] **T328** (P1) Reconnect mid-game after transient drop
- [ ] **T329** (P1) Idempotent message handling (no double-apply)
- [ ] **T330** (P1) Clock/timezone handling in timestamps
- [ ] **T331** (P2) Graceful opponent-quit handling
- [ ] **T332** (P2) Network metrics logged

### 5.D Environment separation · *Done when: no cross-state*
- [ ] **T333** (P0) Cop & Thief in separate processes
- [ ] **T334** (P0) Separate config dirs; no shared module state
- [ ] **T335** (P1) Assert no shared memory/global leakage
- [ ] **T336** (P2) Lint rule / review checklist for isolation

### 5.E Phase-5 quality
- [ ] **T337** (P1) `tests/unit/test_negotiation.py`
- [ ] **T338** (P1) `tests/integration/` remote-sim (mocked transport)
- [ ] **T339** (P0) **M5**: full game vs remote peer over tunnel
- [ ] **T340** (P1) Coverage ≥85%; ruff clean; files ≤150
- [ ] **T341** (P2) Update `PRD_p2p_mcp.md` with handshake
- [ ] **T342** (P2) Document remote-play run in README

---

# PHASE 6 — Security, Crypto & Reliability (rulebook Ch.5, Ch.8) → M6

### 6.A Commit-reveal (`domain/crypto.py`) · *Done when: commit/verify round-trips*
- [ ] **T343** (P0) `_canonical(payload)` JSON sort_keys, fixed separators
- [ ] **T344** (P0) `CommitReveal.commit_of(payload, nonce)` SHA-256
- [ ] **T345** (P0) `seal(payload)` fresh nonce via `secrets.token_hex`
- [ ] **T346** (P0) `verify(payload, nonce, commit)` + `compare_digest`
- [ ] **T347** (P0) Raise `CryptoError` on mismatch
- [ ] **T348** (P0) Payload includes state, move, intent, nonce (+ hint, step)
- [ ] **T349** (P1) Deterministic bytes across machines (interop)
- [ ] **T350** (P1) Unit test commit→verify OK
- [ ] **T351** (P1) Unit test tampered payload → fail
- [ ] **T352** (P1) Unit test nonce uniqueness
- [ ] **T353** (P2) Fuzz test canonicalization stability

### 6.B Sealing per step (`peer/sealing.py`) · *Done when: log holds sealed records*
- [ ] **T354** (P0) Seal each step → `{payload, nonce, commit}`
- [ ] **T355** (P0) Send only commit during play
- [ ] **T356** (P0) Reveal move+hint (nonce withheld) at reveal step
- [ ] **T357** (P0) Hold all nonces until end-of-game
- [ ] **T358** (P1) `identity_from_config()` + `now_iso()`
- [ ] **T359** (P1) Append records to runtime log
- [ ] **T360** (P1) Unit test seal/reveal ordering

### 6.C Audit · *Done when: tampered log detected*
- [ ] **T361** (P0) `audit_records(records)` re-verify every step
- [ ] **T362** (P0) Return {passed, verified_steps, failed_steps}
- [ ] **T363** (P0) Exchange revealed logs at end
- [ ] **T364** (P0) Mutual audit: both re-verify opponent log
- [ ] **T365** (P0) Any mismatch → `tamper_forfeit` (0 points)
- [ ] **T366** (P1) Mutual-agreement signature over result
- [ ] **T367** (P1) Unit test audit pass
- [ ] **T368** (P1) Unit test audit fail on 1 bad step
- [ ] **T369** (P2) Audit performance for full 35-step game

### 6.D Step-0 declaration (`shared/sysinfo.py`) · *Done when: signed spec in declaration*
- [ ] **T370** (P0) Collect OS / CPU cores+freq
- [ ] **T371** (P0) Collect RAM capacity
- [ ] **T372** (P0) Collect GPU / VRAM (if any)
- [ ] **T373** (P0) Collect LLM model + code version
- [ ] **T374** (P0) Record GitHub commit hash of the running code
- [ ] **T375** (P0) Pack to JSON + seal (sealed_spec_record)
- [ ] **T376** (P1) Token budget declaration
- [ ] **T377** (P1) Unit test sysinfo shape (mock platform)
- [ ] **T378** (P2) Cross-platform (Windows/Linux) handling

### 6.E State machine (`peer/`) · *Done when: illegal transitions raise*
- [ ] **T379** (P0) `GamePhaseMachine` with TRANSITIONS table
- [ ] **T380** (P0) States: WAITING→COMPUTING→COMMITTING→AWAITING_REVEAL→VERIFYING
- [ ] **T381** (P0) Error edges → TECHNICAL_LOSS (terminal)
- [ ] **T382** (P0) Reject illegal transition (raise)
- [ ] **T383** (P1) Drive runtime turn loop via the machine
- [ ] **T384** (P1) Unit test each legal transition
- [ ] **T385** (P1) Unit test illegal transition raises
- [ ] **T386** (P2) Diagram in `PLAN.md` matches code

### 6.F Reliability patterns · *Done when: opponent failure → defined end*
- [ ] **T387** (P0) Deadline tracker: expiry on every MCP request
- [ ] **T388** (P0) Missed deadline → retry or technical loss
- [ ] **T389** (P0) Watchdog: heartbeat monitor (60s)
- [ ] **T390** (P0) Watchdog → controlled shutdown + persist state
- [ ] **T391** (P0) Orchestrator single-gateway to all subsystems
- [ ] **T392** (P1) No module-to-module direct calls (gateway only)
- [ ] **T393** (P1) Timeout → `timeout` result, winner = self
- [ ] **T394** (P1) Clean queue drain on failure
- [ ] **T395** (P1) Unit test deadline expiry
- [ ] **T396** (P1) Unit test watchdog trip
- [ ] **T397** (P2) Recovery from persisted state
- [ ] **T398** (P2) Chaos test: kill opponent mid-turn

### 6.G Phase-6 quality
- [ ] **T399** (P1) `tests/unit/test_crypto.py`
- [ ] **T400** (P1) `tests/unit/test_runtime.py` (state machine)
- [ ] **T401** (P1) `tests/unit/test_sysinfo.py`
- [ ] **T402** (P1) `tests/unit/test_deadline_controls.py`
- [ ] **T403** (P0) **M6**: commit-reveal + mutual audit + Step-0 pass
- [ ] **T404** (P1) Coverage ≥85%; ruff clean; files ≤150
- [ ] **T405** (P1) Docstrings on crypto/state machine
- [ ] **T406** (P2) Update `PRD_commit_reveal.md`
- [ ] **T407** (P2) Security self-review (secrets, canonicalization)

---

# PHASE 7 — Reporting, GUI & Replay (rulebook Ch.9, Ch.7, App.A) → M7

### 7.A Report artifacts (`report/`) · *Done when: 4 files validate vs Appendix F*
- [ ] **T408** (P0) `artifact_schemas.py` — schemas for the 4 files
- [ ] **T409** (P0) Declaration writer (identities, repos, MCP, hardware, times)
- [ ] **T410** (P0) Config artifact writer (agreed config + `config_sha256`)
- [ ] **T411** (P0) Log artifact writer (records + summary + audit)
- [ ] **T412** (P0) Result artifact writer (per-subgame + aggregate + signature)
- [ ] **T413** (P0) Filenames derived from `game_id`/`game_uid`
- [ ] **T414** (P0) One shared `game_uid` stitches all four
- [ ] **T415** (P1) Per-group `logs/<group_id>/` subfolders
- [ ] **T416** (P1) Include **all 4 GitHub links** (2 per team — ours + opponent's, rule 49) + commit ids + total tokens
- [ ] **T417** (P1) `emit_series()` writes all artifacts
- [ ] **T418** (P1) Schema-validate output before write
- [ ] **T419** (P1) `tests/unit/test_artifacts.py`
- [ ] **T420** (P1) `tests/unit/test_report_writer.py`
- [ ] **T421** (P2) Golden-file compare vs sample-run format
- [ ] **T422** (P2) Human-readable `_schema` notes in each file
- [ ] **T423** (P1) `game_ids.py` helper (id/uid derivation)
- [ ] **T424** (P2) Back-compat legacy per-role log
- [ ] **T425** (P2) Redact secrets from artifacts

### 7.B Gatekeeper (`shared/gatekeeper.py`) · *Done when: overflow queues, no crash*
- [ ] **T426** (P0) `ApiGatekeeper(config, service)`
- [ ] **T427** (P0) `execute(api_call, *args)` rate-limited
- [ ] **T428** (P0) Read limits from `rate_limits.json` (never hardcode)
- [ ] **T429** (P0) Quota manager (daily cap → block before send)
- [ ] **T430** (P0) Token-bucket limiter `tokens←min(C,tokens+r·Δt)`
- [ ] **T431** (P0) DOS detector (loop/burst → LOCKED)
- [ ] **T432** (P0) FIFO queue on overflow (not reject)
- [ ] **T433** (P1) Max queue depth + backpressure alert
- [ ] **T434** (P1) Retry on transient errors (max_retries)
- [ ] **T435** (P1) Drain mechanism on limit reset
- [ ] **T436** (P1) `get_queue_status()` metrics + logging
- [ ] **T437** (P1) 429 handling / backoff
- [ ] **T438** (P1) `tests/unit/test_gatekeeper.py`
- [ ] **T439** (P1) `tests/unit/test_rate_limiter.py`
- [ ] **T440** (P2) Circuit-breaker open/half-open/closed states

### 7.C Rate limiter (`shared/rate_limiter.py`)
- [ ] **T441** (P0) `RateLimiter(limits, queue)` acquire/release
- [ ] **T442** (P1) Concurrent-request cap
- [ ] **T443** (P1) `requests_per_minute` window
- [ ] **T444** (P1) Thread-safe token accounting
- [ ] **T445** (P2) Monotonic-clock refill

### 7.D Email reporting (`infra/email_sender.py`, App.A) · *Done when: result emailed*
- [ ] **T446** (P0) OAuth2 flow (`InstalledAppFlow`, `token.json`)
- [ ] **T447** (P0) Scope = `gmail.send` only (least privilege)
- [ ] **T448** (P0) Build MIME message + base64url encode
- [ ] **T449** (P0) `send_report(result_json, subject)` to `[Agent Reporting Address]`
- [ ] **T450** (P0) Route send through Gatekeeper
- [ ] **T451** (P0) Attach result JSON (not plaintext)
- [ ] **T452** (P1) `mode = draft` for testing
- [ ] **T453** (P1) `credentials.json`/`token.json` in `.gitignore`
- [ ] **T454** (P1) Both teams send separately (each its own copy)
- [ ] **T455** (P1) Refresh-token auto-renew
- [ ] **T456** (P1) `tests/unit/test_email_sender.py` (mock API)
- [ ] **T457** (P2) Retry/backoff on 429 via gatekeeper
- [ ] **T458** (P2) `.env-example` OAuth placeholders
- [ ] **T459** (P2) Setup guide in README (5 OAuth steps)

### 7.E Live GUI (`gui/`) · *Done when: local-truth heatmap screenshot*
- [ ] **T460** (P1) `window.py` main Tkinter window
- [ ] **T461** (P1) `board_view.py` grid render (own pos, visited, barriers)
- [ ] **T462** (P1) Belief heatmap render (white→red)
- [ ] **T463** (P1) **Local truth only** (never opponent's true cell)
- [ ] **T464** (P1) Turn banner (green YOUR TURN / grey LOCKED)
- [ ] **T465** (P1) Info panel (step, tokens, opponent hint, my verdict, commit)
- [ ] **T466** (P1) Controls: Start/Pause/Play/Stop/Restart/Quit
- [ ] **T467** (P1) Sub-game selector (1–6)
- [ ] **T468** (P2) Step-time-budget slider (0–60s)
- [ ] **T469** (P2) Help→About (versions, license, host spec)
- [ ] **T470** (P2) Help→Open guidelines PDF
- [ ] **T471** (P1) Input locked when not your turn (no race)
- [ ] **T472** (P1) `tests/unit/test_live_controls.py`
- [ ] **T473** (P2) Screenshot every GUI state for report

### 7.F Replay viewer (`gui/replay.py`) · *Done when: Verified OK + TAMPERED detected*
- [ ] **T474** (P0) Load standardized `log_<game_id>_gNN.json`
- [ ] **T475** (P0) Play / Pause / Step controls
- [ ] **T476** (P0) Re-verify each commit hash live
- [ ] **T477** (P0) Green "Verified OK" stamp on match
- [ ] **T478** (P0) Red "TAMPERED" banner + invalidate on mismatch
- [ ] **T479** (P1) Load sibling opponent log → both agents on board
- [ ] **T480** (P1) Fallback to belief heatmap if sibling missing
- [ ] **T481** (P1) Go-to-step + Restart + sub-game selector
- [ ] **T482** (P1) Frozen-track banner on unequal step counts
- [ ] **T483** (P1) Show sealed host-spec declaration + mutual audit
- [ ] **T484** (P1) `replay_data.py` normalize both log formats
- [ ] **T485** (P1) `tests/unit/test_replay_data.py`
- [ ] **T486** (P1) `tests/unit/test_replay_normalize.py`
- [ ] **T487** (P0) Screenshot "Verified OK" for submission
- [ ] **T488** (P2) Demo a tampered log → red banner screenshot
- [ ] **T489** (P0) **M7**: Gmail JSON + GUI + Replay (Verified OK) working

### 7.G SDK & CLI wiring
- [ ] **T490** (P0) `sdk/sdk.py` `SimulationSdk` facade (single entry point)
- [ ] **T491** (P0) `run_peer(role, ...)` whole series
- [ ] **T492** (P0) `sdk/series.py` `run_series` (roles alternate)
- [ ] **T493** (P0) `cli.py` `peer` / `replay` subcommands
- [ ] **T494** (P1) CLI flags `--role --stub-llm --no-gui`
- [ ] **T495** (P1) No business logic in CLI/GUI (delegate to SDK)
- [ ] **T496** (P1) `tests/unit/test_cli.py` + `test_sdk.py` + `test_series.py`
- [ ] **T497** (P2) `load_log()` helper for replay

---

# PHASE 8 — Quality, Research, Docs & Submission

### 8.A Final quality gates · *Done when: all gates green in both repos*
- [ ] **T498** (P0) Coverage ≥85% whole project
- [ ] **T499** (P0) `ruff check` 0 violations
- [ ] **T500** (P0) Every code file ≤150 lines
- [ ] **T501** (P0) Every module/public fn has docstring
- [ ] **T502** (P1) No hardcoded config values (all via config/env)
- [ ] **T503** (P1) No secrets in code or history
- [ ] **T504** (P1) `pyproject.toml` + `uv.lock` committed
- [ ] **T505** (P1) No `pip`/`venv`/`requirements.txt` anywhere
- [ ] **T506** (P1) All commands run via `uv run`
- [ ] **T507** (P1) `__init__.py` + `__all__` + `__version__` everywhere
- [ ] **T508** (P1) Relative imports only (no absolute paths)
- [ ] **T509** (P2) Thread-safety review for parallel code
- [ ] **T510** (P2) ISO/IEC 25010 self-assessment table
- [ ] **T511** (P2) Automated test report (pass/fail) saved

### 8.B Research notebook (`notebooks/`) · *Done when: sensitivity plots produced*
- [ ] **T512** (P1) Analysis notebook scaffold (Jupyter)
- [ ] **T513** (P1) Sensitivity: scent decay ρ vs capture rate
- [ ] **T514** (P1) Sensitivity: `smell_trust_weight` vs belief accuracy
- [ ] **T515** (P1) Sensitivity: police `barrier_chance` vs capture rate
- [ ] **T516** (P1) Sensitivity: board size vs game length
- [ ] **T517** (P2) OAT / partial-derivative parameter analysis
- [ ] **T518** (P1) Heatmap of belief accuracy over turns
- [ ] **T519** (P1) Win-rate: our strategy vs random/greedy baselines
- [ ] **T520** (P1) Line/bar charts with labels + captions
- [ ] **T521** (P2) Box plots of score distributions
- [ ] **T522** (P2) Save figures to `assets/` (high-res)
- [ ] **T523** (P2) LaTeX equations for scent/belief/Bayes
- [ ] **T524** (P2) Academic references in notebook

### 8.C Cost analysis · *Done when: token cost table in report*
- [ ] **T525** (P1) Count input/output tokens per provider
- [ ] **T526** (P1) Cost-per-million table by model
- [ ] **T527** (P1) Estimate series cost (~200k budget)
- [ ] **T528** (P2) Optimization notes (template=0 tokens, every_n_steps)
- [ ] **T529** (P2) Budget alerts / monitoring notes

### 8.D README academic report · *Done when: all 6 sections present, both repos*
- [ ] **T530** (P0) §1 Selected Dec-POMDP model
- [ ] **T531** (P0) §2 FastMCP communication dilemma (queues, failures, orchestrator, gatekeeper)
- [ ] **T532** (P0) §3 Implemented strategy (heuristics/belief/optional RL)
- [ ] **T533** (P1) §4 Learning curves (only if RL used)
- [ ] **T534** (P0) §5 Screenshots: Live GUI belief map + Replay Verified OK
- [ ] **T535** (P0) §6 Link to companion repo (Cop↔Thief)
- [ ] **T536** (P1) Install / usage / config / examples / license sections
- [ ] **T537** (P1) Troubleshooting section
- [ ] **T538** (P2) Architecture diagrams embedded
- [ ] **T539** (P2) Demo GIF / video link

### 8.E Process docs
- [ ] **T540** (P1) Complete `docs/PROMPTS.md` (significant AI prompts, context, outputs)
- [ ] **T541** (P1) Finalize ADR records (rationale, trade-offs)
- [ ] **T542** (P1) C4 + UML diagrams in `PLAN.md` / `docs/`
- [ ] **T543** (P2) Deployment/run diagram
- [ ] **T544** (P2) Extension-points doc (plugin hooks)

### 8.F League operations · *Done when: ≥2 games vs ≥2 teams reported*
- [ ] **T545** (P0) Find ≥2 opponent teams
- [ ] **T546** (P0) Agree shared `game.json` per pair
- [ ] **T547** (P0) Warm-up game (uncounted) per opponent
- [ ] **T548** (P0) Play official game vs team A
- [ ] **T549** (P0) Play official game vs team B
- [ ] **T550** (P0) Agree result with each opponent
- [ ] **T551** (P0) Send own JSON report per game (both sides)
- [ ] **T552** (P0) Declare games-played count truthfully each game
- [ ] **T553** (P0) Record exact commit hash used per game
- [ ] **T554** (P1) One game per opponent (no repeats for score)
- [ ] **T555** (P1) Attach each game's config to repo
- [ ] **T556** (P1) Verify mutual audit passed before agreeing result
- [ ] **T557** (P2) Log league standings locally

### 8.G Submission · *Done when: both repos tagged + submitted*
- [ ] **T558** (P0) Fill team members/IDs in PRD + declaration
- [ ] **T559** (P0) Fill both repo URLs everywhere referenced
- [ ] **T560** (P0) Cross-link READMEs verified
- [ ] **T561** (P0) `git tag -a v1.0-submission` in Cop repo
- [ ] **T562** (P0) `git tag -a v1.0-submission` in Thief repo
- [ ] **T563** (P0) Push tags to both remotes
- [ ] **T564** (P0) Repos shared with lecturer / public
- [ ] **T565** (P0) `/config` with PRD files, PLAN, TODO present
- [ ] **T566** (P0) No secrets committed (final scan)
- [ ] **T567** (P0) Download Moodle Word template → fill → save as PDF (don't move fields)
- [ ] **T568** (P0) Each member submits separately in Moodle
- [ ] **T569** (P0) Unique 8-char team code (no spaces) in filename
- [ ] **T570** (P1) Self-assessment (code quality only)
- [ ] **T571** (P1) Final pre-submission checklist (rulebook Ch.11)
- [ ] **T572** (P2) Verify grader can run from a clean clone

### 8.H Cross-cutting continuous (revisit every phase)
- [ ] **T573** (P0) Keep `TODO.md` statuses current
- [ ] **T574** (P0) Update relevant PRD on each mechanism change
- [ ] **T575** (P1) Update README as features land
- [ ] **T576** (P1) Add test file for every new module (TDD)
- [ ] **T577** (P1) At least one test per public function
- [ ] **T578** (P1) Cover standard path + error cases
- [ ] **T579** (P1) Mock all external deps in tests
- [ ] **T580** (P1) Keep test files ≤150 lines too
- [ ] **T581** (P1) `conftest.py` shared fixtures
- [ ] **T582** (P1) Run full suite before every merge
- [ ] **T583** (P1) Code review via PR before merge to main
- [ ] **T584** (P1) Meaningful commit messages
- [ ] **T585** (P1) Feature branches per capability
- [ ] **T586** (P2) Bump versions on significant change
- [ ] **T587** (P2) Keep `uv.lock` in sync
- [ ] **T588** (P2) Periodic dependency review
- [ ] **T589** (P2) Backup logs / results

### 8.I Robustness & edge cases
- [ ] **T590** (P1) Handle malformed inbound message (reject, no crash)
- [ ] **T591** (P1) Handle opponent illegal move (reject + record)
- [ ] **T592** (P1) Handle duplicate/replayed message
- [ ] **T593** (P1) Handle tunnel drop mid-game
- [ ] **T594** (P1) Handle Gmail 429 / quota exceeded
- [ ] **T595** (P1) Handle LLM provider unavailable
- [ ] **T596** (P1) Handle config version mismatch
- [ ] **T597** (P1) Handle port already in use
- [ ] **T598** (P2) Handle disk-full when writing artifacts
- [ ] **T599** (P2) Handle clock skew between peers
- [ ] **T600** (P2) Handle Unicode in hints/landmarks
- [ ] **T601** (P2) Graceful degradation messages everywhere

### 8.J Documentation of edge cases & results
- [ ] **T602** (P1) Document each edge case (input → expected response)
- [ ] **T603** (P1) Screenshot faults where relevant
- [ ] **T604** (P1) Save logs of successful + failed runs
- [ ] **T605** (P1) Expected results per test documented
- [ ] **T606** (P2) Automated coverage report artifact
- [ ] **T607** (P2) Defensive-programming review pass

### 8.K Final verification (both repos)
- [ ] **T608** (P0) Fresh clone → `uv sync` → tests pass
- [ ] **T609** (P0) Fresh clone → run a full local game
- [ ] **T610** (P0) Fresh clone → replay verifies OK
- [ ] **T611** (P1) Ruff + coverage gates pass in CI
- [ ] **T612** (P1) All 150-line checks pass
- [ ] **T613** (P1) All secrets scan clean
- [ ] **T614** (P1) All docs present + linked
- [ ] **T615** (P1) All 4 JSON artifacts produced + valid
- [ ] **T616** (P1) Live GUI + Replay screenshots attached
- [ ] **T617** (P0) Both repos tagged `v1.0-submission`
- [ ] **T618** (P1) League reports sent for all official games
- [ ] **T619** (P1) Moodle PDF submitted per member
- [ ] **T620** (P0) Final sign-off: PRD/PLAN/TODO reconciled with code

---

# ADDENDUM A — v2.10 review-pass tasks (gaps found vs. Material sources)

### A.1 Acknowledge protocol step (rulebook Fig. 6: Commit → Ack → Reveal → Final-Reveal)
- [ ] **T621** (P0) Add Acknowledge message to `domain/protocol.py` (or ack as `receive_turn`'s synchronous return — document the choice)
- [ ] **T622** (P0) Runtime waits for opponent's ack after commit, before revealing; reveal-before-ack is rejected (test)

### A.2 Natural-language-only hint channel (Appendix E rules 26–27)
- [ ] **T623** (P0) Outbound hint validation: natural language only — block coordinate/numeric location encodings before send
- [ ] **T624** (P1) Inbound hint sanity check: flag + log a coordinate-protocol hint as a rule violation

### A.3 League integrity & series
- [ ] **T625** (P0) Official matches: set `network_and_league.num_games = 6` in the signed `game.json` (Fixed, Appendix F Table 18; dev may use 1)
- [ ] **T626** (P1) Declaration artifact includes truthful games-played-count field vs this opponent
- [ ] **T627** (P1) Result-agreement flow: detect conflicting results → mark game disqualified (0/0) in the result artifact
- [ ] **T628** (P1) Record diversity-bonus (10) context in the result/league log (first counted game per opponent)

### A.4 Docs & structure follow-ups
- [ ] **T629** (P1) Keep PLAN mermaid diagrams (state machine §4.1, sequence §4.2) in sync with code as it lands
- [ ] **T630** (P2) Create `data/` directory when first input data exists
- [ ] **T631** (P2) Split ADRs from PLAN §8 into `docs/ADR/` files (completes T009)
- [ ] **T632** (P2) Defensive: enforce the 15-word hint cap on inbound hints too

---

# ADDENDUM B — v2.11 compliance-audit tasks (gaps found vs. all 3 Material sources)

### B.1 Four repo links in the game-end JSON (rule 49, Ch.9)
- [ ] **T633** (P1) Result artifact writer stores **all four repo links** (our 2 + opponent's 2, captured during the handshake identity exchange T320); unit test asserts 4 links present

### B.2 UI/UX documentation (guidelines §10)
- [ ] **T634** (P2) Interface documentation: describe typical user workflows, note accessibility considerations, and run a Nielsen-heuristics self-check on the Live GUI + Replay Viewer (screenshots per state already in T473)

### B.3 Scent-model crypto-lock (rule 23)
- [ ] **T635** (P2) Handshake test: `pheromones` section (formula parameters) is part of the signed terms hash — a peer with a different scent model is refused at negotiation

---

## Milestones
**M1** legal move + capture (local) · **M2** message A→B (localhost) · **M3** shortest path to target · **M4** belief + truth/lie hints · **M5** remote game via tunnel · **M6** commit-reveal + audit + Step-0 · **M7** Gmail JSON + GUI + Replay (Verified OK).

## Task count
635 tasks (T001–T620 + addenda T621–T635). Tasks apply to both repos unless marked *(role-specific)*.



