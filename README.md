# P2P Thief Agent

Independently installable Thief-side package for the “Distributed Cops-and-Robbers over
a Peer-to-Peer Network” university project.

Companion Cop repository:
<https://github.com/SharbelMaroun/p2p-cop-agent>

## Milestone status

M0, M2, and M3 are `DONE`, and the simulator-conformant protocol layer (commit-reveal,
canonical hashing, wire messages, signed-terms handshake) is implemented. M1 is
`IN PROGRESS`: the wire profile is authored and adopted, but no acceptance verdict is
recorded and the contract checker stays fail-closed. M4–M9 are `PENDING` and proceed
sequentially; unresolved choices are raised explicitly rather than classified as
blockers.

Version `1.00` began as an M0–M1 documentation and package scaffold. The inspected
baseline (`119fa911d5b1a5aecdaa9531d0912e5c6f9ab32f`) contained no Python package,
tests, `pyproject.toml`, or lockfile; that milestone added those engineering
foundations.

The M2 core domain — coordinates, board geometry, legal movement, barrier rules, and
capture conditions — is now implemented behind the public SDK under the 2026-07-28
coordinator authorization for contract-independent domain work. It uses only Appendix
E/F `CONFIRMED` rules, takes every board and position input explicitly, and depends on
no shared-contract byte, MCP endpoint, or Cop-owned file. See
[M2_DOMAIN.md](docs/M2_DOMAIN.md).

Commit-reveal, canonical hashing, the wire message types, and the signed-terms
handshake are implemented as pure protocol logic under `src/p2p_thief_agent/protocol/`
and documented in [SIM_WIRE_PROTOCOL.md](docs/SIM_WIRE_PROTOCOL.md).

Since then the FastMCP transport has been built on both sides — a server mailbox and
an outbound client, confined to `adapters/` by a guard test — together with the
private opponent-URL boundary and the pre-play agreement gate, which refuses a
mismatched match **by name** before a first move exists. A message has crossed a real
socket between two operating-system processes, closing the book's stage-2 milestone.

The turn loop now exists too: a bounded sub-game runs end to end through a declared
phase machine and reveals its audit, with both crossing a real socket into a separate
operating-system process.

The repository still deliberately implements no public tunnel, scent field, belief
map, LLM, Gmail, GUI, or replay behavior — and, decisively, **no second peer that
plays back**. The opponent's moves in every run so far come from a local script, so
**no game has been played against a real opponent**.

Earlier Cop-bundle reviews are retained as historical audit evidence only. No
peer-owned file was integrated, and those bundles are not inputs to the current
Thief-authored conformance workflow. The dated findings remain in
[COORDINATOR_VERDICT_2026-07-28.md](docs/COORDINATOR_VERDICT_2026-07-28.md) and
[CONTRACT_REVIEW.md](docs/CONTRACT_REVIEW.md).

On 2026-07-28 the copy model was **superseded**. Under `THIEF-002` this repository has
no access to the companion Cop repository and must play unknown classmate opponents, so
byte-parity with one peer would prove nothing about interoperability. M1 is therefore a
conformance gate rather than a copy gate: the Thief authors its own wire profile.

On 2026-07-29 that profile was re-based onto the reference simulator's wire
(`SIM_WIRE_PROTOCOL.md`), replacing the earlier Option-B profile. The Node neutral-stub
harness and the conformance tests written against the **old** profile were retired with
it and now sit unused in `archive/pre-sim-realign/`; the current profile has **not** yet
been proved bidirectionally against any independent stub. Re-establishing that evidence
is open M1 work, and the contract checker stays fail-closed until it exists. See
[CONTRACT_HANDOFF_CHECKLIST.md](docs/CONTRACT_HANDOFF_CHECKLIST.md).

## Install and inspect

