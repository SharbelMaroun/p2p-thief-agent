# Research report — parameter sensitivity and performance analysis

The book names this file (p.142/265) and sets its standard in one line: the research must
be **"based on numbers and not on guesses"** (p.142/266). Guidelines §9.1 asks for
"systematic experiments with controlled changes to parameters", §9.3 for bar, line, heatmap
and box-plot visualisations, `M9-006c` for "experiment tables with **run counts**, not
anecdotes".

Every number below comes from `tests.unit.test_strategy_comparison.simulate` — the same
harness the `M6-015` test gates. To reproduce:

```text
uv run python scripts/run_experiments.py     # writes results/*.json
uv run python scripts/render_charts.py       # writes assets/chart-*.svg
```

## The finding that matters

![The two metrics rank the strategies in opposite directions](../assets/chart-metric-disagreement.svg)

**`M6-015`'s evidence measures a quantity the game does not score.**

The shipped comparison asserts that belief-driven evasion beats the blind baseline on
**total survival steps**, over four fixed openings. It does, and comfortably: 125 against
52, a 2.4× advantage. That test passes and is not wrong about what it measures.

Widening the scenario set to all 24 perimeter openings, and then scoring the runs the way
Appendix F actually scores them:

| Metric | blind | belief | Winner |
|---|---|---|---|
| Total survival steps | 437 | **810** | belief (1.85×) |
| Scenarios reaching the horizon | 11 | **23** | belief |
| **League points** (10 survive / 5 captured) | 175 | **235** | **belief** |

> **Corrected 2026-08-07.** This table previously read `175` for blind against
> `140` for belief — our policy losing to a random walk on the only metric a
> sub-game pays. The cause was lexicographic ranking putting threat distance
> first, which walks a Thief into a corner; `choose_evasive_action` now sums
> distance and mobility. Re-checked on board sizes 5-9, randomised openings,
> barrier layouts and horizons 15-50. See `M6-015c` and the academic report §3.1.


**The opponent model is part of the result, and ours is the weakest plausible one.** Every
number above is measured against a Cop that steps to minimise Manhattan distance to the
Thief's *current* cell. Re-run against two stronger pursuers on the same 24 openings
(2026-08-07):

| Cop | belief escapes | belief points |
| --- | ---: | ---: |
| greedy (the harness Cop) | 23/24 | 235 |
| herding — closes, and breaks ties to shrink our room | 23/24 | 235 |
| **anticipating** — chases the centroid of our *next* legal cells | **8/24** | **160** |

Belief beats the blind arm against all three, so the fix in §3.1 is real and not an artifact
of the opponent. But **23/24 is a greedy-Cop number, not a league expectation.** A classmate
whose pursuit anticipates one turn ahead cuts our escape rate by roughly two thirds, because
running from where the Cop *is* is exactly what an anticipating Cop exploits.

This is stated rather than quietly omitted for the same reason the previous table was left
visible: an evaluation is only as strong as its opponent, and ours is currently a weak one.
Improving against anticipation is open work, not a claim already banked.


### Against an anticipating Cop: a measured ceiling and five failed attempts

`M6-015c` left the evasion policy at **8/24 escapes (160 points)** against a Cop that chases
the centroid of the Thief's next legal cells, versus 23/24 against a greedy one. The obvious
next question is whether that is a policy gap or a property of the board.

**It is a policy gap.** The anticipating Cop is deterministic, so optimal Thief play is a
finite search over `(cop, thief, step)` and can be solved exactly. Solved:

| Cop | optimal | shipped |
| --- | ---: | ---: |
| greedy | 24/24 (240) | 23/24 (235) |
| herding | 24/24 (240) | 23/24 (235) |
| **anticipating** | **24/24 (240)** | **8/24 (160)** |

