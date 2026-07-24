# PRD — P2P Networking & FastMCP

- **Version:** 1.01 · **Status:** DRAFT · *(v1.01 — compliance audit: NET-7 explicitly covers the scent-model crypto-lock, rule 23)*
- **Modules:** `infra/mcp_server.py`, `infra/mcp_client.py`, `domain/protocol.py`, `peer/handshake.py` · **Phase 2, 5** · **Tasks:** T131-175, T305-342 · **Requirements:** FR-13, FR-14, FR-15

## 1. Purpose
Let two untrusting agents on different machines play a full game **with no central server**, each acting as both server and client over the Model Context Protocol (FastMCP), reachable across the internet via a tunnel.

## 2. Theoretical background
- **MCP / FastMCP:** open protocol connecting agents to tools; `@mcp.tool` exposes a function callable remotely with a structured schema.
- **Symmetric peer:** every agent is simultaneously a **server** (exposes tools) and a **client** (calls the opponent). No strong/weak side.
- **NAT traversal:** most hosts sit behind NAT/firewalls; a **tunnel** (ngrok/Localtonet) yields a public URL (conceptually STUN-style).
- **Turn token:** a single logical token travels with the turn message — holding it means it is your turn ("green").

## 3. Functional requirements
- **NET-1** Each peer runs its own FastMCP HTTP server on a configured port.
- **NET-2** Expose tools: `receive_turn`, `receive_ack`, `receive_reveal`, `receive_audit`, `receive_negotiation` (the ack may alternatively be the synchronous return value of `receive_turn` — one of the two, documented).
- **NET-3** Client calls the opponent's URL; **retries until up** (start-order agnostic).
- **NET-4** Every request carries a **deadline**; no response in time → retry or technical loss.
- **NET-5** `TurnMessage` schema serializes/deserializes canonically (carries the turn token, commit, reveal, hint, scent field).
- **NET-6** Public exposure via tunnel for league; localhost for dev.
- **NET-7** Pre-game **negotiation/handshake**: exchange + verify SHA-256 over the shared `game.json`; agree `game_id`/`game_uid`; **refuse to play on mismatch**. The signed terms explicitly include the `pheromones` section, so the **scent model is crypto-locked before the game** (rule 23 — deviation from the formula cancels the game); identities exchanged here include **both of the opponent's repo URLs** (needed for the 4-link result JSON, rule 49).
- **NET-8** Cop and Thief run as **separate processes / config dirs**; no shared memory or live-state module.
- **NET-9** **Acknowledge step:** the receiver confirms a commit is locked before any reveal flows (Commit → Ack → Reveal → Final-Reveal).
- **NET-10** The verbal hint channel carries **natural language only** — no direct coordinate-numbering protocols (Appendix E rules 26–27; violation disqualifies). Structured data (commits, scent fields) travels in protocol fields, never in hints.

## 4. Interface (I/O)
```python
# server
@mcp.tool def receive_turn(msg: dict) -> dict
@mcp.tool def receive_reveal(msg: dict) -> dict
@mcp.tool def receive_audit(msg: dict) -> dict
# client / transport
McpTransport(opponent_url, inboxes, connect_timeout, retry_interval, audit_send_timeout)
  .send_turn(msg); .poll_turn(interval) -> dict|None
# handshake
negotiate(runtime); validate_agreement(config); terms_from_config(config)
```

## 5. Performance metrics
- Connection established regardless of which peer starts first. · Turn round-trip within `response_timeout_sec` (30s). · 0 deadlocks over a full series (state machine guarantees a defined end).

## 6. Constraints & limitations
- Requires a working tunnel; a dropped tunnel = deadlock risk → handled by deadline/watchdog. · Only the opponent URL is known — no other opponent internals. · No business logic in `infra/` (transport only).

## 7. Alternatives considered
| Option | Verdict |
|---|---|
| Central game server / matchmaking | Rejected — violates the no-referee mandate. |
| Raw sockets / custom protocol | More work; loses MCP tooling & interop. |
| WebRTC / direct P2P NAT punching | Complex; tunnel is simpler and course-standard. |
| **FastMCP server+client + tunnel** | **Selected** — book-mandated, symmetric, interoperable. |

## 8. Success criteria
- M2: message A→B over localhost received intact. · M5: full game vs a remote peer over a tunnel completes. · Mismatched `game.json` → both peers refuse to play.

## 9. Test scenarios (→ T140, T167-169, T323-324, T337-339, T621-624)
- Serialize/deserialize `TurnMessage` round-trip. · Two-process localhost message exchange. · Start thief-first and police-first (both connect). · Matching terms → agree; mismatched terms → refuse. · Opponent silent past timeout → `timeout` result. · Reveal-before-ack rejected. · Outbound hint containing coordinates blocked by validation.
