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

Any future Thief private TOML remains local, role-specific, and ignored by Git. Exact
private keys and compatibility behavior are `PENDING` under ADR-0004.

Opposite-role Cop drafts are preserved outside the active configuration tree under
`archive/pre-audit/opposite-role-config/`.
