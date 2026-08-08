# Academic report — model, decisions, results

Covers `M9-011`, `M9-011a`, `M9-011b`, `M9-011d`, `M9-007c`.

The README carries the six components §9.4.2 requires. This is the body underneath: the
formalism in the book's own notation, the architectural decisions with what each one cost,
and the measurements — including the one that does not flatter us.

## 1. The formalism

### 1.1 The Dec-POMDP tuple

The book models the game as a decentralised partially-observable Markov decision process
(p.4/109), an ordered tuple of eight components:

$$\langle n,\; S,\; \{A_i\},\; P,\; R,\; \{\Omega_i\},\; O,\; \gamma \rangle$$

| Symbol | Meaning | In this repository |
| --- | --- | --- |
| $n$ | agents | 2 — Cop and Thief, symmetric peers |
| $S$ | state space | board occupancy × barrier placement × turn index |
| $A_i$ | agent $i$'s actions | move N/E/S/W, or place a barrier — never both in one turn |
| $P$ | transition function | deterministic; `domain/` applies a legal move or refuses it |
| $R$ | reward | Appendix F table 17: capture, survival, tie, technical loss |
| $\Omega_i$ | observations | own cell, disclosed barriers, the opponent's hint |
| $O$ | observation function | partial — neither agent ever sees the other's position |
| $\gamma$ | discount factor | $\gamma \in [0,1]$; unused, because our policy is myopic (§2.2) |

The partial observability is the whole problem. If $O$ were full, the pursuit would be a
shortest-path computation and there would be nothing to model.

### 1.2 The scent model

Scent intensity in cell $(i,j)$ updates once per full turn (p.27/115):

$$\tau_{ij}(t+1) = \max\left(0,\; (1-\rho)\cdot\tau_{ij}(t) + \Delta\tau_{ij}\right)$$

with $\rho = 0.10$ the decay rate and $\Delta\tau_{ij}$ the intensity emitted this turn. The
$\max(0,\cdot)$ matters: without it, floating-point drift can carry a decayed cell slightly
negative, and a negative prior is not a probability.

> **Two contradictions in the source, disclosed under chapter 110.** Both are recorded in
> `docs/SPECIFICATION_CONFLICTS.md` as `C-014` and `C-015`; they were identified during M6
> and are restated here because §1.2's formula relies on the resolution.
>
> **`C-014`** — the book's prose (ch. 4.3, p.43; `inst/:930`) says the factor $(1-\rho)$
> means "the existing scent is **reduced by 90%**". Its own formula says the opposite:
> $(1-\rho) = 0.90$ *retains* 90%, reducing by 10%. We implement the **formula**, because
> rule 23's lock is taken over the formula and because the prose reading decays ten times
> too fast, erasing the history trail the mechanism exists to leave.
> `test_scent_regression.py` pins $0.9\tau + \Delta\tau$.
>
> **`C-015`** — the book (ch. 4.4, p.46) says raising $\rho$ toward 1.0 would leave the
> board "**saturated** with scent". Reversed: $\rho \to 1.0$ drives $(1-\rho) \to 0$, so
> scent vanishes almost immediately. Saturation is what $\rho \to 0$ approaches. Sensitivity
> work sweeps in the correct direction.

> **A third contradiction, in the scoring boundary** (`M3-005c`, `C-017`). Appendix F table
> 15 sets `[Step Limit]` and `[Survival Threshold]` to the **same value**, 35. Two readings
> follow and the book never chooses: does this agent win by surviving *exactly* 35 steps, or
> must it exceed them? One turn separates them, and a whole sub-game — 20 points — hangs on
> it. For the Thief this is not a corner case but the **entire win condition**: surviving is
> how this agent scores when it is not captured.
>
> **Where it is.** In the mandatory parameters table, the document both peers negotiate
> from — not in a figure. Two agents built from the same appendix can disagree about who won
> a game they both played correctly.
>
> **What we chose.** The **inclusive** horizon — completing step 35 uncaptured is a win.
>
> **Why.** Chapter 3 table 2 (PDF p. 38) defines survival as lasting "the limit of valid
> moves" without capture, and table 15 makes that limit *equal* the threshold. The two
> tables together settle what either alone leaves open, so no coordinator ruling was needed.
> `resolve_outcome` already used `steps >= survival_threshold`; what was missing was the
> record and the boundary test. `test_scoring.py::test_survival_at_threshold` asserts 34/35/36
> and `test_sub_game.py::test_surviving_the_threshold_wins_inclusively` pins the same horizon
> in the live loop. `U-022` is closed and `C-017` marked `RESOLVED`.
>
> The companion Cop repository records the identical reading, from the same two tables, as
> `C-024`, and pins it with its own boundary test. Both sides of a match therefore score the
> final turn the same way — which is the property that actually matters here, since a
> disagreement about it would produce two logs that each look correct and report different
> winners.

