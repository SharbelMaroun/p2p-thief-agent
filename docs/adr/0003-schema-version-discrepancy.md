# ADR-0003: Schema-Version Discrepancy

Status: Pending

## Evidence

Official project book v3.0.0 Appendix B shows `schema_version` 1.2, while all four
inspected unauthenticated generated examples use 1.1 (`JS-001`; see
[JSON_ARTIFACT_SCHEMAS.md](../JSON_ARTIFACT_SCHEMAS.md)).

## Decision needed

Authoritative clarification or a jointly accepted Cop/Thief ADR must determine the
version for each artifact and any compatibility policy. Neither value is silently
normalized or selected here.
