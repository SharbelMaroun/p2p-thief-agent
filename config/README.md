# Configuration Status

There is currently no approved runtime configuration in this repository.

All files under `config/drafts/` are unverified historical drafts. No implementation
may load them. Their exact fields, filenames, versions, values, and schemas remain
`UNKNOWN`.

Appendix F values/statuses are directly verified in
`docs/PARAMETERS_BASELINE.md`. Official template key-presence evidence is recorded in
`docs/JSON_ARTIFACT_SCHEMAS.md`.

The Cop agent owns the M1 contract proposal process. No proposal is currently
available, so no active `config/game.json`, `config/rate_limits.json`, protocol
fixture, or parity manifest is created here. Accepted parity-controlled files will be
copied byte-for-byte only after source review and hash verification.

Any future Thief private TOML remains local, role-specific, ignored by Git, and outside
the parity manifest. Exact private keys/schema are pending ADR-0004.

Opposite-role Cop drafts are preserved outside the active configuration tree under
`archive/pre-audit/opposite-role-config/`.
