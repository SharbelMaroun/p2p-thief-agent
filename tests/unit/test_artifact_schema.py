"""`M7-012`: every emitted artifact validates, and requiredness has a citation.

The row's family asks for validation of all four artifacts plus a `game_uid` agreement
check. The constraint that shaped the design is `U-019`: the four example artifacts have
unresolved provenance and "do not prove requiredness, optionality, types, enums, bounds,
additional-property behavior". So a schema generated from them would demand keys no source
demands — and would refuse a conformant opponent for omitting one.

Hence the two tests that matter here are not the happy paths. They are:

* **every `BOOK` field cites a rule or page** — so requiredness can be defended, not just
  asserted; and
* **an unexpected key is accepted** — because `U-019` means we cannot know it is illegal,
  and refusing one would fail rule 36's mutual audit over a difference no source forbids.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.reporting.artifact_schema import (
    ARTIFACT_FIELDS,
    BOOK,
    ArtifactSchemaError,
    check_shared_game_uid,
    known_fields,
    required_fields,
    validate_artifact,
)

ARTIFACTS = tuple(sorted(ARTIFACT_FIELDS))


# --- the authority split, which is the whole design --------------------------------------


@pytest.mark.parametrize("artifact", ARTIFACTS)
def test_every_book_mandated_field_carries_a_citation(artifact: str) -> None:
    """**The test this module exists for.** A required key with no citation is a key
    somebody assumed. `U-019` says the templates cannot supply that authority, so if it is
    required, the book has to say so and the table has to name where."""
    for field in ARTIFACT_FIELDS[artifact]:
        if field.authority == BOOK:
            assert field.citation, f"{artifact}.{field.name} is required with no citation"
            assert any(token in field.citation.lower()
                       for token in ("rule", "p.", "appendix")), field.citation


@pytest.mark.parametrize("artifact", ARTIFACTS)
def test_no_template_only_field_is_ever_required(artifact: str) -> None:
    """The `U-019` constraint, enforced structurally: a key we only saw in an example can
    be emitted, never demanded of an opponent."""
    for field in ARTIFACT_FIELDS[artifact]:
        if field.authority != BOOK:
            assert not field.required, f"{artifact}.{field.name} demands a template-only key"


@pytest.mark.parametrize("artifact", ARTIFACTS)
def test_each_artifact_requires_something(artifact: str) -> None:
    """A validator requiring nothing passes everything, which is worse than no validator
    because it reads as protection."""
    assert required_fields(artifact), f"{artifact} requires no field at all"


def test_the_mandated_fields_match_what_the_book_was_asked_for() -> None:
    """Spot-checks against the direct reading, so a later edit that quietly drops one of
    these fails rather than passing with a smaller table."""
    assert "github_commit" in required_fields("declaration")   # rule 53
    assert "config_sha256" in required_fields("config")        # p.111
    assert "mutual_agreement" in required_fields("log")        # rule 36
    assert "mutual_agreement" in required_fields("result")     # rule 35
    assert "final_result" in required_fields("result")         # rule 54


# --- validation behaviour ------------------------------------------------------------------


@pytest.mark.parametrize("artifact", ARTIFACTS)
def test_an_artifact_with_every_required_field_validates(artifact: str) -> None:
    document = dict.fromkeys(required_fields(artifact), "value")
    validate_artifact(artifact, document)


@pytest.mark.parametrize("artifact", ARTIFACTS)
def test_removing_any_required_field_is_refused_and_the_error_cites_why(
    artifact: str,
) -> None:
    """The error carries the citation, so an operator reading a refusal learns which rule
    they are about to breach rather than only that something is absent."""
    for name in required_fields(artifact):
        broken = {k: "value" for k in required_fields(artifact) if k != name}
        with pytest.raises(ArtifactSchemaError, match=name):
            validate_artifact(artifact, broken)


@pytest.mark.parametrize("artifact", ARTIFACTS)
def test_an_unexpected_key_is_accepted(artifact: str) -> None:
    """**Deliberate.** `U-019` means we cannot know an unfamiliar key is illegal, and
    refusing an opponent's artifact for carrying one would fail rule 36's mutual audit over
    a difference no source forbids."""
    document = dict.fromkeys(required_fields(artifact), "value")
    validate_artifact(artifact, {**document, "some_future_key": 1})


@pytest.mark.parametrize("shape", [None, [], "text", 42])
def test_an_artifact_that_is_not_an_object_is_refused(shape: object) -> None:
    with pytest.raises(ArtifactSchemaError, match="not an object"):
        validate_artifact("declaration", shape)


def test_an_unknown_artifact_type_is_refused_rather_than_skipped() -> None:
    with pytest.raises(ArtifactSchemaError, match="unknown artifact type"):
        validate_artifact("not_an_artifact", {})


def test_known_fields_covers_required_plus_template() -> None:
    for artifact in ARTIFACTS:
        assert set(required_fields(artifact)) <= set(known_fields(artifact))


# --- M7-012e: the four files must describe one match ---------------------------------------


def test_a_matching_set_returns_its_shared_uid() -> None:
    uid = check_shared_game_uid({name: {"game_uid": "u-1"} for name in ARTIFACTS})
    assert uid == "u-1"


def test_a_set_assembled_from_two_matches_is_refused() -> None:
    """**The check that catches the plausible mistake.** Four files that each validate
    perfectly, describing between them a match that never happened — the shape a rushed
    re-run produces when one artifact is left over from the previous game (`AR-001`)."""
    mixed = {name: {"game_uid": "u-1"} for name in ARTIFACTS}
    mixed["result"] = {"game_uid": "u-2"}
    with pytest.raises(ArtifactSchemaError, match="does not share one game_uid"):
        check_shared_game_uid(mixed)


def test_a_set_with_a_missing_uid_is_refused_rather_than_treated_as_matching() -> None:
    """`None == None` would make two artifacts that both forgot the field look consistent."""
    mixed = {name: {"game_uid": "u-1"} for name in ARTIFACTS}
    mixed["log"] = {}
    with pytest.raises(ArtifactSchemaError, match="does not share one game_uid"):
        check_shared_game_uid(mixed)
