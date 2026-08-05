# PRD — Cop-Scent Observation and Thief Belief

Status: official values/formula confirmed; observation contract and belief design pending.

The Thief consumes only public Cop-scent observations and maintains only its local
belief about the Cop (`SR-004`, `THIEF-001`). Fixed values are center `0.9`, decay
`0.10`, and a `5×5` neighborhood (`AF-016`).

Official book Chapter 4.3, PDF p.43 / printed p.27, defines multiplicative decay:
`τ(t+1) = max(0, (1-ρ) × τ(t) + Δτ)`. The pinned simulator instead performs
subtractive/immediate decay in its example path; that behavior must not be copied
(`C-009`, ADR-0005).

Emission-versus-decay ordering, turn synchronization, normalization, belief update, and
MCP representation remain open. The template-only `pheromone_min_center_intensity` field
has no Appendix F value and is not promoted into game behavior.

## Confirmed emission shape (`M6-001`, built 2026-08-02)

Book Figure 4 (p.44) fixes the radial profile of the new emission Δτ by distance class:

| Distance class | Cells | Δτ |
|---|---|---|
| Centre (agent's cell) | 1 | `0.90` |
| Orthogonal cross | 4 | `0.62` |
| Diagonal | 4 | `0.20` |
| Mid-side edge | 4 | `0.14` |
| Corner | 4 | `0.04` |
| Squared-distance 5 ring | 8 | **`U-025`** — unnamed by the figure; `perception/scent` holds a documented residual `0.04` pending a ruling |

`perception/scent.py` implements this as `emission_field()` plus the per-turn update
`settle`/`advance_field` (`τ(t+1) = max(0, (1-ρ)·τ(t) + Δτ)`, ρ = 0.10), with the p.43
"reduced by 90%" prose corrected to a 90% **retain** under `C-014`. Fifteen of the
seventeen named cells and the eight `U-025` cells are pinned by `test_scent.py`.

## Public scent observation on the wire (`M6-002`, built 2026-08-02)

`perception/observation.py` is the boundary between the `smell_grid` wire field — a
sparse `{"r,c": intensity}` map (`SIM_WIRE_PROTOCOL.md`) — and the `(row, col) → intensity`
map the belief layer reads. `parse_smell_grid` decodes it order-independently and rejects
a malformed key or a non-numeric/negative intensity by name; `encode_smell_grid` produces
the sparse form, omitting silent cells (an unseen cell is absent, not zero, `M6-006a`) and
emitting keys in a deterministic sorted order. Off-board rejection needs the negotiated
grid and is `M6-006b`.

## Thief-local belief (`M6-003`, foundation built 2026-08-02)

`perception/belief.py` holds a probability distribution over the Cop's position — never
the Cop's actual cell (`AE-8`, `AE-9`). `uniform_belief` sizes it to the **negotiated**
grid; `apply_evidence` is the Bayes update `posterior ∝ prior × likelihood` renormalised,
where the likelihood is computed by the caller from a **public** observation (scent or a
hint), so no objective truth can enter — proven by `apply_evidence` having no parameter
for a real cell. `normalize` falls back to max-entropy uniform on a zero total, so a
contradiction never divides by zero (`M6-003c`).

### Hint decoding and the trust factor (`M6-003b`/`M6-003e`/`M6-003f`, design 2026-08-03)

The book delegates strategy and belief design to the team, so the following are recorded
team decisions, not spec values — open to revision, but chosen to honour every binding
rule.

**What an inbound hint is.** The Thief's belief is over the **Cop's** position. We treat an
inbound hint as the opponent's free-text claim about **where it is or which way it is
heading** — a claim that may be truthful or a bluff. It therefore decodes into evidence
about the Cop's cell, and the trust factor plus the Cop's own scent arbitrate its honesty.

**Decoding (`M6-003e`), deterministic and coordinate-free.** `perception/hint.decode_hint`
scans the hint for a small set of natural-language **directional cues** —
north/up/top, south/down/bottom, east/right, west/left, center/middle, corner — and turns
each into a per-cell **gradient** weight (e.g. "north" favours low row indices). The
gradients multiply, and the result is normalised into a likelihood. This is deterministic
pure Python, so it can feed the move without the LLM (`AE-25`), and it uses only common
directional vocabulary, never an agreed `"r,c"` coordinate protocol (`AE-27`). A hint with
no recognised cue — or an empty/absent one — yields a **uniform** likelihood: missing
evidence is not an error (`M6-003c`, `M6-009c`).

**Trust factor (`M6-003b`).** Each opponent carries a running trust `∈ [0, 1]` (neutral
`0.5`). `perception/trust.trust_weighted` blends the hint's likelihood toward uniform by
`(1 − trust)`, so a low-trust hint barely moves the belief and a zero-trust hint is
ignored entirely — the hint is applied through `apply_evidence` at its trust-tempered
strength.

**Trust update (`M6-003f`).** `perception/trust.update_trust` compares the hint's
likelihood against the **scent-derived** belief (where the Cop's own residue actually
points). Agreement above the no-correlation baseline raises trust; a hint that points where
scent shows nothing lowers it — a claimed direction with no scent residue is evidence of a
lie. Trust stays clipped to `[0, 1]`. How fast trust falls and whether it recovers is
`M6-027`.

## Future acceptance criteria and tests

- Center, decay, and neighborhood remain fixed at the official values.
- Multiplicative decay and nonnegative clipping match the book formula.
- Thief state never reads Cop-private position or memory.
- Observation ordering follows the accepted shared contract.
- Normal, boundary, repeated-emission, clipping, and invalid-shape paths are tested.
- Belief policy is a Thief-local design behind the SDK, not a transport concern.

No scent or belief implementation is included in M1.

## Board-level field and involuntary emission (`M6-007`, built 2026-08-03)

`perception/field.py` lays the emission profile onto the whole board. `deposit(field,
board, cell)` decays the field and stamps a fresh 5×5 emission at the agent's cell — it
takes the *cell*, never the *action*, and carries no suppression flag, so a `STAY` re-emits
exactly as a move does and no path can skip or fake the trail (`M6-007a`, `M6-007c`).
`scent_likelihood(observed, board)` is the bridge into belief: it turns the **opponent's**
observed field into a likelihood for `apply_evidence` (empty ⇒ uniform). The Thief's own
`deposit` output is encoded outbound and never fed here — a guard proves the belief modules
never touch the own-emission functions, so own scent can never become evidence (`M6-007b`).

## Reference: belief update rule and the locked scent model (`M6-012`)

### Belief update formulas (`M6-012a`)

Let `b` be the current belief over the `R×C` grid (`Σ b = 1`) and `L` a likelihood from a
public observation. The update is Bayes, renormalised (`perception/belief.apply_evidence`):

```text
posterior[i,j] = b[i,j] · L[i,j] / Σ_{k,l} b[k,l] · L[k,l]
normalize(M)   = M / ΣM,  and if ΣM = 0 then normalize(M) = uniform   (M6-003c)
```

A scent observation becomes `L` by `scent_likelihood` (intensity per cell, normalised). A
hint becomes `L` by `decode_hint`, then tempered by the sender's trust `t ∈ [0,1]` before it
is applied (`perception/trust.trust_weighted`):

```text
L_eff = t · normalize(L_hint) + (1 − t) · uniform          (M6-003b)
```

Trust itself moves by the overlap of the hint with the Cop's own scent, against the overlap
an uninformative hint would score (`perception/trust.update_trust`, `M6-003f`):

```text
agreement = Σ L_hint · b_scent
signal    = clip(agreement / (1/(R·C)) − 1, −1, 1)
t'        = clip(t + rate · signal, 0, 1)
```

The belief holds only a distribution — never the Cop's real cell — and the update takes no
parameter for objective truth (`AE-8`, `AE-9`, proven by `test_belief.py`).

### The locked scent model (`M6-012b`)

`perception/scent_lock.scent_model_record` is the exact object hashed and locked at
negotiation (`AE-23`). Its members are:

```text
model                                = "multiplicative-decay"
update                               = "tau_next = max(0, (1 - decay_per_step) * tau + emission)"
center_intensity                     = 0.9
decay_per_step                       = 0.10
field_size                           = 5
emission_profile_by_squared_distance = {"0":0.90, "1":0.62, "2":0.20, "4":0.14, "5":0.04, "8":0.04}
```

`scent_model_hash = canonical_sha256(record)` — the same canonicalisation as the config and
commitments, so the lock is byte-comparable. `with_scent_lock` stamps it into the signed
terms; a peer running any other formula, constant, or profile (including a different `U-025`
value for the squared-distance-5 ring) produces a different hash and is refused by name
before the first move.

## Offering the scent implementation for parity (`M6-018`)

Book §6 recommends sharing the scent source so both peers run identical logic.
`perception/scent.py` depends on nothing in this project (only `from __future__`), so it is
a self-contained reference unit that can be offered to an opponent verbatim — proven by
`test_scent_shareable.py`. A classmate who adopts it, or reproduces the model in "The locked
scent model" above, produces byte-identical fields; the `M6-005` lock then verifies that
parity at negotiation and refuses a mismatch before the first move. Under `THIEF-002` the
offer is one-directional: this repository publishes its scent logic and its hash and consumes
nothing from the opponent's repository.

## Trust-decay policy for repeated lies (`M6-027`)

Trust moves linearly and symmetrically (`perception/trust.update_trust`). A hint whose
directional claim fully contradicts the Cop's scent scores a signal of `−1` and drops trust
by `rate` (default `0.2`); a fully corroborated hint scores `+1` and raises it by `rate`;
partial agreement moves it proportionally. Both ends are clipped to `[0, 1]`, so about
`1/rate` ≈ **five** consecutive lies drive trust to the floor, and a low-trust hint barely
moves belief (`L_eff = t·L + (1−t)·uniform`). Trust **recovers**: a peer that lied can rebuild
it by telling the truth, at the same rate — one bad hint is not a life sentence. Pinned by
`test_trust_decay.py`.