Python 3.11 or newer and
[uv](https://docs.astral.sh/uv/) are required.

```text
uv sync --frozen
uv run p2p-thief --help
```

The command exposes scaffold metadata and help only. It does not start a peer or a
game.

## Quality gates

```text
uv run ruff check .
uv run pytest --cov --cov-branch --cov-fail-under=85
uv run python scripts/check_file_lengths.py
uv run python scripts/check_secrets.py
uv run python scripts/check_shared_contracts.py
```

The conformance checker remains fail-closed at `PENDING` until an exact accepted
profile revision is recorded. This is honest incomplete evidence, not a blocker on
profile or conformance work.

## Confirmed boundaries

- Cop and Thief are separate processes and repositories with no shared memory, database,
  runtime filesystem, or private truth (`SR-001`, `SR-004`, `THIEF-001`).
- This repository is developed with no read and no write access to the companion Cop
  repository, and must interoperate with an **unknown** opponent (`THIEF-002`). League
  play is against classmates, so matching one companion repository is evidence about
  that repository only. Interoperability is demonstrated against a neutral stub sharing
  no files with either side.
- Legal moves are north, south, east, west, and stay; diagonals are illegal
  (`AF-015`).
- Barrier placement is disclosed; a barrier on the Thief’s current cell and a trapped
  Thief are captures (`AE-015`, `AE-046`).
- SHA-256 commit-reveal, secret nonces until reveal, explicit state machines,
  illegal-transition rejection, deadlines, watchdogs, and public tunneling are required
  (`AE-004`, `AE-006`, `AE-010`, `AE-017`).
- Live GUI information is local truth only (`AE-008`).
- Appendix F values are recorded as `AF-013`–`AF-022`; artifact-example key-set
  observations are recorded as `JS-001`–`JS-003`, with provenance still unresolved.
- Deterministic movement is the project default. Appendix E rule 25 is a
  recommendation, not an automatic mandatory sanction (`AE-025`).

See the [requirements ledger](docs/REQUIREMENTS_LEDGER.md), [verified parameter
baseline](docs/PARAMETERS_BASELINE.md), [JSON artifact evidence](docs/JSON_ARTIFACT_SCHEMAS.md),
[book/template reconciliation](docs/BOOK_TEMPLATE_RECONCILIATION.md),
[proposed gate-resolution review](docs/GATE_RESOLUTION_REVIEW.md),
[unknowns](docs/UNKNOWN_REQUIREMENTS.md), [conflicts](docs/SPECIFICATION_CONFLICTS.md),
[repository audit](docs/REPOSITORY_AUDIT.md), [independent contract
review](docs/CONTRACT_REVIEW.md), [contract handoff
checklist](docs/CONTRACT_HANDOFF_CHECKLIST.md), and
[M1 verification record](docs/M1_VERIFICATION.md).

## Architecture boundary

All future business behavior must be reachable through the public SDK. CLI, GUI, MCP
transport, and external integrations may adapt inputs and outputs but may not contain or
duplicate business logic. The present package exposes the implemented M2 domain and
deterministic baseline through the SDK; protocol, orchestration, service, and UI
packages remain explicit boundaries for their later milestones.

Historical configurations remain quarantined under `config/drafts/`; runtime code must
not load them. Local private TOML and real `.env` files are ignored.

## Configuration

Configuration is split in two, and the split is load-bearing (`ADR-0004`).

- **Shared, signed, byte-identical.** The per-match game object holds everything
  that shapes the game — board, movement, scoring, scent, league counts. Both peers
  must hold the same bytes; it is hashed and signed during the pre-play agreement,
  and any differing term refuses the match **by name**.
- **Private, local, never sent.** `config/game.toml` holds this peer's own port,
  the opponent's URL, model choice, credentials, and per-turn commitment nonces.
  `config/game.toml.example` is the committed skeleton, matching the book's page 131
  and the reference's own `config/thief/game.toml`; the real file is git-ignored.

The opponent's address is read only from `[network].opponent_url`, by
`shared.private_config.load_opponent_url`. The shared object must carry no URL,
port, or host at all — `assert_no_network_address` refuses one that does, whether
the address is named like an address or merely looks like one.

## Usage

This peer is not yet runnable as a live agent. The SDK, protocol layer, both
transport adapters, the agreement gate, and the turn loop all exist; what is missing
is the wiring that points them at a real opponent and a second peer to answer. Today's
honest usage surface:

```text
uv run p2p-thief --version        # 1.00
uv run python -m p2p_thief_agent --version
```

A message crossing a real socket between two operating-system processes — the
book's stage-2 milestone — is exercised by:

```text
uv run pytest tests/integration/test_localhost_two_processes.py -v
uv run pytest tests/integration/test_negotiation_gate.py -v
```

This section will gain the live `peer` invocation, its flags, and replay
screenshots once the turn loop and a full sub-game land.

## Contributing

The gates enforce the standards, so a change that passes CI already meets them:

- **Style.** `ruff check .` with no findings; do not add per-file ignores to
  silence one.
- **File length.** No file over **150 lines** (`scripts/check_file_lengths.py`).
  Split by responsibility rather than deleting explanatory comments.
- **Tests.** `pytest --cov --cov-branch --cov-fail-under=85`. New behaviour needs a
  test that would fail without it. Prefer pinning a rule to the document that states
  it, so an edited constant fails here rather than in a match.
- **Secrets.** `scripts/check_secrets.py` must report zero findings. Ports, the
  opponent URL, credentials, and commitment nonces stay in the git-ignored
  `config/game.toml` or `.env`.
- **`THIEF-002`.** No task may be satisfied by reading, cloning, or inspecting the
  companion Cop repository. The pinned simulator is the sanctioned wire reference:
  match its wire, never copy its source.
- **The contract checker** (`scripts/check_shared_contracts.py`) is **fail-closed**
  and exits non-zero while no accepted parity manifest exists. Never edit it to
  pass.
- **Commits.** Stage explicit paths, never `git add .`. Say what changed and *why*,
  citing the authority (book section, Appendix E/F rule, ADR) when the change
  encodes a rule.
- **Documentation.** A behaviour change updates `docs/TODO.md` and every document
  asserting the old behaviour; `docs/PROMPT_LOG.md` records significant AI-assisted
  steps with the problem found and the lesson drawn.

## Report

The graded report has six sections. Sections needing a completed match are marked
blocked rather than filled with claims we cannot show.

### 1. The Dec-POMDP model

The game is a **decentralised, partially observable Markov decision process**.

- **Decentralised.** No server, no referee, no shared memory. Each peer runs in its
  own operating-system process under its own configuration directory and the two
  communicate only by message. Neither can inspect the other, so fairness rests on
  cryptography rather than trust — and under `THIEF-002` this repository is developed
  without access to the companion peer at all, so the opponent is genuinely unknown.
- **Partially observable.** The Thief never learns the Cop's position. Each turn it
  observes its own position, the barriers it has discovered, the Cop's hint, and a
  commitment hash. Barrier placement is disclosed, so the map of known obstacles grows
  as the game proceeds — that is the Thief's main source of hard information, and it
  arrives as a constraint rather than a location.
- **Markov decision process.** State is the two positions, the barrier field, and the
  step index; actions are `N`, `S`, `E`, `W`, `STAY`; transitions are deterministic
  given both actions. Rewards come from the fixed Appendix F table: capture pays the
  Thief 5, survival 10, a tie 2, and a technical loss **zero to both sides**.

The asymmetry favours the evader in one respect and not another: the Thief **moves
first** every turn and only has to survive the step limit, but it cannot place
barriers, so it can never shape the board — it can only read it.

The Thief's local state is deliberately incapable of holding the Cop's position:
`ThiefLocalState` carries only the board, its own position, its known barriers, and
the step. The Zero-Trust property is enforced **by construction**, not by discipline.

### 2. The FastMCP communication dilemma

Two agents must talk to play, yet every message is a chance for the opponent to cheat
or to learn.

**Simultaneity without a referee.** Whoever announced a move first would be at the
other's mercy, and there is no third party to hold both. **Commit-reveal** resolves
it: each peer hashes its private decision with a fresh nonce and sends only the
digest, so no decision can change after seeing the other's. Nonces stay secret until
the post-game audit, where every commitment is recomputed; one mismatch is an
automatic zero with no appeal, which makes an audit failure worse than a lost game.

**Deception is legal; forgery is not.** The Thief may lie in its hint — that is the
strategic layer the project is about — but the lie is sealed. It declares `intent` as
truth or bluff inside the commitment, so at audit the opponent learns exactly which
hints were honest. A player may deceive within the turn and cannot deceive about
having deceived.

**What crosses the wire.** The book describes a per-turn phase where peers exchange
their actual moves. The pinned reference sends **none**: the live message carries the
hint, the scent grid, and the commitment hash only, while the move, true position,
bluff verdict, and nonce stay private until the audit (`C-022`). This repository
follows the wire, because interoperability is decided by what crosses the socket.
That decision cost real work — an earlier iteration implemented the book's live
reveal step and had to remove it (`P-020`), which is the most instructive mistake in
this project's history.

**Trusting an unknown opponent.** League play is against classmates, so a peer's
replies cannot be assumed to match ours. Outbound we accept any reply that does not
explicitly refuse; inbound our tools always acknowledge and validate afterwards, so a
content rejection is recorded as a game outcome rather than raised at the sender as a
network fault. Strict in what we send, generous in what we accept.

**Refusing to play is a feature.** Before a first move exists, the pre-play agreement
compares every negotiated term against our own and refuses a mismatch **by name**,
enforcing the Appendix F floors — `Fixed` values exactly, `Minimum` values only in
the harder direction. A refusal an opponent cannot act on would be worth little.

**Bounded waiting (added 2026-08-01).** Every wait is now finite. The book is blunt
about why — *"Missing a Deadline is a Failure, Not Patience"* — and permits only two
outcomes when an expiry passes: retry, or declare a technical loss and clear the
queue. An un-expiring pending request is named as the direct path to freezing. So
each attempt carries its own expiry, retries stop at the agreed limit, and an attempt
that overruns its own deadline is **not** retried: the retry budget does not rescue a
missed deadline.

The four limits live in the **shared, signed** match object rather than private
configuration, which is the part worth noticing — a peer able to set its own timeout
could stall an opponent legitimately. Reading them from the agreed bytes makes that
impossible rather than merely impolite.

*Problems hit building it.* Three. The reference notebook froze twice and the query
had to be re-sent three times before it submitted — logged rather than skipped,
because a tool failure is not permission to skip a verification step. Re-reading the
ledgers first turned up two rows still marked open for work already finished, which
would have sent someone to redo it. And the book PDF contradicted our own parameter
baseline in a small way: Appendix F table 19 marks the watchdog timeout
**`Negotiation`**, not `Minimum` like the retry limits beside it — a distinction that
matters, since a `Minimum` may only be tightened while a negotiated value can move
either way. Both baselines were corrected.

**The Gatekeeper (added 2026-08-01).** Outbound calls now pass through a rate
limiter that queues overflow instead of refusing it. The guidelines are explicit -
*"Overflow is queued, not rejected"* - which inverts the usual instinct: a busy gate
tells the caller to wait and **keeps** the work, and only a genuinely full queue
fails, loudly, because silently discarding a call is worse than admitting defeat.
The limits (30 requests/minute, 2 concurrent, queue depth 100) come from the signed
match object, so neither peer can quietly give itself more room.

*Problems hit building it.* Two, both about scope rather than code. Idempotency was
already done - the receive-side intake had been deduplicating and rejecting replays
since an earlier milestone - so checking first turned a planned feature into a
verification. And the book narrowed it again: the Gatekeeper guards **outbound**
Gmail and LLM calls against rate-limit bans, not the inbound peer mailbox. Building
it as an inbound queue would have been a plausible and completely useless answer.

Worth recording: our own task title said *"FIFO queue depth"*, and the book turned
out never to say FIFO - it was our inference wearing a citation. The word was
removed. A task that credits the book for something the book never said is how an
invented requirement becomes permanent.

**The Watchdog (added 2026-08-01).** Where a deadline bounds a single request, the
watchdog watches the whole game loop. If no heartbeat arrives for longer than the
agreed `watchdog_timeout_sec`, it performs a **controlled shutdown**: `persist_state()`
to save the game for later recovery, then `controlled_shutdown()` to release the MCP
connections and close the logs — in that order, once, and with teardown guaranteed to
run even if saving state fails. Time is injected, so a freeze is exercised by passing
a number rather than sleeping through minutes. This closes the `M5-004` reliability set
(deadlines, watchdog, mid-turn-disconnect terminal loss, backpressure). A dropped send
mid-turn has no deadlock exit: the turn loop routes it, and every sub-game to a
terminal technical loss whose audit is still revealed, is proven by test.

*Problems hit building it.* Two worth recording. First, no NotebookLM tool was
available in this environment, so — with the coordinator's authorization — the work
was verified against the higher authority the notebooks only summarize: the book PDF,
Appendix E/F, and the authorized reference simulator on disk. Second, that simulator
implements **no watchdog at all** — a book-mandated pattern it skipped — which removed
any wire or interop question and left the book as the sole authority; the boundary
(`elapsed > timeout`) was therefore taken from its page-83 code verbatim, deliberately
unlike the deadline's `>=`.

#### The play loop: driving the mailbox (`M5-019`, 2026-08-02)

The FastMCP server this peer runs is a **passive mailbox** — its four tools enqueue the
opponent's message, acknowledge it, and do nothing else. The turn loop is the mirror
image: it consumes a message and never looks for one. Nothing joined the two, which
meant every sub-game test had to hand the loop a *scripted* opponent, and a peer could
not play a match unattended.

The join is a polling turn source. Each wait drains the mailbox, hands back the next
turn the peer **accepted**, and is bounded — Appendix E rule 6 makes a deadline
mandatory "to prevent deadlocks while waiting for the opponent", so silence returns
`None` and the loop takes its declared exit to `TECHNICAL_LOSS` instead of blocking.
The wait also **pulses the heartbeat every iteration**, because book section 8.4.2 puts
the watchdog on the main game loop and waiting for an opponent is precisely the window
in which a frozen peer and a patient one are indistinguishable.

Three behaviours in the mailbox side are there because each would otherwise break an
unattended match invisibly: a *rejected* turn is consumed (leaving it queued makes the
poller re-reject it forever and starve the real turn behind it), a *second* queued turn
is left in place (draining both discards the next step rather than playing it), and the
other three mailboxes are drained first (a control or audit message parked in front of
a turn stalls the game). A whole sub-game now plays with **no message fed in by hand**.

**The Thief's asymmetry matters here.** This peer *opens* every cycle — the book gives
it the first move — so step 1 sends without waiting and the poller becomes load-bearing
from step 2 onward. The mirror-image mistake is not hypothetical: a Thief that waits
for step 1 deadlocks against a Cop that is correctly waiting for it, and the companion
repository's test harness contained exactly that error until a failing test exposed it.

*Problems hit building it.* The two notebooks appeared to **contradict each other**:
the reference drives its runtime by polling its own inboxes at `poll_interval_seconds`,
while the book mandates a strict state machine rather than a loop. Treating that as a
conflict would have meant choosing one and quietly dropping the other; the actual
resolution is that they answer different questions — polling is only *how* a queued
message is picked up, and the phase machine still decides what may legally follow.

*What is still not built.* The `serve` CLI (`M5-019e`). `build_server(...).run()` is a
blocking call, so launching a peer needs the server on a background thread plus
autonomous negotiation sequencing. A **passive** `serve` — one that mailboxes without
playing — was rejected in the companion repository as proving connectivity rather than
a game; that decision is honoured here rather than quietly reversed.

*A blocker that got worse on inspection.* The book's stage-5 milestone requires
**screenshots from the Replay App showing "Verified OK", plus the Live GUI belief map**
as its evidence. Both are `M8` deliverables, so the two-machine game cannot be
*evidenced* even once the hardware and the CLI exist.

*A ledger gap this exposed.* `docs/TODO.md` had **no row at all** for the play loop —
the companion repo named it only inside a blocked row's prose, and here it was named
nowhere. The single most load-bearing missing piece in the repository was invisible to
any search for open tasks. It is now `M5-019`, with sub-rows.

#### Ledger reconciliation (2026-08-02)

That gap prompted an audit of every open `M5` row against the code actually present.
Six rows were wrong:

- **`M5-016` (backpressure) was already done and never recorded.** `services/gatekeeper.py`
  and nine tests implement it, one of which — `test_a_full_queue_refuses_loudly_rather_than_discarding`
  — states the row's Definition of Done almost verbatim. Closing it required no code.
- **`M5-012a`…`f` were stale.** The parent `M5-012` closed on 2026-08-01; its six
  sub-rows were left reading `PENDING` underneath a `DONE` parent. Four are superseded
  by `M5-014` and `M5-007`; two are genuinely done.

Three rows were checked and **confirmed genuinely open** — `M5-011` (adversarial-peer
proof), `M5-013a/b` (subsystem diagram and failure-path table), `M5-018` (SDK/transport
guard). The evidence of each check is written into the row so the next session does not
repeat it. That negative result matters: in conversation I had guessed `M5-011` and
`M5-018` were probably already satisfied, and both turned out to be real work. A
reconciliation that records only the good news drifts the ledger the other way.

### 3. The implemented strategy

Movement is **pure Python and deterministic**; the language model never selects a
move. The shipped baseline ranks candidate moves by strict criterion priority rather
than a weighted sum — discard dead ends, maximise distance from the believed threat,
maximise mobility, maximise two-ply reach, then minimise corner contact, with a fixed
action order breaking ties.

Lexicographic ranking was chosen over weights deliberately: no calibration data
exists that would justify any particular coefficients, and a strict order can be
audited from the log, while tuned weights cannot. The first definition of "trapping"
proved nearly vacuous — the cell just vacated is always a legal way back — and was
replaced by "every exit leads back to the origin".

This is the floor the graded strategy must beat, not the deliverable.

### 4. Learning curves

**Not applicable.** No reinforcement learning is used; the policy is deterministic by
design, so there is no training run and no curve. If RL is adopted, this section
gains the curves rather than a placeholder chart.

### 5. Live belief map and "Verified OK" replay screenshots

**Still blocked, but for a narrower reason than before.** A bounded sub-game now runs
end to end and its audit is delivered: every turn and the final reveal cross a real
socket into a separate operating-system process, which validates each one — and a
*tampered* audit is rejected there, so rule 19 is enforced over a real carrier rather
than asserted locally.

What is missing for a screenshot is a **second peer that plays back**. The Cop's
replies in those runs come from a local script, so there is no live belief map to
photograph yet, and there is no GUI.

### 6. Companion repository

<https://github.com/SharbelMaroun/p2p-cop-agent> — the Cop-side peer. Under
`THIEF-002` it is not an input to this repository's development.

## License and provenance

The [MIT license](LICENSE) covers team-authored material where legally valid.
Lecturer-provided documents and simulator code are not automatically relicensed. No
lecturer simulator runtime code is included in this scaffold.
