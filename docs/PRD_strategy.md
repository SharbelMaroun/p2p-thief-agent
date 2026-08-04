# PRD — Thief Strategy

Status: deterministic baseline policy **implemented** as a contract-independent module
on branch `agent/thief-baseline-strategy`. Belief, scent, look-ahead beyond two ply,
and any verbal layer remain `PENDING` in their later milestones.

Evasion, legal route selection, survival, Thief-local belief use, and Thief-local verbal
behavior are in scope. Appendix E rule 25 recommends algorithmic movement and LLM use
for text/behavioral-profile generation. It is a recommendation without an automatic
mandatory sanction, not a categorical prohibition (`AE-025`).

ADR-0007 therefore **proposes** a deterministic movement baseline. Its status is
`Proposed`, not accepted, so it is a recorded proposal rather than settled project
policy; the implemented baseline below follows it as the working default without
treating it as an accepted decision. Any future change requires both peers' accepted
policy and still cannot bypass legal-action validation, deadlines, or the SDK. No
model/provider is mandatory.

## Future inputs and output

The accepted SDK strategy input will contain only Thief-local state, public
observations, known disclosed barriers, legal actions, history, and configured
deadlines. Output will be one structured candidate action; orchestration validates it
before any protocol use.

## Future acceptance criteria and tests

- The baseline always chooses one of N/S/E/W/STAY from the supplied legal set.
- Same snapshot and configuration produce the same choice.
- Empty/trapped and boundary cases produce the accepted capture/outcome path.
- Known barriers and survival objective affect selection without Cop-private truth.
- No strategy function performs networking, GUI work, or an external/LLM call.
- Normal, tie-break, fallback, trapped, and invalid-input paths are covered.

Weights, look-ahead, belief heuristic, verbal policy, and optional future learning are
team design choices. No strategy implementation is included in M1.

## Implemented baseline

`p2p_thief_agent.strategy` exposes `choose_action` and `rank_actions` through the SDK.
Both are pure: they take board, position, plausible Police cells, and disclosed
barriers explicitly, and they read no Cop-private truth.

Because scent physics and belief are `PENDING` in M6, the policy cannot infer a Police
position. It accepts an explicit iterable of **plausible** Police cells and reasons
about the worst case among them. An empty iterable is a vacuous criterion, not an
assertion that every cell is safe.

Candidates are ranked by strict criterion priority, never by a weighted sum, so no
numeric weight needs calibration data the project does not have:

1. discard dead-end targets — a target whose every remaining exit leads back to the
   cell just vacated;
2. maximize the Manhattan distance to the nearest plausible Police cell;
3. maximize one-step mobility at the target, excluding `STAY`;
4. maximize two-ply onward reach, then minimize corner/edge contact;
5. break remaining ties by the fixed `Action` order `N, S, E, W, STAY`.

Consequences of this ordering that are deliberate, not accidental: fleeing outranks
corner avoidance, so the policy will move towards an edge to increase distance; and
because `STAY` is always legal from an on-board cell, a legal action always exists, so
`choose_action` never raises for an on-board position. An off-board position is
rejected by the domain rather than silently repaired.

`rank_actions` ranks dead ends last as a block rather than dropping them, so a caller
facing nothing but dead ends still receives a complete legal ordering. That block
ordering is the deterministic fallback.

### Boundary

The baseline is a contract-independent exception authorized on 2026-07-28. It is not
M3-004: formal M3 integration remains `PENDING`, and this module adds no local state, no history,
no scoring, and no turn state machine. Manhattan distance and the criterion order are
implementation choices, not official rules, and no shared-contract byte depends on
them.

## Belief-driven evasion (`M6-004`, built 2026-08-03)

The baseline ranks legal actions against *given* threats; `M6-004` supplies the threat
from the belief instead of from an observed Police cell. `strategy/belief_policy.py`:

- `believed_cop_cell(belief, board)` reads the single most-likely Cop cell off the
  perception-layer distribution, breaking ties at the lowest `(row, col)` so the choice is
  deterministic (`M6-004g`).
- `choose_evasive_action(board, position, belief, barriers)` hands that cell to
  `choose_action` as the threat, so evasion, dead-end avoidance, legality, and the fixed
  tie-break are all inherited unchanged. A belief that misdirects the Thief — even one
  peaked on a wall or on its own cell — can therefore never produce an illegal move
  (`M6-004e`), and nothing on the path is an LLM or a network call (`M6-004b`, guarded by
  `test_movement_llm_free.py`, `AE-25`). The policy is weight-free, so no tuning value can
  leak into the shared JSON (`M6-004h`).

The move is always pure Python. The verbal layer (`verbal/hints.py`,
[PRD_scent_belief](PRD_scent_belief.md)) is strictly separate: a zero-token template
provider by default (`AF-t21`), natural-language only, within the agreed word limit, and
never a coordinate channel (`AE-27`).

## Per-turn decision cost (`M6-011`, measured 2026-08-04)

One turn's decision — the belief update from a scent observation and a hint, then the
evasive-move policy — is pure Python over the grid with no I/O, so it is bounded by
construction. `scripts/benchmark_decision.py` measures it and writes
`results/decision_benchmark.json`; `test_decision_benchmark.py` gates a loose worst-case
bound so a slow machine cannot flake.

| Grid | mean | worst | response budget |
|---|---|---|---|
| 7×7 (negotiated minimum) | ~0.9 ms | ~2 ms | 30 000 ms |
| 20×20 | ~1.5 ms | ~3.5 ms | 30 000 ms |

The decision spends roughly **four orders of magnitude** under the 30 s response timeout
(`network_and_league.response_timeout_sec`), so computational fairness is never in doubt —
the Thief cannot stall, and its move never risks the deadline. Feeds `M9-006`.
