# PRD — Thief Strategy

Status: deterministic baseline policy selected for planning; algorithm details pending.

Evasion, legal route selection, survival, Thief-local belief use, and Thief-local verbal
behavior are in scope. Appendix E rule 25 recommends algorithmic movement and LLM use
for text/behavioral-profile generation. It is a recommendation without an automatic
mandatory sanction, not a categorical prohibition (`AE-025`).

The project policy in ADR-0007 is therefore a deterministic movement baseline. Any
future change requires both peers' accepted policy and still cannot bypass legal-action
validation, deadlines, or the SDK. No model/provider is mandatory.

## Future inputs and output

The accepted SDK strategy input will contain only Thief-local state, public
observations, known disclosed barriers, legal actions, history, and configured
deadlines. Output will be one structured candidate action; orchestration validates it
before any protocol use.

## Future acceptance criteria and tests

- The baseline always chooses one of N/S/E/W/STAY from the supplied legal set.
- Same snapshot and configuration produce the same choice.
- Empty/trapped and boundary cases produce the accepted capture/outcome path.
- Known barriers and survival objective affect selection without Cop-private truth.
- No strategy function performs networking, GUI work, or an external/LLM call.
- Normal, tie-break, fallback, trapped, and invalid-input paths are covered.

Weights, look-ahead, belief heuristic, verbal policy, and optional future learning are
team design choices. No strategy implementation is included in M1.
