# PRD — Cop-Scent Observation and Thief Belief

Status: official values/formula confirmed; observation contract and belief design pending.

The Thief consumes only public Cop-scent observations and maintains only its local
belief about the Cop (`SR-004`, `THIEF-001`). Fixed values are center `0.9`, decay
`0.10`, and a `5×5` neighborhood (`AF-016`).

Official book Chapter 4.3, PDF p.43 / printed p.27, defines multiplicative decay:
`τ(t+1) = max(0, (1-ρ) × τ(t) + Δτ)`. The pinned simulator instead performs
subtractive/immediate decay in its example path; that behavior must not be copied
(`C-009`, ADR-0005).

Exact public field shape, emission-versus-decay ordering, turn synchronization,
normalization, belief update, and MCP representation remain open. The template-only
`pheromone_min_center_intensity` field has no Appendix F value and is not promoted into
game behavior.

## Future acceptance criteria and tests

- Center, decay, and neighborhood remain fixed at the official values.
- Multiplicative decay and nonnegative clipping match the book formula.
- Thief state never reads Cop-private position or memory.
- Observation ordering follows the accepted shared contract.
- Normal, boundary, repeated-emission, clipping, and invalid-shape paths are tested.
- Belief policy is a Thief-local design behind the SDK, not a transport concern.

No scent or belief implementation is included in M1.
