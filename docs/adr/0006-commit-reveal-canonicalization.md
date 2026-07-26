# ADR-0006: Commit-Reveal Canonicalization

Status: Pending

## Evidence

Official project book v3.0.0 requires SHA-256 commit-reveal, and unauthenticated
generated examples contain observed integrity fields (`JS-003`). Appendix E rule 18
keeps nonces secret until the end-game reveal. The Chapter 5 core example serializes
the shown commitment object with sorted keys and compact separators, encodes it as
UTF-8, and hashes those bytes (`CR-001`). Appendix B separately associates sorted-key
canonical JSON with consistent `config_sha256`.

The evidence does not settle the complete committed payload, nonce encoding/length,
Unicode and number normalization, array ordering, `config_sha256` inclusion/exclusion
scope, signature bytes, or wire sequencing (`U-002` and `U-005`).

## Decision needed

Cop and Thief must accept one complete canonicalization specification and shared test
vectors. The accepted decision must preserve the confirmed sorted, compact UTF-8
commit primitive while explicitly resolving the remaining byte-level questions.
