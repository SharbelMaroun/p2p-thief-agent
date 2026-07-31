# M3 Local-State, Scoring and Baseline-Integration Record

Implementation date: 2026-07-29

Branch: `agent/thief-baseline-strategy`

Status: **CONTRACT-INDEPENDENT M3 IMPLEMENTATION COMPLETE — AWAITING COORDINATOR
ACCEPTANCE.** This is a descriptive implementation record. It does not declare any
task `DONE`; the `DONE`/acceptance verdict for `M3-001`…`M3-004` remains the
coordinator's, and the `TODO.md` rows are left unchanged.

The Thief-local state, scoring, and baseline integration are implemented independently
behind the public SDK in a new `state/` package. They use only Appendix E/F `CONFIRMED`
values with explicit inputs, author no shared-contract byte, import no Cop module, and
read no Cop-private truth. FastMCP, protocol runtime, and live peer runtime remain
separate `PENDING` milestones.

## Modules

| Module | Task | Responsibility |
|---|---|---|
| `state/local_state.py` | M3-001 | Immutable `ThiefLocalState` and `ThiefSnapshot`: the Thief's own position, step count, known barriers, and an append-only history. Every transition returns a new state; `advance` resolves a move through the domain and pushes a history snapshot |
| `state/known_barriers.py` | M3-002 | Immutable `KnownBarriers`: a map of disclosed barrier cells to the step each was learned, on-board validated, keeping the earliest disclosure. Holds no Police position and no unobserved barrier |
| `state/scoring.py` | M3-003 | Official FIXED Appendix F Table 17 points, the `Outcome` enum, `thief_score`, and `resolve_outcome` for locally determinable terminal conditions |
| `state/policy.py` | M3-004 | Binds the deterministic baseline (`EXC-001`) to local state: `choose_local_action`, `rank_local_actions`, `step_with_baseline`, and `local_outcome`. A plausible Police position is always an explicit argument |

## Decisions and interpretations

- **Scoring is FIXED (`AF-017`).** Capture Cop/Thief `20`/`5`, survival Cop/Thief
  `5`/`10`, tie `2` each, technical loss `0` (project book Appendix F Table 17). These
  are official fixed values, not implementation choices, and no shared-contract byte
  depends on them.
- **Technical loss is scored from the Thief's own perspective (`AE-019`).** The book
  fixes the penalised party at zero and does not fix the opponent's column, so this
  module scores only the local Thief's technical loss as `0`. That matches the
  protocol's existing terminal technical-loss score (`session_audit.py` sets the local
  score to `0` on `COMMITMENT_MISMATCH`). The Cop's technical-loss score is not invented.
- **Survival horizon default `35` (`AF-015`).** `DEFAULT_SURVIVAL_THRESHOLD = 35` is the
  Appendix F Table 15 `MINIMUM`; it is a per-call argument and not a Cop-owned byte.
- **Tie is not inferred locally.** `resolve_outcome` classifies only capture, survival,
  and technical loss, which are locally determinable. A tie is a coordinator or
  mutual-agreement result (`AE-019`); `thief_score(Outcome.TIE)` still scores it when it
  is declared.
- **Capture outranks survival at the horizon.** A Thief captured on the same step it
  would otherwise reach the survival horizon is scored a capture, consistent with
  capture being an immediate terminal condition.
- **Barrier provenance keeps the earliest disclosure.** Re-recording a known barrier is
  a no-op that preserves the first step it was learned, so provenance is stable and
  auditable.

## Independence and privacy

- No import of any Cop package module; no read of the Cop repository at runtime.
- No shared mutable state or filesystem path with Cop.
- Local state stores no objective/private Police truth. The Police position is accepted
  only as an explicit auditable input to `local_outcome` and to the strategy layer as a
  *plausible* cell, never as stored local truth.

## Boundary and remaining scope

- These modules add local-truth state, scoring, and baseline binding only. They contain
  no protocol wire behaviour, no canonicalization, and no commit-reveal; those remain
  the M4 milestone.
- There is still no live turn state machine driving a full game loop across two peers;
  `advance` applies one already-chosen legal action. Enforcing barrier-versus-movement
  exclusivity across a complete turn remains the future turn state machine's job (see
  the M2 boundary note in `M2_DOMAIN.md`).
- Exact live-turn event ordering across move, barrier disclosure, capture check, and
  scent remains `U-014`, pending an accepted shared protocol.

## SDK exposure

`p2p_thief_agent.sdk` re-exports the whole `state` module and its public symbols
(`PS-007`), so adapters reach local-state behaviour only through the SDK boundary.

## Verification

`ruff` clean; the four `state` modules at 100% branch coverage; file-length, secret,
CLI, and `git diff --check` gates pass; the contract checker remains fail-closed at
`PENDING` / exit 1.

> The suite total recorded here when M3 landed was `452 passed` at `95.36%`. That
> counted the Option-B protocol layer and its conformance tests, which commit
> `11d0c7a` removed on 2026-07-29, and the total has moved several times since as
> M5 landed. **Whole-suite totals are deliberately not restated**: a hard-coded
> count is stale the moment the next test lands, and a number that rots is worse
> than no number because a reader trusts it. The per-module claim above is the
> durable one; run the suite for the current total.
