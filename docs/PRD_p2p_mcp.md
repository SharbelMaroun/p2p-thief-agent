# PRD — Peer-to-Peer FastMCP

Status: structural and reliability boundaries confirmed; the wire contract was
**settled on 2026-07-29** by adopting the simulator wire — see
[SIM_WIRE_PROTOCOL.md](SIM_WIRE_PROTOCOL.md), which is the authoritative record.

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

## Tool surface — settled

The four tools are **`negotiate`**, **`receive_turn`**, **`submit_audit`**, and optional
**`receive_control`**, each taking a single argument (`message`, `message`, `payload`,
`message`) with **no envelope** — the argument *is* the message dict.

> `receive_move` is **not** a tool in this profile. It was the earlier Option-B/book
> name and was withdrawn when the simulator wire was adopted on 2026-07-29. Building a
> server that exposes `receive_move` would leave this peer unreachable by any agent
> written against the reference simulator, which is what classmates build from.

These are interoperability choices matching the reference simulator, not book-mandated
names — the book leaves tool naming open. Ports remain private (`U-006`). Idempotency
keys, ordering, maximum sizes, and recovery messages are M5 runtime design.

## Future acceptance criteria and tests

- Two independently installed processes exchange only accepted public messages.
- Invalid schema, identity, state, order, duplicate ID, and expired deadline fail
  explicitly.
- Silence triggers the accepted watchdog outcome without deadlock.
- Transport handlers delegate all decisions through the SDK.
- Localhost and public-tunnel integration paths pass against the same contract fixtures.

No FastMCP dependency or runtime is added in M1.