Escape is always available. Sixteen scenarios are left on the table. (The solver knows the
Cop's exact cell *and its policy*, so this is a generous bound and not reachable by a legal
agent — the same role the companion Cop's `oracle` arm plays.)

**Five attempts to close it, all measured, all worse than shipping `distance + mobility`:**

| Attempt | vs anticipating |
| --- | ---: |
| shipped: `distance + mobility` | **160** |
| one-ply worst case | 160 (no change — see below) |
| `+ wall_margin` term, weights swept | 120–160 |
| true minimax, depth 1–5 | 130–140 |
| territory (cells we reach first), weights swept | 120 |
| search against a greedy Cop *model*, depth 2–10 | 130–140 |

Three of those failures are informative rather than merely negative:

* **One ply changed nothing** because `mobility` is constant across the Cop's replies, so the
  minimum was a fixed offset and the ordering never moved. A search whose evaluation does not
  vary with the opponent's choice is not a search.
* **Deeper worst-case minimax got monotonically worse.** Against a perfect pursuer the Thief
  is lost, so every move evaluates as lost, the tie-break decides, and the policy stops
  playing to survive the opponent it actually has.
* **Territory collapsed to 120 — never escaping.** Owning more board is not the objective when
  the objective is to still exist at turn 35; the Thief traded safety for area.

The belief is not the bottleneck either: the believed Cop cell is exact 64% of the time
against greedy and 37% against anticipating, with mean error 0.46 and 0.77 cells. Wrong
enough to punish a ten-ply plan, not wrong enough to explain an 8/24.

**Left open, deliberately.** The gap is real and the ceiling is known; what is missing is a
policy that exploits a *modelled* opponent without inheriting the model's errors — most
likely opponent modelling learned from observed moves rather than assumed in advance. Shipping
any of the five would have made the agent worse, and the numbers are here so the next attempt
starts from what has already been ruled out.

Appendix F pays the Thief **10 for reaching the survival threshold** and **5 for being
captured**, both `Fixed`. There is nothing in between. A policy that reliably survives 28 of
35 turns scores *exactly* what one caught on turn 2 scores.

So the two arms differ in kind, not degree:

![Survival steps by evasion arm](../assets/chart-survival-distribution.svg)

The blind baseline is **bimodal** — 11 outright escapes, the rest caught within 2–7 turns,
almost nothing between. Belief-driven evasion is **consistent** — median 29, standard
deviation cut from 15.8 to 7.6 — but it converts far fewer scenarios into the only outcome
that pays.

![Outright escapes](../assets/chart-full-escapes.svg)

Paired scenario by scenario, belief wins 13 and **loses 11**. On steps it is barely better
than a coin flip; on points it is behind.

**What this is not.** It is not proof that the blind baseline is a better strategy — it is
one deterministic Cop on one board, and a pursuing opponent that reacted to evasion could
easily reverse it. What it *is*: evidence that the acceptance criterion behind `M6-015` does
not track the scoring rules, and that the four-scenario sample was too small to notice.
Recorded as an open row rather than silently patched, because changing the strategy is a
larger decision than this batch.

## Protocol

| Aspect | Value |
|---|---|
| Harness | `simulate` — a deterministic greedy pursuing Cop, no randomness anywhere |
| Scenarios | **24** — every perimeter opening, Cop and Thief on opposite cells |
| Design | **paired** — scenario *i* gives both arms the identical Cop and opening |
| Arms | `blind` (ignores scent), `belief` (senses the Cop's trail and flees the believed cell) |

**The scenario set is widened, not repeated.** The harness is fully deterministic, so
running it forty times returns the identical answer forty times. That would inflate the run
count without adding a single bit of evidence — the one way an `n` can lie. Enumerating the
perimeter is a genuinely larger sample of the same question.

## Parameter sweeps (`M9-006a`)

Appendix F marks each parameter `Fixed`, `Minimum` or `Negotiation`; `Minimum` "may be
raised by agreement but never lowered", so every sweep runs **upward from** its minimum.

![Mean survival against board size](../assets/chart-sweep-board-size.svg)

![Parameter sensitivity](../assets/chart-parameter-sensitivity.svg)

More room helps both arms, and helps the blind baseline at least as much — a larger board
does not rescue the metric disagreement.

![League points against the survival threshold](../assets/chart-sweep-horizon.svg)

Raising the horizon makes things **worse** for belief, not better: a longer game is more
time for a deterministic pursuer to close, and the consistent-but-not-escaping policy
converts fewer scenarios into points the further out the threshold moves.

## Decision cost

Recorded separately by `scripts/benchmark_decision.py` in `results/decision_benchmark.json`:
mean 0.86 ms and worst case 2.11 ms on 7×7 over 3 000 iterations; 1.53 ms and 3.47 ms on
20×20 over 1 000. Against the negotiated 30 000 ms response timeout the worst case is
**0.012%** of budget, so computational fairness is not close to contested.

## Learning curves

Required only **"if RL was used"** (p.81/189). This policy is deterministic and weight-free,
so there is no convergence to plot, and the book is silent on a substitute. The paired
comparison above stands in its place — it answers the same question a learning curve
answers, and in this case it answers it uncomfortably.

## Threats to validity

1. **One Cop.** A single deterministic greedy pursuer. An opponent that anticipated evasion
   would change every number here.
2. **No live opponent.** No counted league game has been played.
3. **Perimeter openings only.** Interior starts are unmeasured, and the metric disagreement
   may be sensitive to them.
4. **Determinism cuts both ways.** No sampling noise, so each scenario's result is exact —
   but 24 scenarios is still 24, and "no effect detected" is not "no effect".

## Addendum 2026-08-08 — the live loop now plays the measured arm

Until 2026-08-08 every number above described a policy the wire never ran: the live
`decide` adapter played the blind baseline with an empty `smell_grid`. `M9-026a` closes
that — the served Thief now runs exactly the `_belief` arm this report measures
(fresh-per-observation belief, `choose_evasive_action`, involuntary emission), so the
figures here are claims about the deployed agent, not about a harness-only artifact.

Two cross-repository results bear on threat 1 ("one Cop"). The companion's new opponent
grid (`p2p-cop-agent`, `M9-30`) measures its arms against a **distance+mobility evader —
this repository's own shipped shape** — and cannot capture it with any arm, including a
barrier stack aimed with referee truth: 0/40 across the board. Read from this side, that
is evidence the shipped evasion is strong against the entire pursuit-plus-barriers class
its companion could build, not only against the greedy harness Cop. The anticipating-Cop
gap above (8/24, ceiling 24/24) remains this policy's one measured weakness, and remains
open: the same grid confirms the five failed attempts were not underpowered variants of a
working idea — reactive play does not beat one-step prediction from either side of the
board. The next attempt should model the pursuer from observed moves.
