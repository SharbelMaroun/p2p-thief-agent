"""`M1-013a`: every profile item is labelled, and no simulator behaviour is mandatory.

The row's condition is unusual in that it constrains a *document* rather than code:
"No item is unlabelled; simulator behaviour is never promoted to mandatory." A prose
promise decays the moment someone adds a row to the table, so it is asserted here.

Why the second clause matters more than it looks. The book and the reference **disagree**
about the commit construction — `inst/police_thief_p2p_Summary.md:1107` puts the nonce
inside the hashed string, the reference concatenates it outside behind a bar, and the two
produce different digests on the same record. We follow the reference, with a reproduced
real-match digest as evidence. Labelling that "book-confirmed" would be false; labelling
it "mandatory" would hide a deliberate deviation behind a rule number. It is labelled as
what it is, and this file keeps it that way.
"""

from __future__ import annotations

import re
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2] / "docs" / "SIM_WIRE_PROTOCOL.md"
LABELS = (
    "book-mandatory",
    "book-confirmed",
    "book-minimum",
    "simulator-derived",
    "Option-B project choice",
    "project choice",
    "UNKNOWN",
)


def _rows() -> list[tuple[str, str, str]]:
    """Return (item, authority, evidence) for every row of the authority table."""
    text = PROFILE.read_text(encoding="utf-8")
    table = text[text.index("| Item | Authority | Evidence |") :]
    table = table[: table.index("\n\n")]
    rows = []
    for line in table.splitlines()[2:]:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3:
            rows.append((cells[0], cells[1], cells[2]))
    return rows


def test_the_authority_table_exists_and_is_not_a_stub() -> None:
    rows = _rows()
    assert len(rows) >= 15, f"only {len(rows)} items labelled; the profile has more than that"


def test_no_item_is_unlabelled() -> None:
    """`M1-013a`: "No item is unlabelled". An item with no authority is not part of the
    profile — it is a guess someone will later mistake for a decision."""
    for item, authority, _ in _rows():
        assert any(label in authority for label in LABELS), f"{item!r} has no authority label"


def test_no_simulator_derived_item_is_promoted_to_mandatory() -> None:
    """The clause this file exists for. "Simulator behaviour is never promoted to
    mandatory" — the reference is evidence of what interoperates, never of what is
    required, and conflating the two would let a wire detail acquire a sanction it does
    not carry."""
    for item, authority, _ in _rows():
        if "simulator-derived" in authority:
            assert "book-mandatory" not in authority, f"{item!r} promotes the simulator to mandatory"


def test_every_book_claim_cites_a_rule_table_or_line() -> None:
    """A book label without a citation is an assertion, not evidence — and this test
    caught exactly that while the table was being written: canonical JSON was labelled
    `book-mandatory` on a notebook's say-so, with nothing behind it. Checking `inst/`
    found the book *does* fix it (`:1212`) but in a **code listing**, not a ruled
    sanction, so the label became `book-confirmed`. The distinction is the whole point of
    `M1-013a`: a listing must not borrow a rule's authority."""
    for item, authority, evidence in _rows():
        if any(k in authority for k in ("book-mandatory", "book-confirmed", "book-minimum")):
            assert re.search(r"rule \d+|table \d+|Appendix [EF]|:\d{3,4}", evidence), (
                f"{item!r} claims book authority with no rule, table or line cited"
            )


def test_the_commit_layout_is_not_claimed_as_book_authority() -> None:
    """The specific trap. We deviate from `:1107` knowingly; the label must say so rather
    than borrowing rule 17's authority, which covers the *mechanism* only."""
    layout = [r for r in _rows() if "byte layout" in r[0]]
    assert layout, "the commit byte layout must be labelled explicitly, not left implicit"
    item, authority, _ = layout[0]
    assert "simulator-derived" in authority
    assert "deviates" in authority, "a knowing deviation must be visible in the label itself"


def test_the_deviation_is_explained_where_a_reader_will_find_it() -> None:
    """A label alone would leave the reader knowing we differ but not why it is safe."""
    text = PROFILE.read_text(encoding="utf-8")
    section = text[text.index("### The one place we knowingly depart from the book") :]
    assert "rule 17" in section.lower(), "the deviation must say why the mandatory rule still holds"
    assert "78a31c51" in section, "the deviation must cite the reproduced real-match digest"


def test_the_profile_does_not_cite_archived_artifacts_as_current_evidence() -> None:
    """The realign archived `WIRE_CONFORMANCE_PROFILE.md`, `protocol/canonical.py`,
    `commitment.py` and `negotiation.py`. Citing a deleted file as evidence is how a
    checklist stays ticked while the thing it certified no longer exists."""
    text = PROFILE.read_text(encoding="utf-8")
    for archived in ("WIRE_CONFORMANCE_PROFILE.md", "protocol/canonical.py",
                     "protocol/commitment.py", "protocol/negotiation.py"):
        assert archived not in text, f"profile still cites the archived {archived}"
