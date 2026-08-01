# ADR-0009 — Launching a peer: threading, bind address, and readiness

*Status:* accepted 2026-08-02 · *Supersedes:* nothing · *Relates to:* `M5-019e`, `M5-005c`

## Context

`M5-019` closed the play loop: the mailbox is now driven, and a sub-game plays with
nothing fed in by hand. What is still missing is the process that hosts it. There is
no way to *launch* a Thief peer — `python -m p2p_thief_agent` is a scaffold that prints
help.

Three constraints shape the design, and two of them are easy to get wrong in ways
that only fail at the two-machine rehearsal.

## Decision

### 1. The server runs on a daemon background thread; the game loop owns the main thread

`build_server(...).run(...)` blocks forever. The reference solves this by threading the
server and keeping the runtime in the main thread — confirmed 2026-08-02, verbatim:

```python
thread = threading.Thread(
    target=lambda: server.run(transport="http", host=host, port=port,
                              show_banner=False, log_level="warning"),
    daemon=True, name=f"mcp-{role}")
```

`daemon=True` matters: the mailbox must never keep the process alive after the game
ends. The game loop decides when the process exits, and a lingering server thread
would turn a finished match into a hang — the exact failure the watchdog exists to
catch, reintroduced at the process level.

A port-free pre-check runs **before** the thread starts, so a stale peer still holding
the port fails loudly at launch rather than producing a server that silently never
binds while the game loop waits for messages that cannot arrive.

### 2. Bind `0.0.0.0`, never `127.0.0.1`

This is the decision most likely to be got wrong, because the obvious source is wrong
for our purpose. Three independent confirmations:

| Source | Says |
|---|---|
| Book, `police_thief_p2p_Summary.md:657` | `mcp.run(transport="http", host="0.0.0.0", port=8000)` — comment: "Bind the server so a tunnel can expose it publicly" |
| Book rule 10, `…Summary.md:3326` | "Use tunnels to expose the local server to the public internet. **Sanction: Inability to compete against opponents**" |
| `DEV-SPEC.md:382` | same call, "so a tunnel can expose it" |

The **reference binds `127.0.0.1`** (thief 8801, police 8802) because it runs both
peers on one machine. That is single-machine convenience, not the requirement, and the
source hierarchy puts the book above the simulator. Copying the reference here would
produce a peer that passes every local test and is invisible through the tunnel — a
failure that surfaces only at the stage-5 rehearsal and reads as a network fault.
`…Summary.md:673` is explicit that localhost is "permitted only during the early
development stages".

The bind host is therefore a parameter with `0.0.0.0` as the default, so tests can
still bind loopback without the production path depending on a test's choice.

### 3. Readiness is a bounded retry, because start order must not matter

Two peers launched by two people cannot be started simultaneously. The reference makes
this explicit — "start order doesn't matter" — and retries until the opponent is
reachable, governed by two private keys confirmed 2026-08-02:

- `connect_timeout_seconds` (60) — bounds the **whole** wait, then gives up
- `retry_interval_seconds` (1.0) — the gap between attempts

This is deliberately *not* the same mechanism as `services/deadlines.py` (per-request
expiry) or `services/watchdog.py` (whole-system silence). Startup is the one phase
where an unreachable peer is **expected and harmless** rather than a fault: before the
game exists there is nothing to forfeit, so waiting is correct here and wrong
everywhere else. Keeping it a separate module stops that leniency leaking into the
match, where rule 6 requires the opposite.

It is still **bounded**: a peer that waits forever for an opponent who never starts is
a hang, and gives the operator no signal.

## Consequences

- `services/readiness.py` is transport-neutral and takes an injected probe, clock and
  sleep, so start-order tolerance is proven by advancing a number, not by sleeping.
- `adapters/serving.py` is the only new module that touches `fastmcp`, keeping the
  guard test's "only `adapters/` imports fastmcp" invariant true.
- The CLI holds **no** logic: guidelines §4.1 — "There is no business logic in the GUI
  or CLI layers — these layers delegate to the SDK" — and the reference agrees, its
  `_run_peer_inner` doing nothing but `SimulationSdk(...).run_peer(role)`.

## Not decided here

The negotiation-to-first-move orchestration (send offer → poll for the counter-signature
→ verify both directions → begin play). The book requires the Step-0 attestation to be
**exchanged and mutually signed**, and the pre-game declaration to be written *after
negotiation but before play*; the reference confirms the runtime waits for the
counter-signature before step 1. That is a separate sub-task (`M5-019f`) and is not
stubbed here, because a `serve` that comes up and waits without playing is the passive
mailbox rejected on 2026-08-01.
