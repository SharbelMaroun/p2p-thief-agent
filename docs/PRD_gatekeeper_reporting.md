# PRD — Gatekeeper and Reporting

Status: quantitative/reporting requirements confirmed; integration details pending.

## Confirmed requirements

- External API calls use the centralized gatekeeper boundary in `PS-008`.
- Official minimums are 30 outgoing requests/minute, two concurrent requests, five
  seconds before retry, three retries, and queue depth 100. Defaults are 30-second
  response and 60-second watchdog timeouts (`AF-019`).
- Final reports are automatic JSON attachments only; each peer reports separately after
  agreement (`AE-032`).
- The general address is `rmisegal@gmail.com`; automated reports go to
  `rmisegal+uoh26finalgame@gmail.com` (`AF-020`).
- Official filenames are recorded in `AF-021`, and observed template keys are recorded
  in `JS-001..003`.

## Still open

Gmail draft-versus-send behavior, OAuth setup details, retries for each call category,
signature/canonicalization procedures, and template requiredness/types/enums remain
open (`U-002`, `U-009`, `U-019`, ADR-0010). A populated template is not a formal schema.

## Future acceptance criteria and tests

- No external API bypasses the gatekeeper.
- FIFO/backpressure, minimum limits, retries, timeouts, and monitoring are configured,
  not embedded in adapters.
- Exactly the accepted JSON result is attached; no free-text final-report body is added.
- Wrong recipient, missing agreement, malformed artifact, and secret leakage fail.
- External services are mocked in unit tests and all behavior is SDK-reachable.

No gatekeeper, Gmail, or reporting implementation is included in M1.
