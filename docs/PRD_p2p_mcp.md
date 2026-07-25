# PRD — Peer-to-Peer FastMCP

Status: structural and reliability boundaries confirmed; wire contract pending.

## Confirmed requirements

- Each peer is both FastMCP server and client (`SR-005`) and runs in a separate process
  (`SR-004`).
- One gateway coordinates subsystems (`AE-003`).
- An explicit state machine rejects illegal transitions (`AE-004`).
- Deadlines and a watchdog prevent indefinite waits (`AE-006`).
- Each local server is publicly reachable through a tunnel; no provider is mandated
  (`AE-010`).
- Appendix F defaults are 30-second response and 60-second watchdog timeouts
  (`AF-019`).

## Contract gate

Exact MCP tool names, envelopes, fields, idempotency keys, ordering, acknowledgements,
ports, maximum sizes, and recovery messages remain in `U-003`/`U-006` and ADR-0001/0002.
Simulator names such as `negotiate`, `receive_turn`, `submit_audit`, and
`receive_control` are candidate interoperability choices, not book-mandated names.

## Future acceptance criteria and tests

- Two independently installed processes exchange only accepted public messages.
- Invalid schema, identity, state, order, duplicate ID, and expired deadline fail
  explicitly.
- Silence triggers the accepted watchdog outcome without deadlock.
- Transport handlers delegate all decisions through the SDK.
- Localhost and public-tunnel integration paths pass against the same contract fixtures.

No FastMCP dependency or runtime is added in M1.
