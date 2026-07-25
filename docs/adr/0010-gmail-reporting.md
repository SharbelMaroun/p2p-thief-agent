# ADR-0010: Gmail Reporting

Status: Proposed

## Evidence

Official project book v3.0.0 Chapter 9.3 and Appendix E rules 32-34 require automated,
machine-readable JSON attachment reporting and prohibit a free-text final report.
Appendix F Table 20, page 141, assigns `rmisegal@gmail.com` to general/repository
contact and `rmisegal+uoh26finalgame@gmail.com` to automated JSON reports (`AF-020`).

## Proposal awaiting acceptance

Preserve those address roles and send final-report data only as official JSON
attachment(s), with no free-text final-report body. Attachment selection, MIME details,
draft/send mode, retries, and idempotency remain pending (`U-009`); no Gmail behavior is
implemented here.
