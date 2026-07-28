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
| `domain/barriers.py` | M2-04 | Pure disclosed-barrier placement validation and immutable `BarrierField`; on-board, one orthogonal step from the Police cell, not on it, unique, within quota |
| `domain/capture.py` | M2-05 | `evaluate_capture` with fixed precedence over the three official capture causes |

## Decisions and interpretations

- **Direction vs. adjacency.** N/S/E/W labels resolve to row/column deltas per the
  configured `OriginCorner`; orthogonal adjacency (barriers, trapping) is
  origin-independent (`|Δrow| + |Δcol| == 1`).
- **STAY legality vs. rescue.** STAY is always a legal action, but it is not a cardinal
  escape. A Thief whose four cardinal neighbors are all off-board or barriered is
  captured (`AE-046`), consistent with the coordinator instruction that STAY does not
  rescue.
- **Capture precedence.** When multiple conditions hold simultaneously, precedence is
  fixed and deterministic: `SAME_CELL` > `BARRIER_ON_THIEF` > `TRAPPED`.
- **Barrier quota default.** `DEFAULT_BARRIER_QUOTA = 14` is the Appendix F Table 15
  `MINIMUM` (`AF-015`); it is configurable per call and is not a Cop-owned contract
  byte.

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
