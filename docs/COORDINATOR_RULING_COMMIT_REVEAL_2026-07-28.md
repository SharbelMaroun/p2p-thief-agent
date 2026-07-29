# Coordinator Ruling — Commit-Reveal Construction and Turn Flow

Ruling date: 2026-07-28

## Context

The M1 wire conformance profile (`WIRE_CONFORMANCE_PROFILE.md`) was first authored
against the Option B (simulator, source-of-truth authority 7) commit-reveal
construction and turn flow. Direct reading of the project book (authority 1),
Chapter 5.3 and its Figure-6 sequence diagram (printed pp.36–37 / PDF pp.52–53),
showed the book **directly specifies** the construction as literal code, contradicting
Option B on the most interoperability-critical details. Because league play is against
classmates who implement from the book — not the simulator — and an `AE-017` commitment
mismatch is a technical loss worth zero, the choice was brought to the coordinator.

## Ruling

The coordinator ruled on 2026-07-28:

1. **Commit-reveal construction: BOOK construction.** The nonce is a field **inside** the
   hashed JSON payload; there is **no delimiter**; serialization is the book's
   `json.dumps(payload, sort_keys=True, separators=(",", ":"))` with default
   `ensure_ascii=True` (non-ASCII escaped as `\uXXXX`), UTF-8 encoded, then SHA-256.
2. **Turn flow: BOOK four-step flow**, with the server tool named **`receive_move`**.
   The four steps are Commit (`H_commit` only) → Acknowledge (locked) → live Reveal
   (Move + Hint, nonce still hidden) → Final Reveal (all nonces at end of game).

This reverses the Option B choice on exactly these two points. All other Option B wire
choices that the book leaves genuinely open remain in force until separately revisited.

## Exact book construction (Chapter 5.3, printed p.37)

```python
nonce = secrets.token_hex(16)
payload = json.dumps(
    {"state": state, "move": move, "intent": intent, "nonce": nonce},
    sort_keys=True, separators=(",", ":"),
)
h_commit = hashlib.sha256(payload.encode("utf-8")).hexdigest()
```

Verified byte-level facts:

- Nonce is inside the payload object; no `"|"` (or any) delimiter is used.
- `json.dumps` is called **without** `ensure_ascii=False`, so non-ASCII text is escaped
  as `\uXXXX`. This differs from the RFC 8785 JCS canonicalizer (raw UTF-8) used for the
  separate config-hash domains, which is unaffected by this ruling.
- `nonce = secrets.token_hex(16)` → 16 bytes → 32 lowercase hex characters.
- The book comment states the sealed record is richer (`hint, verdict, step, role,
  sub_game`) and that "the core is shown". A richer payload is therefore book-sanctioned;
  the **exact cross-classmate field set and field names remain a coordination `UNKNOWN`**
  (`U-005`) and must not be presented as fully book-confirmed.

## Scope and residual unknowns

- BOOK-CONFIRMED by this ruling: nonce-inside-payload, no delimiter, sorted/compact
  `ensure_ascii=True` serialization, UTF-8, SHA-256; the four-step flow; the tool name
  `receive_move`.
- Still `UNKNOWN` (not resolved here): the exact committed field set and names, whether
  a `domain` separator field is interoperable, and cross-language number edge cases
  beyond integers. These stay labelled `UNKNOWN` in the profile until an authenticated
  lecturer answer or accepted cross-team vector settles them.

Nonce length is a local choice and is not interoperability-critical: each peer generates
its own nonce and the verifier recomputes from the revealed payload, which carries that
nonce. The implementation adopts the book's 16-byte / 32-hex nonce for faithfulness.

## Implementation

Applied to `commitment.py`, the turn/session protocol, the neutral Node stub, their
tests, and `WIRE_CONFORMANCE_PROFILE.md` in focused follow-up commits. The
shared-contract checker stays fail-closed at `PENDING` throughout.
