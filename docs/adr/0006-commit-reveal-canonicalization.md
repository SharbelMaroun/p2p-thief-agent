# ADR-0006: Commit-Reveal Canonicalization

Status: Pending

## Evidence

Official project book v3.0.0 requires SHA-256 commit-reveal, and the official artifact
templates confirm integrity fields (`JS-003`). Appendix E rule 18 keeps nonces secret
until the end-game reveal. Exact canonical bytes, committed payload, nonce
encoding/length, and wire sequencing remain unknown (`U-002` and `U-005`).

## Decision needed

Cop and Thief must accept one canonicalization specification and shared test vectors.
This placeholder selects no serialization, concatenation, encoding, or state sequence.
