# P2P Thief Agent

Thief-side repository for the “Distributed Cops-and-Robbers over a Peer-to-Peer
Network” final project.

> Companion Cop repository: <https://github.com/SharbelMaroun/p2p-cop-agent>

## Requirements status

This repository is in a requirements-audit phase. It does not yet contain a verified
runtime implementation. Existing configuration and design drafts are not implementation
authority.

- [Requirements ledger](docs/REQUIREMENTS_LEDGER.md)
- [Unknown requirements](docs/UNKNOWN_REQUIREMENTS.md)
- [Specification conflicts](docs/SPECIFICATION_CONFLICTS.md)
- [Verification policy](docs/VERIFICATION_POLICY.md)
- [Source inventory](docs/SOURCE_INVENTORY.md)
- [Repository audit](docs/REPOSITORY_AUDIT.md)

Only ledger entries marked `CONFIRMED` may be implemented as requirements. Numerical
values, schemas, filenames, protocol messages, tool names, timeouts, game counts,
cryptographic fields, reporting behavior, model names, ports, email addresses, README
contents, and submission-tag rules remain non-binding unless supported by direct
authoritative evidence.

## Scope

The eventual runtime represented here is the Thief peer only. Thief-specific work may
cover evasion strategy, a local belief about the Cop, Cop-scent observations, the
survival objective, a Thief truth/bluff policy, and Thief-local state and private
settings. This repository must not import from, mount, or depend on the Cop repository.

Generic stateless protocol or domain code may be considered only after the permission
to duplicate/share it independently has been verified. Shared live state is prohibited
by the task boundary; the wider official rule still requires direct verification.

## Current repository contents

- `docs/` contains the audit and quarantined pre-audit design drafts.
- `config/thief/` contains unverified configuration drafts. They are not active
  requirements or safe implementation inputs.
- `config/police/` is role-confused material retained for teammate safety and classified
  `REMOVE LATER`; it must not guide the Thief runtime.
- `Material/` contains local reference material. Summaries and translations are
  navigation aids, not binding evidence.

No installation or usage command is published yet because the package requirements,
entry points, and dependencies have not been verified from the authoritative sources.

## Academic report placeholders

The required README/report structure and exact section count are `UNKNOWN`. The eventual
report must add only directly verified sections. Candidate Thief topics, pending
verification, include system model, peer-to-peer communication, Thief evasion and
belief strategy, experimental evidence, screenshots/replay evidence, and companion
repository information. These are placeholders, not a claim about mandatory structure.

## License

See [LICENSE](LICENSE). Applicability of the current license to all future code and
course-provided material must be reviewed before sources are added.
