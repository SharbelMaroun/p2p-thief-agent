# Barrier-aware evasion v2 — experimental strategy (default-off)

Status: **SHIP_CANDIDATE**, 2026-08-14. The production default remains `"current"` (the shipped
`choose_adaptive_action`). Whether to flip the default to `"barrier_aware_v2"` is the
coordinator's decision; nothing in this branch does so, and no committed config enables it.

## The problem

The shipped evasion is already 24/24 against every *mover* archetype (`results/pursuer_grid.json`,
`adaptive_decoded`). Its one measured weakness is a Cop that combines interception with
proactive barrier placement: against `interceptor_waller` it converts only **8/24**
(`results/waller_grid.json`). The cause is structural — its exact solver (`strategy/escape_search.py`)
freezes the barrier field and plans against movement alone, so a line planned as if the walls
never come walks into the trap the waller builds.

## What was built (all isolated; production default unchanged)

| Module | Role |
|---|---|
| `strategy/waller_models.py` | Deterministic walling archetypes in `src` (`greedy_waller`, `interceptor_waller`). Byte-parity with the committed `experiment_wallers` grid (8064 states identical); every wall they propose passes `domain.barriers.validate_barrier_placement` — strategy proposes, the domain validates. |
| `strategy/barrier_search.py` | Exact escape solver carrying the barrier mask **and** the remaining quota *inside* the recursion, in the same step order as `escape_search`. With quota 0 it equals `escape_search.survives` exactly (cross-checked). Depth-bounded (receding horizon). |
| `strategy/barrier_aware_policy.py` | `choose_barrier_aware_action`: keeps the adaptive pick when it already survives the assumed waller, substitutes a walled-safe action only when the adaptive pick would be trapped, else falls back to the adaptive pick. `evasion_action` dispatches the named strategy. |
| `orchestration/thief_policy.py` | `make_decide(strategy=…, barrier_quota=…)`. `"current"` (default, and any unknown value) is `choose_adaptive_action` byte for byte. |
| `adapters/play_command.py` | Reads `[strategy].policy` from the private TOML, default `"current"`. Opt-in only. |
| `scripts/experiment_barrier_aware.py` | Paired old-vs-new grid → `results/barrier_aware_grid.json`, with a latency profile. |

## The finding: engage every step, not on danger

A first cut gated the planner on danger (a disclosed barrier or an imminent one-wall seal).
Measured, it recovered **nothing** — 8/24 unchanged, zero overrides. Against a walling
interceptor the escape space is lost *before* a wall is ever placed, so the gate opened too
late. Planning from the first move instead ("always-on") captures the ceiling.

### Escapability ceiling (exact solver, fed the true Cop cell)

All 24 perimeter openings are escapable against **both** wallers with perfect play — refuting
the earlier note (`M6-032`) that the wall-armed equal-speed pursuer is structurally winning.

| waller | ceiling (truth-fed, exact) |
|---|---|
| greedy_waller | 24/24 |
| interceptor_waller | 24/24 |

### Conversion, belief-fed and live-faithful (decoded belief, barriers disclosed)

| opponent | shipped `adaptive` | `barrier_aware_v2` |
|---|---|---|
| interceptor_waller | **8/24** (160 pts) | **24/24** (240 pts) |
| greedy_waller | 23/24 (235 pts) | **24/24** (240 pts) |
| greedy mover | 24/24 | 24/24 |
| herding mover | 24/24 | 24/24 |
| anticipating mover | 24/24 | 24/24 |
| interceptor mover | 24/24 | 24/24 |

interceptor_waller reaches 24/24 at **every** search depth tested (6, 8, 10, 12). The shipped
default depth is **8** (a small margin over the depth-6 floor). **No mover regression.**

### Latency (worst-case probe: always-on, over 10 920 decisions)

| depth | median | p95 | p99 | max | budget |
|---|---|---|---|---|---|
| 10 | 136 ms | 418 ms | 620 ms | 1673 ms | 30 000 ms |

The worst single decision is ~1.7 s against a 30 s response budget (120 s in the uohay26
config) and a 60–180 s watchdog. Depth 8 is faster; see `results/barrier_aware_grid.json` for
the shipped-depth profile. A strategy exception still degrades to a truthful `MOVE:STAY`
(`M6-033`), so the planner can never cost the match.

## Why this is safe to graft on

1. **`"current"` is byte-identical to today.** `evasion_action("current", …)` calls
   `choose_adaptive_action` with the same arguments; an unknown strategy resolves to `"current"`.
2. **The adaptive pick is the floor.** The planner only overrides an *unsafe* adaptive pick and
   otherwise returns it or falls back to it.
3. **Deterministic.** No RNG (book §6 sanctions deterministic minimax/expectimax). Replay
   verifies the logged move; commit-reveal, sealing, audit, and replay bytes are untouched.
4. **Legality is the domain's.** Movement and barrier legality come from `domain/`; strategy
   proposes, the domain validates.

## Known limits / not done

- The planner assumes an `interceptor_waller` (then `greedy_waller`) opponent model. A future
  Cop with a genuinely different walling policy is not separately modelled; the fallback to the
  shipped policy bounds the downside.
- Anti-predictability (controlled randomisation among equal safe actions, Phase D) is **not**
  implemented — the book prefers determinism and it was out of scope for this pass.
- Real counted opponents so far place few/late barriers (G009: 2 barriers at steps 13–14), so
  the live benefit depends on facing a stronger waller than seen to date; the change costs
  nothing against the opponents already seen.

## Reproduce

```powershell
uv run python scripts/experiment_pursuers.py       # baseline movers  -> results/pursuer_grid.json
uv run python scripts/experiment_wallers.py        # baseline wallers -> results/waller_grid.json
uv run python scripts/experiment_barrier_aware.py  # paired old-vs-new + latency -> results/barrier_aware_grid.json
uv run pytest tests/unit/test_waller_models.py tests/unit/test_barrier_search.py \
              tests/unit/test_barrier_aware_policy.py tests/unit/test_evasion_selector.py
```

To enable the experimental policy **locally** (never committed): set in the private
`config/thief/game.toml`:

```toml
[strategy]
policy = "barrier_aware_v2"
```
