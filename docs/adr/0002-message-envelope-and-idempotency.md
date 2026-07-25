# ADR-0002: Message Envelope and Idempotency

Status: Pending

## Evidence

The peers require one interoperable wire format, but the official field set remains
unknown (`U-003` in [UNKNOWN_REQUIREMENTS.md](../UNKNOWN_REQUIREMENTS.md)).

## Decision needed

A cross-team ADR must define the envelope, correlation and version fields, duplicate
detection, retry semantics, and error representation. This placeholder selects no
field, identifier, timeout, or idempotency algorithm.
