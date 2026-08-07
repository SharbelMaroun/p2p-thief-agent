"""What each artifact must carry, and on whose authority (`M7-012`, `M7-024`).

**Why this is a table and not a JSON Schema file.** `docs/JSON_ARTIFACT_SCHEMAS.md` records
that the four example artifacts have unresolved provenance (`U-019`) and "prove only that
the listed keys occur in the inspected bytes. They do not prove requiredness, optionality,
types, enums, bounds, additional-property behavior, every nested shape, or binding
provenance."

A schema generated from those examples would assert requiredness the sources do not
support, and would then **refuse a conformant opponent** whose artifact omits a key that
was only ever an example. So requiredness here comes from the *book*, and every entry
records which authority put it there. A JSON Schema file cannot express that distinction;
this table can, and `test_artifact_schema.py` asserts every `BOOK` entry cites a rule or a
page.

It also avoids adding `jsonschema` as a runtime dependency (`M8-009c`), and matches how
this repository already validates — explicit field checks in `protocol/wire.py` rather than
schema documents. The companion repository does it the other way; both are pinned as
correct for their own repository rather than reconciled into one.

**The book-mandated sets**, from a direct reading of the four templates alongside the book:

* **declaration** — full hardware spec, LLM model name, the **commit hash** (rule 53),
  group identity and members, repository links, MCP addresses, the agreed token limit, and
  series start/end times.
* **config** — `config_sha256`, the scent-model lock (rule 23), and every Appendix F
  quantitative section.
* **log** — a per-step signature covering state, move, intent and nonce; the revealed move
  and hint; and the mutual-agreement confirmation (rule 36).
* **result** — the commit hash (rule 53), tokens per game *and* per series (rule 54), four
  repository links (rule 49), and mutual agreement on the outcome (rule 35).

Everything else the templates show is `TEMPLATE` — emitted because it is useful and an
opponent may expect it, never required of *them*.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass

BOOK = "book"
TEMPLATE = "template"


@dataclass(frozen=True)
class Field:
    """One artifact key, its authority, and the citation that justifies requiring it."""

    name: str
    authority: str
    citation: str = ""

    @property
    def required(self) -> bool:
        """Only the book can make a key required. A template key is emitted, not demanded."""
        return self.authority == BOOK


def _fields(book: Mapping[str, str], template: tuple[str, ...]) -> tuple[Field, ...]:
    return tuple(
        [Field(name, BOOK, citation) for name, citation in book.items()]
        + [Field(name, TEMPLATE) for name in template]
    )


ARTIFACT_FIELDS: dict[str, tuple[Field, ...]] = {
    "declaration": _fields(
        {
            "groups": "group identity, members, repos and MCP addresses (p.39, 78)",
            "github_commit": "rule 53 — the commit hash of the code that played",
            "max_tokens_per_game": "the agreed token limit (p.78)",
            "game_started_at": "series start time (p.78)",
            "game_ended_at": "series end time (p.78)",
        },
        ("_schema", "schema_version", "declaration_type", "game_uid", "game_id", "links",
         "timezone", "num_sub_games"),
    ),
    "config": _fields(
        {
            "config_sha256": "the configuration lock (p.111); rule 11 requires byte identity",
            "board_and_agents": "Appendix F quantitative section (p.136-139)",
            "movement_and_barriers": "Appendix F quantitative section",
            "scoring": "Appendix F quantitative section",
            "pheromones": "Appendix F quantitative section; rule 23 locks the scent model",
            "network_and_league": "Appendix F quantitative section",
            "rate_limiter_gatekeeper": "Appendix F table 19",
        },
        ("_schema", "schema_version", "game_id", "game_uid", "sub_game_number",
         "agreed_between", "links", "config_name", "world", "_note"),
    ),
    "log": _fields(
        {
            "records": "per-step signature over state, move, intent and nonce (p.34, 58)",
            "mutual_agreement": "rule 36 — the comprehensive mutual audit",
        },
        ("_schema", "schema_version", "game_id", "game_uid", "links", "summary"),
    ),
    "result": _fields(
        {
            "sub_games": "per-game tokens and outcome (rule 54)",
            "final_result": "series totals including tokens_total_series (rule 54)",
            "groups": "four repository links across both groups (rule 49)",
            "mutual_agreement": "rule 35 — agreed result; a contradiction scores 0 for both",
        },
        ("_schema", "schema_version", "game_id", "game_uid", "links", "timezone",
         "report_type", "num_sub_games"),
    ),
}


class ArtifactSchemaError(ValueError):
    """Raised when an artifact omits something the book requires."""


def required_field_digest() -> str:
    """A digest over every book-mandated key, for `M7-024`.

    **Why a digest and not a version bump.** `M7-024` asks that a schema change be visible
    rather than silent. The obvious reading — increment `SCHEMA_VERSION` — is the wrong
    move here: `docs/JSON_ARTIFACT_SCHEMAS.md` records that every inspected template carries
    `schema_version: 1.1`, and `U-019` leaves the provenance of those templates unresolved.
    Emitting a number no observed source shows would invite a peer matching on `1.1` to
    refuse our declaration, which is a real cost against an unresolved question.

    So visibility is enforced the other way round: this digest is pinned by a test, and any
    change to the required set fails it. The change is then made deliberately — including
    the decision about whether the version should move — instead of slipping through.
    """
    line = ";".join(f"{artifact}:{','.join(required_fields(artifact))}"
                    for artifact in sorted(ARTIFACT_FIELDS))
    return hashlib.sha256(line.encode()).hexdigest()[:16]


def required_fields(artifact: str) -> tuple[str, ...]:
    return tuple(f.name for f in ARTIFACT_FIELDS[artifact] if f.required)


def known_fields(artifact: str) -> tuple[str, ...]:
    return tuple(f.name for f in ARTIFACT_FIELDS[artifact])


def validate_artifact(artifact: str, document: object) -> None:
    """Refuse an artifact missing a book-mandated key. Extra keys are permitted.

    Extra keys are *deliberately* allowed: `U-019` means we cannot know that a key we have
    never seen is illegal, and refusing an opponent's artifact for carrying one would fail
    rule 36's mutual audit over a difference no source forbids.
    """
    if artifact not in ARTIFACT_FIELDS:
        raise ArtifactSchemaError(f"unknown artifact type {artifact!r}")
    if not isinstance(document, Mapping):
        raise ArtifactSchemaError(f"{artifact} artifact is not an object")
    missing = [name for name in required_fields(artifact) if name not in document]
    if missing:
        cited = {f.name: f.citation for f in ARTIFACT_FIELDS[artifact]}
        detail = "; ".join(f"{name} ({cited[name]})" for name in missing)
        raise ArtifactSchemaError(f"{artifact} artifact is missing {detail}")


def check_shared_game_uid(artifacts: Mapping[str, Mapping[str, object]]) -> str:
    """Every artifact of one match carries the same `game_uid` (`M7-012e`, `AR-001`).

    This is the check that catches a set assembled from two different matches — four files
    that each validate perfectly and together describe nothing that happened.
    """
    seen = {name: document.get("game_uid") for name, document in artifacts.items()}
    distinct = set(seen.values())
    if len(distinct) != 1 or None in distinct:
        raise ArtifactSchemaError(f"artifact set does not share one game_uid: {seen}")
    return str(distinct.pop())
