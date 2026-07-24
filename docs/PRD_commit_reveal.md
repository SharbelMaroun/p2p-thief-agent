# PRD — Commit-Reveal Cryptographic Integrity

- **Version:** 1.00 · **Status:** DRAFT
- **Module:** `domain/crypto.py`, `peer/sealing.py` · **Phase 6** · **Tasks:** T343-378 · **Requirements:** FR-8, FR-9, FR-10

## 1. Purpose
Guarantee that, in a P2P game with **no referee**, no agent can alter a move after the fact, change a move after seeing the opponent's, or deny past declarations. Trust is replaced by mathematics.

## 2. Theoretical background
- **Commit-Reveal** (Blum's "coin-flip over the phone"): commit to a hidden value first, reveal later; the commitment binds you before you learn the opponent's choice.
- **Cryptographic hash (SHA-256):** pre-image + collision resistance make it infeasible to find a different payload with the same digest → any change is detected.
- **Nonce** (number-used-once): a fresh random value per commit; defeats **dictionary attacks** over the small move space and makes identical moves hash differently.
- **Zero-knowledge spirit:** at commit time the opponent gains certainty a decision is locked but zero knowledge of its content.

## 3. Functional requirements
The protocol is a strict 4-step sequence per turn (rulebook Fig. 6): **Commit → Acknowledge → Reveal → Final-Reveal/Audit**.

- **CR-1** Seal every step: `commit = SHA256(canonical_json(payload) | nonce)`.
- **CR-2** `payload` = `{step, state, move, intent, hint, position, …}`; `intent`/`verdict` marks the hint truthful or bluff.
- **CR-3** Send only the commit during play; withhold the nonce.
- **CR-4** **Acknowledge:** the opponent confirms receipt and lock of the commit; the acknowledgment prevents retraction and ensures reveals happen only after both sides have determined their moves. No reveal before ack.
- **CR-5** Reveal move + hint at the reveal step; **reveal all nonces only at end-of-game**.
- **CR-6** Mutual audit: each side re-hashes the opponent's revealed log and compares to the original commits.
- **CR-7** Any mismatch → `tamper_forfeit` (score 0, no appeal).
- **CR-8** Step-0 pre-game declaration: signed hardware spec + code commit hash + token budget.

## 4. Interface (I/O contract)
```python
CommitReveal.commit_of(payload: dict, nonce: str) -> str          # hex digest
CommitReveal.seal(payload: dict) -> {"nonce": str, "commit": str} # secrets.token_hex(16)
CommitReveal.verify(payload, nonce, commit) -> None               # raises CryptoError on mismatch
audit_records(records: list[{payload,nonce,commit}]) -> {passed, verified_steps, failed_steps}
```
- **Canonicalization:** `json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False)` — mandatory so both machines hash byte-identical input.
- **Comparison:** `secrets.compare_digest` (constant-time).

## 5. Performance metrics
- Seal + verify per step: < 1 ms. Full 35-step mutual audit: < 100 ms.
- 0 false positives (honest game never forfeits); 100% detection of any single-bit change.

## 6. Constraints & limitations
- Nonce must come from `secrets`, never `random`. · Payload key order/whitespace must be canonical or interop breaks.
- The scheme proves **log integrity**, not that a move was *strategically* legal — legality is enforced separately by `rules.py`.

## 7. Alternatives considered
| Option | Verdict |
|---|---|
| Trust + honor system | Rejected — no referee; cheating undetectable. |
| Digital signatures (asymmetric keys) | Overkill; key distribution burden; hash commit suffices for this game. |
| Merkle tree over all steps | Nice-to-have for O(log n) proofs; unnecessary at 35 steps. |
| **SHA-256 commit-reveal + nonce** | **Selected** — simple, interoperable, book-mandated. |

## 8. Success criteria
- Honest full game: audit `passed = True`, all steps verified.
- Tampered log (any field changed): audit fails at that step → forfeit.
- Two independent machines produce identical commits for identical payloads (interop).

## 9. Test scenarios (→ T350-353, T367-369, T621-622)
- commit→verify round-trip OK. · Tamper each payload field → verify raises. · Nonce uniqueness across N seals. · Reordered JSON keys → same commit. · Mutual audit with 1 bad step → `failed_steps=[k]`. · Missing nonce at audit → forfeit. · **Ack ordering:** a reveal arriving before the commit was acknowledged is rejected.
