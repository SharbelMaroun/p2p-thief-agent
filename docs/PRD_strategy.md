# PRD — Strategy & Decision Module

- **Version:** 1.00 · **Status:** DRAFT
- **Modules:** `strategy/brains.py`, `strategy/__init__.py` (factory) · **Phase 3–4** · **Tasks:** T176-228 · **Requirements:** FR-11, FR-12

## 1. Purpose
Decide each turn's **move** — the graded creative core of the project. The move is chosen by **pure Python**; the LLM is never consulted for it (it hallucinates coordinates). This is where league wins come from.

## 2. Theoretical background
- **Pursuit-evasion on a graph:** cop minimizes, thief maximizes distance to the target cell.
- **Manhattan distance** is the admissible heuristic on an orthogonal grid (no diagonals).
- **Belief-driven targeting:** the target is `argmax b(s)` from the belief map, not the true (hidden) opponent.
- **Three valid paths** (rulebook Ch.6): pure heuristics (Bayes + Manhattan, the default), combined heuristics (belief + scent + look-ahead), and optional RL (Q-learning) — all keep the move algorithmic.

## 3. Functional requirements
- **ST-1** `_pick_move(moves, state, belief)` returns a legal `(direction, cell)`.
- **ST-2** Thief: maximize distance to belief peak; prefer unvisited cells; avoid dead-ends.
- **ST-3** Police: minimize distance to belief peak; issue `capture_claim` when on the target cell.
- **ST-4** `_decide_move` chooses **MOVE vs BARRIER vs HOLD** (police barriers only).
- **ST-5** Police barrier placement: legal (1 step away), quota-aware (≤14), never self-trapping; used to cut off escape.
- **ST-6** Move is deterministic given `(state, belief, seed)` — reproducible.
- **ST-7** LLM (optional) writes only the hint; move unaffected by LLM availability/latency.
- **ST-8** Strategy is **config-injectable** via `[strategy] police_class/thief_class`; unset → default heuristic.

## 4. Interface (I/O)
```python
class BrainBase:
    def decide(state, belief, opponent_hint, setting, barriers_max, deadline) -> Decision
    def _decide_move(state, belief, barriers_max) -> (MoveType, Direction|None)
    def _pick_move(moves, state, belief) -> (Direction, Cell)   # student override
resolve_brain(config, role, llm, rng) -> BrainBase              # reads [strategy]
Decision = {move_type, direction, hint, verdict, reasoning, response_seconds}
```

## 5. Performance metrics
- Move computation: instant (< 1 ms), 0 tokens. · Win-rate vs. random baseline and vs. greedy baseline measured and reported. · Capture rate (police) / survival rate (thief) improve with belief integration.

## 6. Constraints & limitations
- Never let the LLM choose the move (exception only by mutual prior agreement — ADR-2). · Must always return a **legal** move (legality enforced against `board.legal_moves`). · Barrier misuse can self-trap the police — planning required. · Hints are **natural language only** — never encode coordinates or numeric location codes (Appendix E rules 26–27; disqualification); outbound hints pass a validation check before send.

## 7. Alternatives considered
| Option | Verdict |
|---|---|
| Pure greedy min/max distance | Baseline only — beatable. |
| **Belief-weighted heuristic + barrier planning + look-ahead** | **Selected** — strong, transparent, no training. |
| Q-learning / MARL | Optional; allowed but not required (course doesn't teach RL); large state space, moving target. |
| LLM-driven move | Rejected by default — hallucinations → illegal/suicidal moves. |

## 8. Success criteria
- M3: agent computes shortest path to a known target with no manual help.
- M4: belief-driven agent beats the random baseline on capture/survival rate.
- Swapping the brain class via config changes behavior with **zero engine edits**.

## 9. Test scenarios (→ T191, T200, T210-212, T219, T225)
- Thief picks the max-distance legal move. · Police picks the min-distance move + valid barrier. · Illegal move never returned (surrounded → HOLD). · Bad `[strategy]` selector fails fast. · Same seed → identical game. · Benchmark harness reports win-rate vs baselines.
