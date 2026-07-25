# PRD — Live GUI

Status: confirmed future deliverable; no M1 implementation.

## Confirmed boundary

Appendix E rules 8–9 (`AE-008`) require a live UI that displays local truth only and
never exposes the complete objective board or the opponent's private state. `PS-007`
requires the UI to delegate through the SDK.

## Future acceptance criteria

- The Thief view shows only Thief-local state, received public data, and the
  Thief-maintained belief about the Cop.
- No UI adapter imports Cop runtime code or reads Cop storage.
- Every displayed field has a documented local/public provenance.
- The UI contains no game, strategy, protocol, or verification business logic.
- A truth-boundary test fails if objective opponent state reaches the view model.

Framework, layout, accessibility implementation, refresh timing, and screenshots are
team decisions for a later gate. ADR-0009 records the truth-model decision.
