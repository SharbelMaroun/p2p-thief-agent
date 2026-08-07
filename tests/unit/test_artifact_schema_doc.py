"""`M1-025`: the schema document describes the artifacts this repository actually emits.

`docs/JSON_ARTIFACT_SCHEMAS.md` records what was observed in the example artifacts and what
the book independently confirms. It is the document a grader reads to learn the shape of our
output, and it is prose — nothing enforces it, so it decays silently every time a builder
gains a field.

It had already decayed twice when this test was written, in the way documentation always
does: `os` was added to `hardware_spec` on 2026-08-07 for rule 24, `github_commit` to the
declaration for rule 53, and both edits stopped at the code. The document still described the
previous shape and still read as current, which is worse than being obviously stale.

The check is per **section**, not per file. A whole-document search would have passed
`github_commit` — the word appears under `4-final-result.json`, where it means the commit of
one sub-game, while its absence from the declaration is the actual gap. Fields sharing a name
across artifacts are exactly the ones a loose check waves through, so each key is looked for
in the section describing the artifact that emits it.

Direction is deliberate: **emitted ⊆ documented**. The reverse would forbid the document from
discussing a template field we deliberately do not emit, and recording those is much of why
this file exists (`U-019`).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from p2p_thief_agent.reporting import (
    artifact_schema,
    config_artifact,
    declaration,
    log_artifact,
    result_artifact,
)

DOC = Path(__file__).resolve().parents[2] / "docs" / "JSON_ARTIFACT_SCHEMAS.md"

# The heading of the section describing each artifact, and the nested key tuples its builder
# enforces. Read from the modules rather than copied, so a renamed field moves the test with
# it instead of leaving the test asserting a name nothing uses any more.
SECTIONS = {
    "declaration": ("`1-pre-game-declaration.json`",
                    declaration._GROUP_KEYS + declaration._HARDWARE_KEYS),
    "config": ("`2-agreed-config.json`", config_artifact._SECTIONS),
    "log": ("`3-game-log.json`",
            log_artifact._SUMMARY_KEYS + log_artifact._RECORD_KEYS + log_artifact._MUTUAL_KEYS),
    "result": ("`4-final-result.json`",
               result_artifact._SUBGAME_KEYS + result_artifact._FINAL_KEYS),
}


def documented(heading: str) -> set[str]:
    """Every backticked identifier under one `##` heading."""
    text = DOC.read_text(encoding="utf-8")
    for chunk in re.split(r"^## ", text, flags=re.M)[1:]:
        head, _, body = chunk.partition("\n")
        if head.strip() == heading:
            return set(re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", body))
    pytest.fail(f"{DOC.name} has no section titled {heading}")
    return set()


@pytest.mark.parametrize("artifact", sorted(SECTIONS))
def test_every_emitted_field_is_described_in_its_own_section(artifact: str) -> None:
    """**The drift this exists to catch.** Two fields were added to the builders and never to
    the document; both are Mandatory rules with sanctions, and neither edit was noticed."""
    heading, nested = SECTIONS[artifact]
    keys = tuple(f.name for f in artifact_schema.ARTIFACT_FIELDS[artifact]) + nested
    missing = sorted({key for key in keys if key not in documented(heading)})
    assert not missing, (
        f"{DOC.name} section {heading} does not mention {missing}, which "
        f"`build_{artifact}` requires. Describe them there, or stop emitting them")


def test_a_shared_field_name_must_appear_in_each_section_that_emits_it() -> None:
    """Why the check is per section. `github_commit` means the series commit in the
    declaration (rule 53) and one sub-game's commit in the result; a document-wide search
    finds the second and reports the first as documented."""
    assert "github_commit" in documented("`1-pre-game-declaration.json`")
    assert "github_commit" in documented("`4-final-result.json`")


def test_the_operating_system_is_documented_as_part_of_the_spec() -> None:
    """`inst/:1278` lists Operating System first among the required specifications, and rule
    24's sanction is denial of eligibility for the computational bonus."""
    assert "os" in documented("`1-pre-game-declaration.json`")


def test_the_check_would_notice_an_undocumented_field() -> None:
    """A guard on the guard: the section parser must return names, not an empty set that
    would make every assertion above vacuously true."""
    described = documented("`3-game-log.json`")
    assert {"summary", "records", "mutual_agreement"} <= described
    assert "field_that_is_not_in_any_artifact" not in described
