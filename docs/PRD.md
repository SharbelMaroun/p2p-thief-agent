# Product Requirements Document

Status: M0 reconciliation complete; M1 scaffold in progress; shared contract pending.

## Product boundary

This repository delivers only the independently installable Thief peer (`THIEF-001`).
The current milestone creates documentation, package boundaries, tests, and quality
gates. It does not implement gameplay, networking, cryptography, LLM access, Gmail,
GUI, or replay.

The official book v3.0.0, authenticated official JSON templates when available, and
professional submission guidelines control requirements in the order recorded by
[SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md). Simulator behavior is reference evidence only.

## M1 goals

| ID | Requirement | Acceptance criterion | Evidence/test |
|---|---|---|---|
| M1-PRD-001 | Installable uv package | `uv sync --frozen` succeeds from the committed lock | Clean-install gate |
| M1-PRD-002 | One public SDK boundary | Importing `ThiefSdk` succeeds and exposes only scaffold metadata | `tests/unit/test_sdk.py` |
| M1-PRD-003 | Runnable scaffold | `p2p-thief --help` exits successfully without starting runtime behavior | `tests/integration/test_cli.py` |
| M1-PRD-004 | Enforced quality policy | Ruff has zero findings; branch coverage is at least 85%; size and secret checks pass | Quality commands in README |
| M1-PRD-005 | Contract consumer, not author | Accepted Cop files are copied byte-for-byte and hashes match, or the gate remains explicitly pending | `scripts/check_shared_contracts.py` |
| M1-PRD-006 | Evidence-preserving docs | Appendix E/F evidence and generated-example JSON observations remain traceable without overstated provenance | Repository audit review |

## Future product requirements

Confirmed future behavior includes independent peer processes, orthogonal movement plus
stay, barrier disclosure and capture rules, SHA-256 commit-reveal, explicit state
machines, deadlines/watchdogs, local-truth GUI, six-game series minimum configuration,
official scores and scent defaults, and JSON-only final reports. Exact MCP messages,
commit canonicalization, schema constraints beyond inspected key sets, private TOML,
and some event ordering remain gated in
[UNKNOWN_REQUIREMENTS.md](UNKNOWN_REQUIREMENTS.md).

Future implementations must expose business behavior through the SDK (`PS-007`) and
test normal, boundary, and failure paths (`PS-004`).

## Non-goals for M1

- No legal-move or capture implementation.
- No FastMCP server/client, public tunnel, state machine, or watchdog runtime.
- No commit/reveal hashing or nonce generation.
- No scent, belief, strategy, LLM, Gmail, GUI, replay, or reporting behavior.
- No active shared configuration or invented protocol fixture.
- No dependency on the Cop repository or lecturer simulator at runtime.

## Release gate

M2 begins only after the coordinator accepts a revised Cop proposal and supplies the
complete handoff, accepted parity-controlled bytes are present in both repositories,
and the manifest and per-file hash checks pass. Until then the contract status is
`PENDING`.
