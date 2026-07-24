# Shared Requirement Baseline

This file contains only shared confirmed structural and professional requirements. It
contains no gameplay values or simulator-specific names.

| ID | Requirement | Status | Direct source location |
|---|---|---|---|
| SR-001 | The final project uses one Cop repository and one Thief repository. | `CONFIRMED` | Official project book v3.0.0, Chapter 9.4 and Appendix C |
| SR-002 | Each repository README links to the other team repository. | `CONFIRMED` | Official project book v3.0.0, Chapter 9.4 and Appendix C |
| SR-003 | Both repositories must be public or otherwise accessible to the lecturer. | `CONFIRMED` | Official project book v3.0.0, Chapter 9.4 and Appendix C |
| SR-004 | Cop and Thief use separate processes and configuration environments, share no live mutable state, and cannot access the opponent’s private truth. | `CONFIRMED` | Official project book v3.0.0, Chapter 2.4.2 |
| SR-005 | Each peer acts as both a FastMCP server and FastMCP client. | `CONFIRMED` | Official project book v3.0.0, peer architecture description |
| SR-006 | Each repository contains a root README, configuration directory, PRD documents, PLAN, TODO, and code. | `CONFIRMED` | Official project book v3.0.0, Chapter 9.4 and Appendix C |
| PS-001 | Required documentation is `README.md`, `docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md`, and dedicated mechanism PRDs. | `CONFIRMED` | Professional Software Submission Guidelines v3.0, pages 7–9 |
| PS-002 | Use `uv`; keep dependencies in `pyproject.toml`; commit `uv.lock`. | `CONFIRMED` | Professional Software Submission Guidelines v3.0, pages 19–20 |
| PS-003 | Code and test files are limited to 150 code lines, excluding blanks/comments. | `CONFIRMED` | Professional Software Submission Guidelines v3.0, page 10 |
| PS-004 | Use red-green-refactor TDD, public-function tests, normal/failure paths, mocked external services, and at least 85% global coverage. | `CONFIRMED` | Professional Software Submission Guidelines v3.0, pages 15–16 |
| PS-005 | Ruff passes with zero violations using the current official course configuration. | `CONFIRMED` | Professional Software Submission Guidelines v3.0, page 17 |
| PS-006 | Do not hard-code configurable values or commit secrets; commit placeholder `.env-example` and ignore secret files. | `CONFIRMED` | Professional Software Submission Guidelines v3.0, pages 17–18 |
| PS-007 | User interfaces and integrations delegate business logic through an SDK/service boundary. | `CONFIRMED` | Professional Software Submission Guidelines v3.0, page 11 |
| PS-008 | External API calls use a centralized gatekeeper with limiting, FIFO queueing, backpressure, retries, and monitoring. | `CONFIRMED` | Professional Software Submission Guidelines v3.0, pages 13–14 |
| PS-009 | Maintain `docs/PROMPT_LOG.md`. | `CONFIRMED` | Professional Software Submission Guidelines v3.0, page 19 |
