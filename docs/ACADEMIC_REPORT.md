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

### 2.2 A myopic policy, and $\gamma$ left unused

The policy ranks candidate actions **lexicographically** rather than by a weighted score.

**Gained:** a strict criterion order is auditable — a reader can say why a move was chosen.
**Cost:** no lookahead. $\gamma$ appears in the formalism and does nothing in the code, and
we say so rather than inventing a discount to look complete. No calibration data exists that
would justify weights, and tuned coefficients nobody can defend are worse than an ordering
anybody can read.

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

## 3. Empirical results — `M9-011b`

Measurements, not claims. Protocol, sample sizes and threats to validity are in
`docs/RESEARCH-REPORT-Performance-Analysis.md`; this is what the numbers say.

### 3.1 The result that does not flatter us

Across **24 scenarios** — every perimeter opening, Cop and Thief starting on opposite cells:

| Metric | Blind baseline | Belief policy | Winner |
| --- | ---: | ---: | --- |
| Total survival steps | 437 | **661** | belief (1.51×) |
| Scenarios reaching the horizon | **11** | 4 | blind |
| **League points** (10 survive / 5 captured) | **175** | 140 | **blind** |

The belief policy survives **51% longer** and scores **20% fewer points**. Both are true. The
metrics disagree because Appendix F pays for *reaching the threshold* or *being captured*,
with nothing in between — so 40 extra steps that end in capture are worth exactly as much as
1 extra step that ends in capture.

We report the league column as the one that counts, because it is the one the league counts.
`M6-015c` is open against this: our own evasion metric measures the quantity that reverses
the ranking. It is not patched, because patching a metric after seeing which arm it favours
is how a result stops meaning anything.

### 3.2 Parameter sensitivity

A larger board helps both arms and helps the blind baseline at least as much — more room does
not rescue the disagreement. Raising the survival threshold makes belief **worse**, not
better: a longer game gives a deterministic pursuer more time to close, and a
consistent-but-not-escaping policy converts fewer scenarios into points the further out the
threshold moves.

### 3.3 Decision cost

Mean **0.86 ms**, worst case **2.11 ms** on 7×7 over 3 000 iterations; **1.53 ms** and
**3.47 ms** on 20×20 over 1 000 (`results/decision_benchmark.json`). Against the negotiated
30 000 ms response timeout, the worst case is **0.012%** of budget. Computational fairness is
not close to contested, which is worth establishing precisely so it can stop being discussed.

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
