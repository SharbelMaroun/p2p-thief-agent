# Configuration Status

There is currently no active played-match runtime configuration in this repository.

All files under `config/drafts/` are unverified historical drafts. No implementation
may load them. Their exact fields, filenames, versions, values, and schemas remain
`UNKNOWN`.

Appendix F values/statuses are directly verified in
`docs/PARAMETERS_BASELINE.md`. Unauthenticated artifact-example key-presence
observations are recorded in `docs/JSON_ARTIFACT_SCHEMAS.md`.

The Thief authors its own conformance profile under `THIEF-002`; no peer file is an
input. Active per-match JSON will be generated only from an accepted profile and
validated negotiated values. Historical drafts remain evidence only and are never
loaded by runtime code.

The Thief private TOML is local, role-specific, and ignored by Git. It lives in the
Thief's **own role directory** (`M5-006`): `config/thief/game.toml.example` is the
committed skeleton, and the real `config/thief/game.toml` is never shared, signed, or
sent. `shared.private_config.load_thief_private_config` resolves only that directory, so
this peer can never read a `config/police/` sibling even from one checkout `[AE-1]`.

The exact private keys were `PENDING` under ADR-0004 and are now settled (`M5-002f`,
2026-07-31), matching the skeleton the book publishes on page 131 and the pinned wire
reference's own `config/thief/game.toml`. The opponent's address is read only from
`[network].opponent_url`, by `shared.private_config.load_opponent_url`. The shared
match JSON carries no URL, port, host, or any network address at all; a peer that tries
to put one there is refused by `assert_no_network_address`.

Ports, opponent URL, models, credentials, tunnels, strategy tuning, and per-turn
commitment nonces are private. The public negotiation challenge nonce is wire data, not
private configuration.

Opposite-role Cop drafts are preserved outside the active configuration tree under
`archive/pre-audit/opposite-role-config/`.
