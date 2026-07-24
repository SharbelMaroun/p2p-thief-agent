# PRD — Scent Trails & Belief Map (Perception)

- **Version:** 1.01 · **Status:** DRAFT · *(v1.01 — compliance audit: scent-model pre-game crypto-lock made explicit, rule 23)*
- **Modules:** `domain/smell.py`, `domain/belief.py` · **Phase 4** · **Tasks:** T229-267 · **Requirements:** FR-5, FR-6, FR-7

## 1. Purpose
Give each agent a way to *locate a hidden opponent* it never sees directly, by reading the opponent's involuntary **scent trail** and fusing it with (possibly lying) verbal hints into a probabilistic **belief map**.

## 2. Theoretical background
- **Stigmergy:** indirect coordination through the environment (ant pheromones). The board becomes a shared blackboard; scent is emitted by movement and cannot be faked (an agent can't plant scent where it hasn't been).
- **Diffusion + decay:** intensity spreads spatially and fades over time, giving a "memory" long enough to be tactical but not eternal.
- **Bayesian belief:** a probability distribution over the opponent's cell, updated multiplicatively by evidence (scent) and diffused by the opponent's motion model.

## 3. Functional requirements
### 3.1 Scent (`smell.py`)
- **SC-1** On each move/stay, emit a **5×5** radial field; **center intensity 0.9** (Fixed).
- **SC-2** Radial falloff from the center (nearer cells stronger).
- **SC-3** **Multiplicative decay per full turn:** `τ(t+1) = max(0, (1−ρ)·τ(t) + Δτ)`, **ρ = 0.10** (Fixed). *(This corrects the reference engine's subtractive decay; the book wins — ADR-5.)*
- **SC-4** Merge trails with **max**; clamp to `[0, 0.9]`.
- **SC-5** Transmit only the intensity field `{'r,c': τ}` — **never an explicit position**.
- **SC-6** Enforce a configured minimum center intensity on deposit.

### 3.2 Belief (`belief.py`)
- **BF-1** Probability grid over the NxN board, uniform prior.
- **BF-2** `observe_smell`: scale each cell by `(1 + trust·intensity)`, then normalize (Bayesian-style).
- **BF-3** `diffuse`: spread mass to the neighborhood matching the opponent's move set (von Neumann for orthogonal).
- **BF-4** `exclude(cell)`: zero out cells ruled out (e.g. "I stand here, no capture happened").
- **BF-5** `most_likely()`: argmax cell = the strategy's target.
- **BF-6** Hint fusion: lower the trust factor when a verbal hint contradicts the scent field.

## 4. Interface (I/O)
```python
SmellField(board_size, grid_size=5, decay=0.10, min_center=0.5)
  .deposit(center, intensity); .absorb(cells); .decay_all(); .snapshot() -> {'r,c': float}
BeliefGrid(board_size, smell_trust=4.0, orthogonal=True)
  .observe_smell(cells); .diffuse(); .exclude(cell); .most_likely() -> Cell; .as_matrix()
```

## 5. Performance metrics
- Belief update + diffuse per turn: < 5 ms on 7×7. · Belief accuracy (top-1 cell vs. true) rises monotonically as scent accumulates. · Contradiction ("north" vs. SE scent) detected with high confidence.

## 6. Constraints & limitations
- Scent is symmetric and unfakeable — you cannot deceive via scent, only via words. · Belief is only as good as the motion model in `diffuse`. · `smell_trust_weight` is a private tuning knob (not signed). · The scent **model itself** (emission + decay formula and its parameters) is **crypto-locked pre-game** via the `pheromones` section of the signed `game.json` (rule 23) — deviating from the agreed formula cancels the game.

## 7. Alternatives considered
| Option | Verdict |
|---|---|
| Kalman/particle filter | Overkill for a 49-cell discrete board. |
| Last-seen-cell heuristic only | Too brittle; loses the opponent instantly. |
| Strict Bayes with explicit likelihood | Cleaner theory; the `×(1+trust·τ)` form is simpler and adequate (documented as "Bayesian-style"). |
| **Radial scent + multiplicative-decay belief grid** | **Selected** — book-faithful, cheap, transparent. |

## 8. Success criteria
- Belief peak lands on/near the true opponent cell within a few turns of receiving scent.
- Decay curve matches the book's worked example (0.9 → 0.81 after one turn at ρ=0.10).
- A lying hint that contradicts scent lowers trust and does not move the belief peak away from the true region.

## 9. Test scenarios (→ T241-244, T256-260, T267)
- 5×5 emission values match spec. · Decay over N turns matches `(1−ρ)^n`. · `observe_smell` peaks at the scented cell. · `diffuse` conserves total mass. · `exclude` renormalizes. · Contradiction case lowers trust coefficient.
