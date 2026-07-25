# P2P Thief Agent

Thief-side repository for the “Distributed Cops-and-Robbers over a Peer-to-Peer
Network” final project.

> Companion Cop repository: <https://github.com/SharbelMaroun/p2p-cop-agent>

## Requirements status

This repository is in the verified-requirements phase. Structural and professional
requirements with direct support are recorded as `CONFIRMED`; unresolved gameplay,
protocol, configuration, and reporting details remain `UNKNOWN`. There is no runtime
implementation or approved runtime configuration yet.

- [Requirements ledger](docs/REQUIREMENTS_LEDGER.md)
- [Shared structural baseline](docs/SHARED_REQUIREMENT_BASELINE.md)
- [Unknown requirements](docs/UNKNOWN_REQUIREMENTS.md)
- [Specification conflicts](docs/SPECIFICATION_CONFLICTS.md)
- [Verification policy](docs/VERIFICATION_POLICY.md)
- [Repository audit](docs/REPOSITORY_AUDIT.md)
- [Configuration status](config/README.md)

No installation or run commands are published until the package and runtime contracts
are verified.

## Confirmed structural requirements

- The final project uses separate Cop and Thief repositories, each linking to the other
  and accessible to the lecturer.
- Cop and Thief run as separate processes with separate configuration environments,
  local state, and no access to the opponent’s private truth.
- Each peer acts as both a FastMCP server and client; exact tool names remain `UNKNOWN`.
- Each repository includes a root README, configuration directory, PRDs, PLAN, TODO,
  and code in its completed form.
- Required documentation includes `README.md`, `docs/PRD.md`, `docs/PLAN.md`,
  `docs/TODO.md`, and dedicated PRDs for important mechanisms.
- Professional requirements confirm `uv`, committed `pyproject.toml` and `uv.lock`,
  code/test file-size limits, TDD and coverage, Ruff, configuration/secrets controls,
  an SDK/service boundary, a centralized external-API gatekeeper, and
  `docs/PROMPT_LOG.md`.

These statements summarize `SR-001` through `SR-006` and `PS-001` through `PS-009`.
Appendix F gameplay values and statuses are directly confirmed as `AF-013` through
`AF-022`. Official JSON schemas, exact MCP messages, and unverified simulator details
remain `UNKNOWN`.

## Thief scope

This repository represents only the Thief peer at runtime. Thief concerns include
evasion, belief about the Cop, Cop-scent observation, survival, route selection,
Thief-local strategy, and Thief-local verbal behavior. Confirmed Appendix F values do
not by themselves settle formulas, event ordering, schemas, or protocol messages.

The Thief implementation must not import the Cop repository’s private runtime code,
depend on its filesystem, or share live mutable state with it. Whether independently
duplicated stateless packages are permitted remains `UNKNOWN`.

## Configuration

There is no approved runtime configuration. Historical Thief drafts are quarantined
under `config/drafts/thief/`; no implementation may load them. See
[config/README.md](config/README.md).

## License

The current [MIT license](LICENSE) applies only to team-authored material where legally
valid. Lecturer-provided documents and code are not automatically relicensed. The final
licensing decision remains subject to review.

Documentation completeness in this requirements-remediation phase does not mean the
project is submission-complete. Runtime implementation, tests, official JSON schemas,
match evidence, repository access, release tagging, and current Moodle requirements
remain separate submission gates.
