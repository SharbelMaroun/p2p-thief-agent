# Quality evidence — the four metrics, ISO/IEC 25010, seams, concurrency

Covers `M9-008`, `M9-008a`, `M9-008b`, `M9-008c`, `M9-014`, `M9-014a`…`M9-014d`.

Two frameworks apply and they come from **different sources**, which is worth stating plainly
because one of them is not in the book at all.

* **The four success metrics** are the book's, from Table 4 (p.94/211). They are what the
  project is judged on.
* **ISO/IEC 25010's eight characteristics** come from the *submission guidelines* §13.1
  (`inst/software_submission_guidelines-V3_Summary.md:816`). The term does not appear in the
  book — asking the book notebook returned `NOT-SPECIFIED-IN-BOOK`, with chapter 11.3
  (p.93/209) offering the nearest equivalent: "professional code is written so it can be read,
  tested and reproduced by others".

Both are answered below. Where the evidence is thin it says so. A self-assessment that scores
itself full marks everywhere is not evidence, it is a claim.

## The book's four success metrics (Table 4, p.94/211)

### Coordination — `M9-014a`

*The book's wording:* a P2P protocol over FastMCP, turn management and synchronisation
between two autonomous agents with no central server and no external referee (chapter 2).

| Evidence | Where |
| --- | --- |
| Two peers, no referee | `adapters/fastmcp_server.py`, `adapters/fastmcp_client.py` |
| Turn ordering and phase machine | `orchestration/phases.py`, `orchestration/sub_game.py` |
| Two real OS processes over localhost | `tests/integration/test_localhost_two_processes.py` |
| Deadlines and watchdog | `services/deadlines.py`, `services/watchdog.py` |
| Bounded inbox — refusal, not growth | `adapters/fastmcp_server.py`, `QUEUE_DEPTH_MINIMUM = 100` |

### Adaptation — `M9-014b`

*The book's wording:* two symmetric agents coping with uncertainty — a belief map over the
opponent's position, processing the opponent's verbal hints, and a scent-trail network
(chapters 4 and 6).

| Evidence | Where |
| --- | --- |
| Belief distribution, Bayes from observation only | `state/belief.py`, `strategy/belief_policy.py` |
| Scent emission and multiplicative decay, hash-locked | rule 23 lock; `test_scent_regression.py` |
| Verbal hints generated and judged | `verbal/hints.py`, `verbal/generation.py` |
| Belief never crosses the wire | `test_belief_and_scent_privacy.py` |

**The honest gap.** `M6-015c` records that our own evasion metric counts total survival steps,
while Appendix F pays for reaching the threshold or being captured, with nothing in between.
Over 24 perimeter openings the ranking **reverses** — blind 175, belief 140. The row is open
rather than patched, and the report discloses it instead of quoting the flattering number.

### Integrity — `M9-014c`

*The book's wording:* preventing forgery and cheating through SHA-256 commit-reveal, and a
full log-audit phase at the end of the game (chapter 5).

| Evidence | Where |
| --- | --- |
| Commit-reveal over canonical bytes | `protocol/crypto.py` |
| Audit before agreement is structural, not remembered | `orchestration/settlement.agree(audit, …)` |
| No report can be composed without a passed audit | `reporting/email_report._require_agreed` |
| Nonces refused before the game ends | `reporting/log_artifact.build_log` requires `ended_at` |
| A stored match re-verifies off disk | `tests/integration/test_replay_of_stored_match.py` |
| No secret anywhere in history | `scripts/scan_git_history.py` — 1744 objects, 0 findings |

### Architecture — `M9-014d`

*The book's wording:* the Orchestrator and Gatekeeper patterns, and failure-resistant code
(chapters 8 and 10).

| Evidence | Where |
| --- | --- |
| One gatekeeper for every external call | `services/gatekeeper.guard` |
| The orchestrator owns the series, not the transport | `orchestration/series.py` |
| Reporting imports no transport — proved from the AST | `test_transport_independence.py` |
| A disconnected game still emits four artifacts | `test_disconnected_emission.py` |

## ISO/IEC 25010, guidelines §13.1 — `M9-008a`

| Characteristic | Evidence | Where it is weak |
| --- | --- | --- |
| **Functional suitability** | Every Appendix E rule carrying a sanction has a named test; `docs/REQUIREMENTS_LEDGER.md` maps rule → code → test | Rules whose behaviour is unresolved (`U-019`) are implemented provisionally and labelled so |
| **Performance efficiency** | `docs/RESEARCH-REPORT-Performance-Analysis.md`; `scripts/benchmark_decision.py`; the token ledger enforces the agreed per-game limit | No profiling against an adversarial peer; the endurance test is local |
| **Compatibility** | Frozen wire profile in `tests/conformance/`; unknown wire fields ignored, missing required fields refused | Interop proven against our own peer and a synthetic foreign log — **never against a classmate** (`M8-003c`, open) |
| **Usability** | `docs/RUNBOOK_reporting_setup.md`, `docs/USAGE.md`, the live GUI, the replay viewer | No user testing. The audience is one grader and two students |
| **Reliability** | Atomic artifact writes (`reporting/emit.py`), watchdog, deadline tracker, 429 backoff, refuse-don't-block queues | Recovery from a mid-series crash is untested; the ledger would need rebuilding by hand |
| **Security** | `gmail.send`-only scope; private-field guard matching on key names; secret scanner over the tree **and** history; nonce secrecy enforced at build time | No threat-model document. The scanner's one reviewed history finding is a false positive pinned by blob SHA |
| **Maintainability** | 150-line file cap, ≥85% branch coverage (actual 99%), a PRD per mechanism, docstrings that carry the *why* | Some modules are split to satisfy the line cap rather than for cohesion. That is a cost of the rule, recorded not hidden |
| **Portability** | `uv.lock` frozen install, verified from a clean clone by `scripts/verify_clean_clone.py` | **Windows only.** Never run on Linux or macOS; `M9-013a` (second machine) is open |

## Extension seams — `M9-008b`

* **Strategy.** `strategy/baseline.py` and `strategy/belief_policy.py` share one call shape,
  and `run_thief_series` takes the policy as an argument. Adding a strategy is adding a
  module, not editing the orchestrator.
* **Verbal provider.** `verbal/providers.py` defines the interface and the shipped default is
  a zero-token template provider, so a live model is a substitution rather than a rewrite.
  It is also why the suite needs no API key and stays deterministic.
* **Transport.** `adapters/` is injected wherever it is used — `send_report(transport=…)`,
  `api_send(service, …)`. The tests pass recording doubles through exactly the seam a
  different provider would use.

## Concurrency — `M9-008c`

Every thread or process, and why each is safe:

| Where | What runs | Why it is safe |
| --- | --- | --- |
| `adapters/fastmcp_server.py` | The server's event loop | Inbox writes go through `_enqueue`/`put_nowait`; a full queue **refuses** rather than blocking or growing (rules 6 and 29) |
| `services/watchdog.py` | Deadline supervision | Time is injected — no background thread. The caller drives the clock, so a test advances a number instead of waiting |
| `tests/integration/localhost_peer.py` | A second interpreter | A real subprocess with no shared memory, which is also what rule 2 demands |

**No shared mutable state crosses a thread boundary anywhere in `src/`.** The belief map, the
scent grid and the token ledger are each owned by one agent and never handed to another.

That is not a happy accident. Rule 2 (Prohibited) says "do not share memory or variables
between parties at all", with immediate disqualification for data leakage as the sanction — so
the safest concurrency story available here is the one where there is nothing to share, and
the design was chosen to make that true rather than to make it provable afterwards.
