# ADR-0004: Shared JSON and Private TOML

Status: Pending

## Evidence

Official project book v3.0.0 Appendix B, including section B.2, distinguishes shared
`config/game.json` from local private `config/game.toml`. Match-wide values belong in
the shared signed JSON; private identity, ports/opponent URL, strategy, language-model,
email-target, and graphics settings belong in the local TOML. Shared JSON overrides a
duplicate gameplay key (`AB-001`). Unauthenticated generated examples provide
observed artifact key sets only.

## Decision needed

The filenames, high-level boundary, and shared-value precedence are confirmed. The
peers must still define the complete validated schemas, the exact parity-controlled
file set, compatibility behavior, and how secrets are loaded without entering either
tracked file. OAuth credentials must not be inferred as TOML content merely because
email settings are private (`U-013`, `U-020`).
