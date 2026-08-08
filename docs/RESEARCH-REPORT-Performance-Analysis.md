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

![Both metrics now rank belief above blind, after the ranking fix](../assets/chart-metric-disagreement.svg)

**`M6-015`'s evidence measures a quantity the game does not score.**

The shipped comparison asserts that belief-driven evasion beats the blind baseline on
**total survival steps**, over four fixed openings. It does, and comfortably: 140 against
52, a 2.7× advantage. That test passes and is not wrong about what it measures. (It read
125 until 2026-08-08; the wall-pressure term in `M6-032` raised it, and
`results/strategy_comparison.json` is regenerated rather than quoted from memory.)

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
mean 0.56 ms and worst case 2.01 ms on 7×7 over 3 000 iterations; 1.52 ms and 3.61 ms on
20×20 over 1 000. Against the negotiated 30 000 ms response timeout the worst case is
**0.012%** of budget, so computational fairness is not close to contested.

Unlike every other figure in this report these two are **machine-dependent** — they are wall
clock on the laptop that ran them, and they move a little on every re-run. They are quoted to
establish an order of magnitude, not a reproducible constant; the reproducible claim is the
ratio to the timeout, which stays four orders of magnitude clear.

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

## Addendum 2026-08-08 (ii) — the sixth attempt, and where the gap actually lives

The stronger-pursuer table above must be read with a correction. Its herding and
anticipating rows were measured with session-scratch pursuers that were never
committed; `M6-029` commits the three archetypes (`strategy/pursuer_models.py`), and
the committed herding and anticipating are **stronger**. Reproducible numbers
(`scripts/experiment_pursuers.py`, `results/pursuer_grid.json`, same 24 paired
perimeter openings):

| arm | greedy | herding | anticipating |
| --- | ---: | ---: | ---: |
| shipped `distance + mobility` | 23/24 (235) | **8/24 (160)** | **5/24 (145)** |
| sixth attempt, argmax-fed | 23/24 (235) | 4/24 (140) | 4/24 (140) |
| sixth attempt, top-2 uncertainty set | 23/24 | 2/24 | 4/24 |
| **sixth attempt, truth-fed (instrument)** | **24/24** | **24/24** | **24/24** |

Robustness agrees (anticipating at 9×9: shipped 10/32 v adaptive 8/32; at horizon 50:
5/24 v 4/24). So the sixth attempt — classify the pursuer online from the believed
trajectory, best-respond with exact escape sets — **fails like the five before it and
is not wired**, per the `M6-015b` reversion rule.

**What it bought is the diagnosis.** Truth-fed, the identical machinery reaches the
theoretical ceiling against every archetype: the classifier works, the solver is
exact, and the entire collapse from 24/24 to 4/24 is the estimator's ~1-cell argmax
error, which turns an exact escape line into a walk into the real pursuer. This
refutes this report's own earlier claim that the belief is "wrong enough to punish a
ten-ply plan, not wrong enough to explain an 8/24" — it is exactly wrong enough, and
now that is measured rather than argued. Planning against a top-2 uncertainty set
makes things worse (the true cell escapes the set often enough that intersection only
empties it), which rules out cheap robustness at the planning layer.

**Attempt #7 therefore targets perception, not policy.** The emission physics are
agreed, hash-locked, and deterministic; the current likelihood weights cells by raw
observed intensity, discarding everything the model knows about how a trail decays
and stacks. A model-matched estimator — score candidate pursuer cells by how well the
*whole observed window* matches the field the model predicts for them — should
localise the emitter to near-truth, and the truth-fed row above is the measured prize
if it does: **24/24 against every committed archetype, 240 league points.** The grid
re-run is one command because, unlike attempts one through five, the sixth attempt's
machinery is committed.

## Addendum 2026-08-08 (iii) — the seventh attempt closes the gap: 240/240

Addendum (ii) predicted the prize; this one banks it. The estimator was rebuilt as a
**model-matched emitter decoder** (`perception/emitter_decoder.py`, `M6-031`): the
locked physics `τ' = (1−ρ)τ + Δτ` has non-negative terms, so the residual between
consecutive observations is *exactly* the newest emission stamp, and matching that
residual against the agreed 5×5 profile localises the emitter — the true cell scores
zero mismatch, the best rival at least `(0.9 − 0.62)²`. The full factorial grid
(`scripts/experiment_pursuers.py`, 24 paired perimeter openings):

| arm | greedy | herding | anticipating |
| --- | ---: | ---: | ---: |
| shipped policy, raw belief | 23/24 (235) | 8/24 (160) | 5/24 (145) |
| adaptive policy, raw belief | 23/24 (235) | 4/24 (140) | 4/24 (140) |
| shipped policy, **decoded belief** | 23/24 (235) | 8/24 (160) | 18/24 (210) |
| **adaptive policy, decoded belief** | **24/24 (240)** | **24/24 (240)** | **24/24 (240)** |
| truth-fed ceiling (instrument) | 24/24 | 24/24 | 24/24 |

Robustness agrees where every earlier attempt failed hardest: anticipating at 9×9 —
**32/32**; at horizon 50 — **24/24** (the raw-belief arms manage 8–10/32 and 4–5/24
there). The legal agent now equals the truth-fed ceiling on every measured cell, so
the anticipating-Cop gap that survived six attempts — 8/24 at its best — is **closed,
not narrowed**, and the factorial design shows both halves were necessary: the
decoder without the adaptive planner reaches 18/24, the planner without the decoder
4/24, together 24/24.

Both halves are wired into the live loop (`M9-026a` path): the decoder with
partial-window handling (the wire carries 5×5 windows, so scoring trusts only cells
both observations covered, and a stale observation falls back to single-stamp
matching) and a deviation guard (a field the model cannot explain anywhere yields
explicit no-information rather than a confident wrong answer — and is, incidentally,
evidence of a rule-23 deviation). Authority verified before building: the book fixes
the physics and frees the inference engine (pp. 48/121, 94/211), and the reference's
own `BeliefGrid` runs a model-matched observation step, so this is the prescribed
path taken seriously.

**Threats to validity, updated.** Threat 1 ("one Cop") is retired — three committed
archetypes, factorial arms, robustness configs. What remains: the archetypes place no
barriers (the companion's grid shows a barrier-using pursuer is a different class —
its own truth-aimed stack still cannot corner a mobility evader, so the direction of
that risk favours the Thief), no live opponent has been played, and the decoder's
exactness assumes the opponent honours the hash-locked emission model — a deviator
degrades us to the uniform-safe belief, and degrades itself to a rule-23 sanction.


## The results-analysis notebook: checked, and NOT a Jupyter file

**Recorded 2026-08-08 after an audit finding that turned out to be wrong.** An external review
flagged 'no analysis notebook in either repo' against guidelines section 9.2, which asks for a
'results analysis notebook'. Asked directly, the book **does not require a Jupyter `.ipynb`**:
it defines the deliverable as a Markdown research report and names it -
`RESEARCH-REPORT-Performance-Analysis.md` under `/docs` - which is exactly the file this
repository already ships. The pinned reference simulator contains no notebook either; its
analysis is markdown plus plain Python scripts.

The finding was an **invented requirement**: a real rule (section 9.2) read through the word
'notebook' rather than through what the source says the artifact is. It is written down here so
the next reader does not 'fix' it by adding a Jupyter file that satisfies nothing, and because
a review that manufactures requirements is a review that wasted the time it cost.
