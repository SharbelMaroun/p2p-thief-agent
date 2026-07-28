# Product Requirements Document

Status: M0 and M2 complete; M1 conformance profile in progress.

## Product boundary

This repository delivers only the independently installable Thief peer (`THIEF-001`).
The package contains the M2 domain and deterministic baseline behind the SDK. M1 adds
an independently authored interoperability profile and conformance evidence without
starting live gameplay, networking, LLM access, Gmail, GUI, or replay.

The official book v3.0.0, authenticated official JSON templates when available, and
professional submission guidelines control requirements in the order recorded by
[SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md). Simulator behavior is reference evidence only.

## M1 goals

| ID | Requirement | Acceptance criterion | Evidence/test |
|---|---|---|---|
| M1-PRD-001 | Installable uv package | `uv sync --frozen` succeeds from the committed lock | Clean-install gate |
| M1-PRD-002 | One public SDK boundary | SDK imports succeed and implemented domain/strategy behavior is exposed through that boundary | SDK export tests |
| M1-PRD-003 | Runnable scaffold | `p2p-thief --help` exits successfully without starting runtime behavior | `tests/integration/test_cli.py` |
| M1-PRD-004 | Enforced quality policy | Ruff has zero findings; branch coverage is at least 85%; size and secret checks pass | Quality commands in README |
| M1-PRD-005 | Independent conformance profile | A Thief-authored profile passes bidirectional and negative tests against a neutral stub without consuming peer files | `tests/contract/` |
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

- No new legal-move or capture behavior beyond the completed M2 domain.
- No FastMCP server/client, public tunnel, state machine, or watchdog runtime.
- No commit/reveal hashing or nonce generation.
- No scent, belief, strategy, LLM, Gmail, GUI, replay, or reporting behavior.
- No active shared configuration or invented protocol fixture.
- No dependency on the Cop repository or lecturer simulator at runtime.

## Sequential completion gate

M1 completes after the Thief-authored Stage A profile, Stage B evidence, and an
explicitly recorded Stage C acceptance. Later milestones remain `PENDING` until the
preceding phase has verified exit evidence. The protected checker remains `PENDING`
until the accepted profile revision is recorded.
