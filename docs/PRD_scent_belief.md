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

## Future acceptance criteria and tests

- Center, decay, and neighborhood remain fixed at the official values.
- Multiplicative decay and nonnegative clipping match the book formula.
- Thief state never reads Cop-private position or memory.
- Observation ordering follows the accepted shared contract.
- Normal, boundary, repeated-emission, clipping, and invalid-shape paths are tested.
- Belief policy is a Thief-local design behind the SDK, not a transport concern.

No scent or belief implementation is included in M1.
