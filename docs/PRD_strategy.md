# PRD — Thief Strategy

Status: deterministic baseline policy **implemented** as a contract-independent module
on branch `agent/thief-baseline-strategy`. Belief, scent, look-ahead beyond two ply,
and any verbal layer remain out of scope and blocked.

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

Because scent physics and belief are M6 and blocked, the policy cannot infer a Police
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
M3-004: formal M3 remains `BLOCKED`, and this module adds no local state, no history,
no scoring, and no turn state machine. Manhattan distance and the criterion order are
implementation choices, not official rules, and no shared-contract byte depends on
them.