### 1.3 The belief map

The belief is the posterior over the opponent's position given everything observed
(p.48/123):

$$b(s) = P(\text{opponent} = s \mid \text{hints})$$

updated by Bayes from observation only:

$$b_{t+1}(s) \;=\; \frac{P(o_{t+1} \mid s)\; \sum_{s'} P(s \mid s')\, b_t(s')}{\sum_{u} P(o_{t+1} \mid u) \sum_{s'} P(u \mid s')\, b_t(s')}$$

**Observation only** is a design commitment, not an implementation detail. Rule 2 forbids
sharing memory or variables between parties, sanction *immediate disqualification for data
leakage*. A belief updated from anything the opponent did not actually emit would be that
breach, so the update takes an observation and the prior and nothing else.
`test_belief_and_scent_privacy.py` asserts the belief never crosses the wire.

### 1.4 Rate limiting

The gatekeeper is a token bucket (Appendix F table 19):

$$\text{tokens} \leftarrow \min\left(C,\; \text{tokens} + r \cdot \Delta t\right), \qquad \text{allow} \iff \text{tokens} \geq 1$$

with capacity $C$ and refill rate $r$ per second. This permits a burst up to $C$ and then a
steady $r$, which is what sits usefully in front of a provider that answers `429`.

## 2. Architectural decisions and their cost — `M9-011a`

Every decision below cost something. The trade-off is stated, not just the choice.

### 2.1 The language model never chooses a move

Movement is pure Python and deterministic; the model is confined to the verbal layer, and
the shipped provider emits templates at zero tokens.

**Gained:** two agents given the same state produce the same move, so a match is reproducible
from its log — which is what makes rule 20's replay verification meaningful at all. The suite
needs no API key and cannot fail because a provider was slow.
**Cost:** we forfeit whatever a model might have contributed tactically, and we cannot claim
an LLM-driven strategy. The book permits either (chapter 6); we chose the one whose behaviour
an auditor can re-derive.

### 2.2 A myopic policy, $\gamma$ left unused — and where lexicographic ranking failed

The baseline ranks candidate actions **lexicographically**. The argument was that a strict
criterion order is auditable, that no calibration data justified weights, and that tuned
coefficients nobody can defend are worse than an ordering anybody can read.

**That argument was right about weights and wrong about ordering, and §3.1 is what it cost.**
Lexicographic ranking does not merely prefer the first criterion; it makes every later one a
tie-break. Evasion ranked threat distance first, so room to move could not influence a choice
between a far corner and a near open cell — and the far corner wins every time until it is
the last cell you have. Measured in league points, the result was worse than a random walk.

The evasion policy now **sums** distance and mobility. That is not a retreat into tuned
coefficients: the weights are 1 and 1, there is nothing to fit, and the change is a claim
about the objective rather than about calibration — a sub-game pays for reaching the horizon,
not for postponing capture, so the two terms belong on the same footing.

**Gained:** an ordering is still auditable where the criteria genuinely rank (the baseline),
and the objective is now the one the scoring table pays for.
**Cost:** still no lookahead. $\gamma$ appears in the formalism and does nothing in the code,
and we say so rather than inventing a discount to look complete.

### 2.3 Artifact validation is a table, not a JSON Schema

**Gained:** requiredness traces to the book, and every required field cites a rule or page.
**Cost:** we cannot hand an opponent a schema file. `U-019` records that the four example
artifacts prove only that the listed keys occur — a schema generated from them would demand
keys no source demands and then refuse a conformant opponent, failing rule 36's mutual audit
over a difference nothing forbids. The companion repository chose schemas; both are pinned
as correct for their own side rather than reconciled.

### 2.4 Refusal over accommodation, at every boundary

A full inbox refuses rather than growing. A log with no `ended_at` refuses to build. A report
cannot be composed without a passed audit. A dirty working tree refuses a counted game.

**Gained:** each refusal names the rule and its sanction, so an operator reading `[AE-38]`
learns that a false game count disqualifies the project.
**Cost:** more failure modes reach the operator, and each one is an interruption. The
alternative is a system that keeps going while producing evidence it cannot defend, and every
sanction in Appendix E falls on the evidence rather than on the crash.

### 2.5 Reporting imports no transport

Proved structurally, from the AST rather than by behaviour.

**Gained:** a game abandoned because the opponent vanished still writes its four artifacts —
and that is the game whose evidence gets disputed.
**Cost:** the send path is assembled by the caller rather than encapsulated, so there is one
more wiring step to get wrong. `test_report_precondition.py` exists because that step *was*
got wrong: the composer accepted a bare result mapping until `M7-005f`.

