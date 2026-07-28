# M2 Domain Implementation Record

Implementation date: 2026-07-28

Branch: `agent/thief-m2-domain-option-b`

Status: **CONTRACT-INDEPENDENT M2 DOMAIN COMPLETE**

The Thief core domain is implemented independently behind the public SDK using only
Appendix E/F `CONFIRMED` rules. It authors no shared-contract byte, imports no Cop
module, and reads no Cop-private truth. FastMCP, commit-reveal, protocol runtime, and
shared-contract runtime remain deferred until Cop `0.2.0-proposed`.

## Modules

| Module | Task | Responsibility |
|---|---|---|
| `domain/coordinates.py` | M2-01 | Immutable hashable `Coordinate` (row/column JSON order) and the five fixed `Action` tokens; rejects booleans, floats, malformed pairs, and unknown tokens |
| `domain/board.py` | M2-02 | Configured square `Board` with `OriginCorner`, axis start index, inclusive bounds, start-position validation, and origin-independent adjacency |
| `domain/movement.py` | M2-03 | One-orthogonal-step-or-STAY movement per origin convention; off-board and barriered targets reject; deterministic legal-action and cardinal-move enumeration |
| `domain/barriers.py` | M2-04 | Pure disclosed-barrier placement validation and immutable `BarrierField`; on-board, on the Police's current cell or one orthogonally adjacent cell, unique, within quota |
| `domain/capture.py` | M2-05 | `evaluate_capture` over the three capture causes, applying an implementation-chosen tie-break when several hold at once |

## Decisions and interpretations

- **Direction vs. adjacency.** N/S/E/W labels resolve to row/column deltas per the
  configured `OriginCorner`; orthogonal adjacency (barriers, trapping) is
  origin-independent (`|Δrow| + |Δcol| == 1`).
- **Barrier placement relationship (official).** Project book Chapter 3.4 (PDF p.37 /
  printed p.21) permits the Police to give up movement and place a barrier either on
  the Police's own current cell or on one orthogonally adjacent cell. The validator
  accepts a target that is `== police_position` or exactly one orthogonal step away,
  and rejects diagonal, multi-cell, off-board, duplicate, and quota-exhausting
  placements.
- **Barrier replaces movement (official).** Placing a barrier consumes the Police's
  movement for that turn (book Chapter 3.4). This is a confirmed rule, not an open
  question. See the M2 boundary note below for why the pure API cannot enforce it yet.
- **STAY legality vs. rescue.** STAY is always a legal action, but it is not a cardinal
  escape. A Thief whose four cardinal neighbors are all off-board or barriered is
  captured (`AE-046`), consistent with the coordinator instruction that STAY does not
  rescue.
- **Capture precedence (PROVISIONAL / implementation-chosen).** No official source
  fixes an ordering when several capture conditions hold at once. The implementation
  applies a deterministic tie-break of `SAME_CELL` > `BARRIER_ON_THIEF` > `TRAPPED`
  purely so results are repeatable; this ordering is not an official fixed precedence
  and remains subject to the approved shared contract.
- **Barrier quota default.** `DEFAULT_BARRIER_QUOTA = 14` is the Appendix F Table 15
  `MINIMUM` (`AF-015`); it is configurable per call and is not a Cop-owned contract
  byte.

## M2 boundary: barrier-versus-movement exclusivity

- M2's pure barrier API validates a single disclosed barrier placement in isolation.
- M2 does not yet contain the live turn/action state machine.
- Therefore M2 cannot currently enforce barrier-versus-movement exclusivity across a
  complete turn: nothing in the pure API prevents a caller from also moving.
- The barrier-replaces-movement rule is a confirmed official rule (book Chapter 3.4),
  not unresolved. The future turn state machine must preserve and enforce it so that a
  turn contains either a move or a barrier placement, never both.

## SDK exposure

`p2p_thief_agent.sdk` re-exports every public domain symbol and the whole `domain`
module (`PS-007`). Adapters reach domain behavior only through this boundary.

## Independence and privacy

- No import of any Cop package module; no read of the Cop repository at runtime.
- No shared mutable state or filesystem path with Cop.
- No objective/private Police truth stored in Thief-local state; the Police position
  is accepted only as an explicit auditable input to pure validators.

## Remaining domain ambiguity

- Exact event ordering across a live turn (move, barrier disclosure, capture check,
  scent) remains `U-014`, pending an accepted shared protocol; the pure validators
  here do not fix a turn sequence.
- Multi-barrier-per-turn limits and any per-turn placement cadence are protocol-level
  and are not decided here.
