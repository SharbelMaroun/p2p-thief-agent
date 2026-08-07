"""`M7-024`: a schema change is visible, not silent.

The row's obvious reading is "increment `SCHEMA_VERSION` when the shape changes", and that
reading was **rejected**. `docs/JSON_ARTIFACT_SCHEMAS.md` records that every inspected
template carries `schema_version: 1.1`, and `U-019` leaves those templates' provenance
unresolved. Emitting a number no observed source shows would invite a peer that matches on
`1.1` to refuse our declaration — a concrete cost paid against an unresolved question.

So visibility is enforced from the other side. The digest below pins the book-mandated
field set; changing it fails this test, and the change then has to be made deliberately —
including deciding whether the version ought to move — rather than slipping through.

The pinned value moved once already, on 2026-08-07, when rule 53's `github_commit` was
added to the declaration. That is the guard working as intended: the field had been missing
since the artifact was first written, and nothing had failed.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.reporting import SCHEMA_VERSION
from p2p_thief_agent.reporting.artifact_schema import (
    ARTIFACT_FIELDS,
    required_field_digest,
    required_fields,
)

PINNED_DIGEST = "ec9053b9c06edbc6"


def test_the_required_field_set_has_not_changed_without_notice() -> None:
    """**The `M7-024` guard.** If this fails, the required set changed. Decide whether the
    change is intended, whether `SCHEMA_VERSION` should move with it, and whether an
    opponent mid-series can still validate what we emit — then update the pin."""
    assert required_field_digest() == PINNED_DIGEST, (
        "the book-mandated field set changed; update PINNED_DIGEST deliberately and say "
        "in the commit why the version did or did not move [M7-024]")


def test_the_emitted_schema_version_matches_the_observed_templates() -> None:
    """Pinned to `1.1` because that is what every inspected template shows. This is the
    other half of the same decision: the version is held still *on purpose*, so the digest
    above is what carries the change signal."""
    assert SCHEMA_VERSION == "1.1"


@pytest.mark.parametrize("artifact", sorted(ARTIFACT_FIELDS))
def test_the_digest_covers_every_artifact(artifact: str) -> None:
    """A digest that silently skipped an artifact would pin nothing for it, and the row it
    is meant to protect would be the one that changes unnoticed."""
    assert required_fields(artifact), f"{artifact} contributes nothing to the digest"


def test_the_digest_moves_when_a_required_field_is_added() -> None:
    """Proves the guard bites rather than merely existing — the failure mode of a pinned
    constant is that it pins something that never varies."""
    before = required_field_digest()
    from p2p_thief_agent.reporting.artifact_schema import BOOK, Field  # noqa: PLC0415

    ARTIFACT_FIELDS["log"] = (*ARTIFACT_FIELDS["log"], Field("invented", BOOK, "rule 0"))
    try:
        assert required_field_digest() != before
    finally:
        ARTIFACT_FIELDS["log"] = tuple(f for f in ARTIFACT_FIELDS["log"]
                                       if f.name != "invented")
    assert required_field_digest() == before, "the fixture failed to restore the table"
