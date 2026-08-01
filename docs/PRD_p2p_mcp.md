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

## Transport contract as built (`M5-002`)

Both halves now exist: `adapters.build_server` (inbound mailbox) and
`adapters.FastMCPClient` (outbound connector). They are the only two modules that
import `fastmcp`; a guard test walks `src/` and fails on any other importer.

**Call shapes.** One tool, one argument, no envelope. Keywords come from
`peer.TOOL_ARGUMENTS`, the single place they are written down:

| Tool | Argument |
|---|---|
| `negotiate` | `message` |
| `receive_turn` | `message` |
| `submit_audit` | `payload` |
| `receive_control` | `message` |

**Acknowledgement semantics (`M5-002d`).** The tools **never validate and never
raise**. They enqueue and acknowledge; `drain` validates afterwards through
`InboundPeer`, and a failure there is a recorded game outcome.

This diverges from the reference implementation, which instantiates its protocol
dataclass inside the tool so a malformed message raises and the caller sees an
MCP error. The divergence is deliberate and load-bearing: a **tampered audit is
structurally well-formed** and must be *scored* as a technical loss under
Appendix E rule 19. A peer that raises invites the opponent to retry a decided
loss as a transport fault, and a settled result then evaporates into a timeout.
Being lenient inbound cannot break an opponent — it only ever accepts more than
required — whereas being strict can discard a decided game.

**Fault mapping.** Two disjoint types, neither inheriting the other:

| Condition | Raised | Meaning |
|---|---|---|
| Unreachable, timed out, carrier error | `TransportError` | The exchange failed; retry or declare a technical loss |
| Reply is not a JSON object | `TransportError` | The peer did not speak the wire |
| Reply explicitly refuses | `PeerRejectionError` | Reached and declined — a **game outcome**, never a retry |

**Liberal on the ack shape.** This peer sends `{"ok": true}`, but the profile
never fixed what an opponent must return and the reference's exact dict is not
established — it may be `{"status": "ok"}` or `{"status": "delivered"}`. Any JSON
object is therefore accepted unless it explicitly signals failure via
`ok: false`, a `status` naming a failure, or a non-empty `error`. Demanding our
own shape would read every successful delivery from a simulator-built classmate
as a refusal and abandon a healthy game.

**Built since:** the separate-process round trip closed the book's stage-2
milestone (`M5-002e`); `shared/private_config.py` supplies the opponent URL from
`[network].opponent_url` and is the only door to one, while
`assert_no_network_address` refuses a shared match object that carries an address
(`M5-002f`); and `protocol/agreement.py` decides whether this peer will play at
all — signature, required terms, Appendix F floors, then every term compared
against our own, refusing **by name** — wired into the live `InboundPeer` handler
(`M5-014`).

## A whole sub-game, and how it ends (`M5-007`)

`orchestration/` holds the declared phase machine, `run_turn`, and
`run_sub_game_over_wire`. One turn is **await → compute → apply → seal → send**; a
peer must receive before advancing, which makes the exchange a strict alternation.
**This peer opens** — the book gives the Thief the first move of every cycle, so step
1 does not wait. A Thief that waited would deadlock against a Cop correctly waiting
for it.

Termination is not the Cop's mirror. The Cop can only *claim* a capture, because it
cannot see where the Thief stands; this peer is the one that **knows**. So a
`capture_claim` is checked against local truth, never believed, and an incorrect claim
is simply the game continuing. Confirmed against the reference 2026-08-01, whose
precedence reads capture "when a cop's `capture_claim` is **confirmed by the thief**",
survival at the threshold, then timeout on silence.

Nothing on the wire forces that answer to be honest — the audit does. Every sealed
record carries this peer's true position, so a false denial is contradicted by its own
reveal, and a forgery scores zero for both sides while an honest loss still scores.
The audit is sent **once per sub-game, after the loop**, and goes out even when this
peer is taking the technical loss.

**Reliability, built (`M5-004`).** `services/deadlines.py` bounds every single request
(retry or declare a technical loss, never wait); `services/watchdog.py` is the
system-wide freeze net — on `elapsed > watchdog_timeout_sec` (book §8.4.2) it runs
`persist_state()` then `controlled_shutdown()` once and returns `SHUTDOWN`, with time
injected so a freeze needs no real wait; `services/gatekeeper.py` queues overflow
rather than dropping it. A mid-turn disconnect has no deadlock exit: `turn_loop` and
`sub_game` route silence, a dropped send, and a seal failure to a terminal technical
loss that still reveals its audit.

**Not yet built:** mutual verification of the *opponent's* audit (the reference has
both peers swap logs and each verify the other's commits), idempotency parent close
(`M5-003`), the orchestrator gateway that hosts these subsystems (`M5-001`), the log
manager (`M5-008`), and the tunnel (`M5-005`).

## Future acceptance criteria and tests

- Two independently installed processes exchange only accepted public messages.
- Invalid schema, identity, state, order, duplicate ID, and expired deadline fail
  explicitly.
- Silence triggers the accepted watchdog outcome without deadlock.
- Transport handlers delegate all decisions through the SDK.
- Localhost and public-tunnel integration paths pass against the same contract fixtures.

`fastmcp` was added as a dependency for `M5-002`; it was deliberately absent
through M1–M4 so the transport-free layers could not accidentally depend on it.