### 2.6 A silent opponent is recorded as silent — `M7-22f`

The pre-game declaration carries each group's hardware and language model inside that
group's own entry. Rule 24's sanction is denial of eligibility for the **computational
bonus**, which chapter 5 introduces by asking whether it is fair for an agent on a mobile
device to race one running heavy models — a comparison between two machines, which one
machine's spec cannot express.

The case that mattered was an opponent who declared neither. Until 2026-08-07 a `null` spec
raised `TypeError` here, so a caller facing a silent peer had two options: drop the group
from the declaration, or invent a spec for them. **Refusing `null` is what manufactures the
pressure to fabricate**, and the reference implementation shows where that leads — it
resolves the opponent as `opp = series.peer_identity or own`, an empty peer identity is
falsy in Python, and it copies its own hardware and model into the opponent's slot. Its
sample artifacts show two groups sharing one machine, which reads as a match played on one
laptop rather than as a defect.

`null` is now accepted, and an `undeclared` array must name exactly what was withheld.

**Gained:** the artifact never states a fact nobody supplied. Rule 38 makes a false
declaration an absolute disqualification, and "they were probably running something like
this" is a false declaration. The omission also stays attributable, so rule 24's sanction
lands on whoever failed to declare.
**Cost:** the declaration can be incomplete through no fault of ours, and a grader sees a
gap. The gap is the true state of the exchange; the alternative is a tidy document that is
wrong.

A present-but-partial spec is still refused. Tolerating an omission is not tolerating a
malformed one — a spec that was sent and is half-filled is a different fact from one that
was never sent, and only the second is the peer's silence.

## 3. Empirical results — `M9-011b`

Measurements, not claims. Protocol, sample sizes and threats to validity are in
`docs/RESEARCH-REPORT-Performance-Analysis.md`; this is what the numbers say.

### 3.1 The result that stopped not flattering us

Across **24 scenarios** — every perimeter opening, Cop and Thief starting on opposite cells:

| Metric | Blind baseline | Belief policy | Winner |
| --- | ---: | ---: | --- |
| Total survival steps | 437 | **810** | belief (1.85×) |
| Scenarios reaching the horizon | 11 | **23** | belief |
| **League points** (10 survive / 5 captured) | 175 | **235** | **belief** |
| Paired, per scenario | — | **13 wins, 0 losses, 11 ties** | belief |

**This table read the other way until 2026-08-07, and that is the more interesting result.**
The policy then scored **140 against blind's 175** — worse than a random walk at the only
thing a sub-game pays for — while winning comfortably on survival steps (661 v 437). Both
numbers were true. Appendix F pays for *reaching the threshold* or *being captured* with
nothing in between, so 40 extra steps ending in capture are worth exactly what 1 extra step
ending in capture is worth.

The cause was one line of ranking. `choose_evasive_action` delegated to a policy whose
criteria are **lexicographic with threat distance first**, so room to move only ever
separated equally-distant moves. Maximising distance on a bounded board against a pursuer
walks into a corner: distance large, exits zero. The fix scores distance **plus** mobility
instead of ordering by distance then mobility, which is a different objective —
P(reach the horizon) rather than E[steps].

Re-checked on board sizes 5–9, on randomised openings rather than the tuned set, on barrier
layouts, and on horizons 15–50. The advantage holds throughout and **grows with the
horizon**, which is the tell: the old policy had a ceiling near 28 steps that is invisible
whenever the threshold sits below it. At the negotiated 35 it is decisive.

What this cost is worth stating plainly. `M6-015` accepted the policy on four hand-picked
openings using total steps, and that criterion kept passing for as long as the policy was
losing. The criterion is now league points over the full opening set (`M6-015c`), and
`metric_disagreement` in `results/strategy_arms.json` — a flag that exists to catch exactly
this — now reads `false`.

**The opponent model is part of the result.** All of the above is measured against a Cop
that minimises distance to our *current* cell — the weakest plausible pursuit. Against a Cop
that instead chases the centroid of our next legal cells, escapes fall from 23/24 to **8/24**
(160 points). Belief still beats the blind arm against every pursuer tested, so the fix is
real; but **23/24 is a greedy-Cop figure, not a league expectation**, and running from where
the Cop *is* is precisely what an anticipating Cop exploits. Improving against anticipation
is open work, not a banked claim.

### 3.2 Parameter sensitivity

A larger board helps both arms. Raising the survival threshold no longer makes belief worse:
that was a symptom of the corner-seeking defect, since a longer game gave a deterministic
pursuer more time to close on a policy that had stopped increasing its options. The sweeps
were regenerated after the fix.

