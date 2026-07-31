"""Cross-implementation evidence for the commit construction (`M1-016`).

These assertions are pinned to a record produced by the **reference simulator**,
not by this project. That is the point: Cop and Thief are both Python and were
both written from the same reading of the wire profile, so a shared wrong
assumption would pass every same-language test and then fail against a
classmate's agent. Reproducing a foreign implementation's hash is the only
check that closes that gap.

Provenance is recorded in the fixture. See `SIM_WIRE_PROTOCOL.md`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p2p_thief_agent.protocol.crypto import canonical_json, commit_of, verify

VECTOR = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures" / "reference_commit_vector.json").read_text(
        encoding="utf-8"
    )
)
PAYLOAD = VECTOR["payload"]
NONCE = VECTOR["nonce"]
COMMIT = VECTOR["commit"]


def test_reproduces_a_real_reference_commit() -> None:
    """Our commit_of must reproduce a hash the reference implementation produced."""
    assert commit_of(PAYLOAD, NONCE) == COMMIT


def test_verify_accepts_the_reference_record() -> None:
    verify(PAYLOAD, NONCE, COMMIT)


def test_floats_render_as_the_reference_rendered_them() -> None:
    """`6.0` must not collapse to `6`, and `31.8` must not gain precision.

    This is the specific hazard the reference vector exists to catch: a
    JavaScript or Go peer that renders 6.0 as `6` produces different bytes and
    therefore a different commitment, which Appendix E rule 19 scores as zero.
    """
    canonical = canonical_json(PAYLOAD)
    assert '"vram_gb":6.0' in canonical
    assert '"ram_gb":31.8' in canonical


def test_the_nonce_is_outside_the_payload() -> None:
    """The nonce must not appear in the canonical bytes, only after the pipe."""
    assert NONCE not in canonical_json(PAYLOAD)


def test_the_book_construction_would_not_reproduce_it() -> None:
    """Records why this project diverges from the book's Chapter 5.3 sketch.

    The book seals the nonce *inside* the payload with no delimiter. Against
    real reference data that construction yields a different digest, so
    following the book literally would fail every cross-peer audit. Disclosed
    under the book p. 5 contradiction clause; see `SPECIFICATION_CONFLICTS.md`.
    """
    import hashlib

    inside = dict(PAYLOAD) | {"nonce": NONCE}
    book_digest = hashlib.sha256(
        json.dumps(inside, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert book_digest != COMMIT


@pytest.mark.parametrize("field", ["step", "model", "code_version", "group_name"])
def test_any_mutation_breaks_the_commitment(field: str) -> None:
    mutated = dict(PAYLOAD)
    mutated[field] = "tampered"
    assert commit_of(mutated, NONCE) != COMMIT
