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
file set, and how secrets are loaded without entering either tracked file. OAuth
credentials must not be inferred as TOML content merely because email settings are
private (`U-013`, `U-020`).

## Settled since (2026-08-01, `M5-002f`)

The private `[network]` keys are no longer open. Checked against the pinned wire
reference and book page 131: each peer reads its own `config/<role>/game.toml` —
police and thief from **separate directories** — and takes the opponent's address
from `[network].opponent_url`. The section also carries `my_port`,
`turn_timeout_seconds`, `poll_interval_seconds`, `connect_timeout_seconds`,
`retry_interval_seconds`, and `audit_send_timeout_seconds`. `config/game.toml.example`
is the committed skeleton; the real file is git-ignored.

Asked directly whether the shared negotiated JSON ever carries a URL, port, host, or
any network address, the answer was **no**: local settings must not "leak into the
agreement". `shared/private_config.py` is the only door to an opponent address, and
`assert_no_network_address` is the lock on the other — it refuses a shared match
object carrying an address either by member **name** or by **value**, since either
check alone is easy to slip past.

The remaining open items above (complete validated schemas, the parity-controlled
file set, secret loading) are unaffected, so this ADR stays `Pending` as a whole.
