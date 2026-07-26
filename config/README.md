# Configuration Status

There is currently no approved runtime configuration in this repository.

All files under `config/drafts/` are unverified historical drafts. No implementation
may load them. Their exact fields, filenames, versions, values, and schemas remain
`UNKNOWN`.

Appendix F values/statuses are directly verified in
`docs/PARAMETERS_BASELINE.md`. Unauthenticated artifact-example key-presence
observations are recorded in `docs/JSON_ARTIFACT_SCHEMAS.md`.

The Cop agent owns the M1 contract proposal process. Candidate
`84339c210c8e3293d972bccec5912abf519d502c` exists, but it is unfrozen and
coordinator-rejected pending revision. No candidate file has been copied here. No
active `config/game.json`, `config/rate_limits.json`, protocol fixture, or parity
manifest will be created until the coordinator supplies an accepted handoff.

Any future Thief private TOML remains local, role-specific, ignored by Git, and outside
the parity manifest. Exact private keys/schema are pending ADR-0004.

Opposite-role Cop drafts are preserved outside the active configuration tree under
`archive/pre-audit/opposite-role-config/`.
