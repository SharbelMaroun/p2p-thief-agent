# ADR-0006: Commit-Reveal Canonicalization

Status: Accepted (coordinator ruling 2026-07-28) for the construction and flow;
exact field set remains `UNKNOWN`.

## Evidence

Official project book v3.0.0 requires SHA-256 commit-reveal, and unauthenticated
generated examples contain observed integrity fields (`JS-003`). Appendix E rule 18
keeps nonces secret until the end-game reveal. Chapter 5.3 (printed p.37 / PDF p.53)
gives the commitment as literal code, and the Figure-6 diagram (printed p.36) gives the
four-step flow. Appendix B separately associates sorted-key canonical JSON with a
consistent `config_sha256` in a **different** hash domain.

## Decision (coordinator ruling 2026-07-28)

The commit-reveal construction follows the **book**, not the earlier Option-B choice:

```python
nonce = secrets.token_hex(16)                      # 16 bytes → 32 lowercase hex
payload = json.dumps(
    {..., "nonce": nonce},                         # nonce INSIDE the payload
    sort_keys=True, separators=(",", ":"),         # default ensure_ascii=True
)
h_commit = hashlib.sha256(payload.encode("utf-8")).hexdigest()
```

- Nonce inside the payload; no delimiter (the earlier Option-B external nonce and `"|"`
  separator are withdrawn).
- Non-ASCII is escaped (`ensure_ascii=True`), which differs from the RFC 8785 JCS
  canonicalizer used for the separate `config_sha256` / source-byte domains. The three
  hash domains stay distinct.
- Turn flow is the book's four steps with the tool named `receive_move`.

See
[COORDINATOR_RULING_COMMIT_REVEAL_2026-07-28.md](../COORDINATOR_RULING_COMMIT_REVEAL_2026-07-28.md).

## Still open

The **exact committed field set and names** (core `state/move/intent/nonce` versus the
book's richer `hint/verdict/step/role/sub_game`, and whether a `domain` separator field
is interoperable) remain `UNKNOWN` (`U-005`) pending an authenticated lecturer answer or
an accepted cross-team vector. Cross-language number edge cases beyond integers are not
exercised by the commit payload, whose numeric fields are all integers.
