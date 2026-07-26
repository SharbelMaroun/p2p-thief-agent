# ADR-0004: Shared JSON and Private TOML

Status: Pending

## Evidence

Official project book v3.0.0 Appendix B, including section B.2, distinguishes shared
JSON from local private TOML. Unauthenticated generated examples provide observed
artifact key sets only; the active shared filename and private TOML schema remain
unknown (`U-013`).

## Decision needed

The peers must jointly define parity-controlled JSON, local-only TOML, precedence,
validation, and secret boundaries. This placeholder chooses no filename, schema, or
override behavior.