### 3.3 Decision cost

Mean **0.56 ms**, worst case **2.01 ms** on 7×7 over 3 000 iterations; **1.52 ms** and
**3.61 ms** on 20×20 over 1 000 (`results/decision_benchmark.json`). Against the negotiated
30 000 ms response timeout, the worst case is **0.012%** of budget. Computational fairness is
not close to contested, which is worth establishing precisely so it can stop being discussed.

These two figures are the only **machine-dependent** numbers in this report — wall clock on
the laptop that ran them, moving slightly on every re-run. The reproducible claim is the ratio
to the timeout, which stays four orders of magnitude clear.

### 3.5 Token and resource accounting — `M9-034`

Rule 54 requires the tokens a game consumed, reported per game and across the series. Both
figures are emitted: `tokens_total` per sub-game in the log artifact and `tokens_total_series`
in the result, through `reporting/token_ledger.py`.

| Configuration | Tokens per 6-sub-game series | Monetary cost |
| --- | ---: | --- |
| **Shipped default** (template provider) | **0** | **0** |
| Optional local model (`ollama`) | 0 API tokens | electricity only |
| Optional cloud model (`claude_api`) | counted against the agreed estimate | provider-dependent |

**The shipped configuration consumes no tokens at all**, and that is a decision rather than an
omission. Movement is pure Python and deterministic (§2.1), so the language model is confined
to the verbal layer, where the zero-token template provider satisfies the same requirement a
paid model would. Appendix F's `[Estimated Tokens for Series]` of ~200 000 is a budget this
agent simply never approaches.

**Why that is a competitive position and not a corner cut.** The book grades *computational
fairness*: it asks whether an agent on a phone races a workstation fairly, and rewards agents
that reach their result with minimal resources rather than by buying compute. An evasion policy
that scores 24/24 against every committed pursuer archetype while consuming **zero tokens and
under 4 ms per decision** is evidence for exactly that claim — the advantage is in the
algorithm, not in the hardware or the API budget. It also removes an entire failure mode from
match day: no API key, no rate limit, no provider outage, and no dependence on the tunnel host
having working internet beyond the peer connection itself.

**What it costs, stated honestly.** No rhetorical sophistication in the hints, and no claim to
an LLM-driven strategy. A classmate spending 200 000 tokens buys a persuasive verbal layer we
have chosen not to buy; the book confines the model to text and forbids letting it move a
piece, so what they can buy with it is bounded (§2.1, rule 25).

### 3.4 Learning curves

Required only "if RL was used" (p.81/189). This policy is deterministic and weight-free, so
there is no convergence to plot and the book names no substitute. The paired comparison in
§3.1 stands in its place: it answers the question a learning curve answers, and here it
answers it uncomfortably.

## 4. References — `M9-011d`, `M9-007c`

Numbered per the guidelines' own bibliography format (`inst/:1082`).

1. Y. Segal, *Distributed Cop-and-Thief Race over a Peer-to-Peer Network — Final Project v3.0.0*, University of Haifa, 2026. — the binding source for every rule, appendix and parameter cited above.
2. Y. Segal, *Software Submission Guidelines v3*, University of Haifa, 2026. — §2.2 documentation structure, §13.1 ISO/IEC 25010, and the reference format used here.
3. ISO/IEC 25010:2011, *Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models*, ISO, 2011.
4. F. A. Oliehoek and C. Amato, *A Concise Introduction to Decentralized POMDPs*, Springer, 2016. — the Dec-POMDP formalism of §1.1.
5. M. Naor, *Bit commitment using pseudorandomness*, Journal of Cryptology 4(2), 1991. — the commitment scheme underlying commit-reveal.
6. NIST, *FIPS PUB 180-4: Secure Hash Standard (SHS)*, 2015. — SHA-256, on whose collision resistance rule 19's audit depends.
7. M. Dorigo, M. Birattari and T. Stützle, *Ant Colony Optimization*, IEEE Computational Intelligence Magazine 1(4), 2006. — stigmergy and the emission/decay model of §1.2.
8. J. Nielsen, *10 usability heuristics for user interface design*, https://www.nngroup.com/articles/ten-usability-heuristics/, 1994. — reference [13]/[14] of the guidelines list.
9. Anthropic, *API key best practices: keeping your keys safe and secure*, https://support.claude.com/en/articles/9767949-api-key-best-practices, 2024. — guidelines reference [10]; the practice behind the secret gates.
10. Model Context Protocol, *Specification*, https://modelcontextprotocol.io/, 2025. — the transport the book mandates.

Course material in `inst/` is quoted under fair academic use and cited by page throughout.
