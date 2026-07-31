# Architecture Decision Records

These files are decision placeholders, not accepted contracts. `Proposed` means an
evidence-backed policy is awaiting review; `Pending` means source or cross-team work is
still required. No record below authorizes runtime behavior.

Shared-impact records require evidence under
[SOURCE_OF_TRUTH.md](../SOURCE_OF_TRUTH.md) and acceptance by both Cop and Thief peers.

| ADR | Topic | Status |
|---|---|---|
| [ADR-0001](0001-mcp-contract.md) | MCP contract | Pending |
| [ADR-0002](0002-message-envelope-and-idempotency.md) | Message envelope and idempotency | Pending |
| [ADR-0003](0003-schema-version-discrepancy.md) | Schema-version discrepancy | Pending |
| [ADR-0004](0004-shared-json-private-toml.md) | Shared JSON and private TOML | Pending |
| [ADR-0005](0005-scent-model.md) | Scent model | Pending |
| ADR-0006 | Commit-reveal canonicalization | **Superseded 2026-07-29** — record archived; see note |
| [ADR-0007](0007-llm-movement-policy.md) | LLM movement policy | Proposed |
| [ADR-0008](0008-simulator-reuse-and-license.md) | Simulator reuse and license | Pending |
| [ADR-0009](0009-gui-truth-model.md) | GUI truth model | Proposed |
| [ADR-0010](0010-gmail-reporting.md) | Gmail reporting | Proposed |

## ADR-0006 — superseded, and what replaced it

ADR-0006 recorded a 2026-07-28 coordinator ruling that the commit-reveal construction
follow the **book**: nonce *inside* the sorted-compact payload, no delimiter,
`ensure_ascii=True`, and a `receive_move` tool. On 2026-07-29 the protocol layer was
replaced wholesale by the simulator-conformant wire (commit
`11d0c7a`, "replace Option-B profile with simulator wire; archive old layer"), which
adopts the opposite construction:

```text
commit = SHA256(canonical_json(payload) + "|" + nonce)   # nonce OUTSIDE, "|" delimiter
canonical_json = json.dumps(sort_keys=True, ensure_ascii=False, separators=(",", ":"))
```

That is what `src/p2p_thief_agent/protocol/crypto.py` ships today, and the active,
authoritative record for it is
[SIM_WIRE_PROTOCOL.md](../SIM_WIRE_PROTOCOL.md) (status `ACTIVE`, adopted 2026-07-29),
not this ADR. The superseded text is kept verbatim at
`archive/pre-sim-realign/0006-commit-reveal-canonicalization.md` together with the
ruling it cited.

The index entry above is **not** a live "Accepted" decision, and reading the archived
file as current guidance would produce commitments that fail every audit against the
shipped code. Appendix E rule 19 makes an audit mismatch an automatic zero, so this
distinction is load-bearing. Whether to re-issue a current ADR-0006 restating the
shipped construction is a coordinator decision that has not been taken.
