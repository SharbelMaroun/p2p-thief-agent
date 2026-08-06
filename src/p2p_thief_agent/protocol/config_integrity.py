"""Two ways a shared config can be wrong that field-by-field checks never see.

`check_appendix_f` already refuses an altered `FIXED` value or a weakened `MINIMUM` one.
Both of those inspect *values*. The two guards here inspect the config's **shape** and
its **membership**, which is where the remaining `M1-017` vectors live.

**Duplicate keys (`M1-017b`).** `json.loads('{"a":1,"a":2}')` silently returns `{"a": 2}`
— the last wins, no error. Appendix E rule 11 is Mandatory and requires the configuration
to be "identical, bit-for-bit, on both sides", sanction "disqualification of the game due
to lack of symmetry". A document with a repeated key cannot satisfy that: re-serialising
what we parsed produces *different bytes* from what arrived, so "the same file" means two
things at once. Worse, a signature computed over the raw bytes and verified over the
parsed object would be checking a different document than the one that was sent. Python
hands you the collision silently, so the refusal has to be explicit.

**Private fields in the shared config (`M1-017c`).** The book splits configuration by
format for exactly this reason (`inst/police_thief_p2p_Summary.md:2901`): "**TOML — For
private and local configuration only.** This format is written only in the private file
for each peer — `config/game.toml`: network port, choice of strategy models, language
mode, LLM settings, email, and group identity", while the shared JSON carries "the
agreed-upon match conditions". `:3001` adds that the private file is "local and **not
subject to negotiation**".

So a key from that list appearing in the negotiated object is not a harmless extra. It
either leaks how we play — the strategy selection is the whole graded contribution — or
it drags an unnegotiable local value into a document both sides must hold identically,
which turns a private edit into a rule 11 mismatch. Rule 39 (Prohibited) makes the
credential case explicit: "Do not push secrets and credentials to the repository…
Sanction: Severe security failure and project failure."

The classes below come from that passage rather than from imagination, one refusal per
class, which is what `M1-017c` asks for.
"""

from __future__ import annotations

import json
from collections.abc import Mapping

# Keyed by the class the book names, so a refusal can say *why* it refused.
PRIVATE_FIELD_CLASSES: dict[str, tuple[str, ...]] = {
    "network": ("port", "host", "url", "endpoint", "opponent_url", "mcp_server", "ngrok"),
    "strategy": ("strategy", "brain", "policy", "model_selection", "seed"),
    "llm": ("llm", "llm_model", "provider", "api_key", "openai_api_key", "temperature"),
    "language": ("language_mode", "verbal_mode", "banter"),
    "contact": ("email", "gmail", "report_to"),
    "credential": ("token", "secret", "credentials", "password", "private_key"),
}


# Match-config schema versions this build implements. **Deliberately not the artifact
# versions**: `reporting/declaration.SCHEMA_VERSION` is `1.1` and moves on its own
# schedule, so one global set would have this guard refuse our own declaration. `ADR-0003`
# records the schema version as unresolved across sources, and guessing at an unknown one
# is how a peer ends up verifying a document it does not understand.
SUPPORTED_CONFIG_SCHEMA_VERSIONS: frozenset[str] = frozenset({"1.2"})


class ConfigIntegrityError(ValueError):
    """Raised when a shared config is malformed or carries what it must not carry."""


def loads_no_duplicates(text: str) -> object:
    """Parse JSON, refusing any object that repeats a key (`M1-017b`).

    `object_pairs_hook` sees the pairs *before* the dict collapses them, which is the only
    point where the duplicate still exists. By the time you hold the dict it is gone.
    """

    def _reject(pairs: list[tuple[str, object]]) -> dict:
        seen: set[str] = set()
        for key, _ in pairs:
            if key in seen:
                raise ConfigIntegrityError(
                    f"duplicate key {key!r}: the document is not bit-for-bit reproducible [AE-11]"
                )
            seen.add(key)
        return dict(pairs)

    return json.loads(text, object_pairs_hook=_reject)


def private_fields_in(terms: Mapping[str, object]) -> list[str]:
    """Return `class:key` for every private-class key present in a shared config."""
    found = []
    for name in terms:
        lowered = str(name).lower()
        for class_name, markers in PRIVATE_FIELD_CLASSES.items():
            if any(marker == lowered or lowered.endswith(f"_{marker}") for marker in markers):
                found.append(f"{class_name}:{name}")
                break
    return sorted(found)


def check_no_private_fields(terms: Mapping[str, object]) -> None:
    """Refuse a shared config carrying a value the book assigns to the private file.

    Names the offending keys rather than refusing bare: rule 11's whole purpose is that
    both sides can converge on one document, and a refusal that does not say what to
    remove cannot be acted on.
    """
    leaked = private_fields_in(terms)
    if leaked:
        raise ConfigIntegrityError(
            "shared config carries private-file values (`config/game.toml`, "
            f"`:2901`): {', '.join(leaked)}"
        )


def check_config_schema_version(
    document: Mapping[str, object],
    supported: frozenset[str] = SUPPORTED_CONFIG_SCHEMA_VERSIONS,
) -> None:
    """Refuse a **match config** announcing a schema version this build does not implement.

    ``supported`` is a parameter because the artifacts version independently of the
    config; passing the wrong set is the bug this signature exists to make visible.

    An absent version is *not* an error — many negotiated term dictionaries carry none,
    and inventing a requirement the sources do not state would refuse the very template
    teams are meant to share.
    """
    announced = document.get("schema_version")
    if announced is None:
        return
    if announced not in supported:
        raise ConfigIntegrityError(
            f"unsupported schema_version {announced!r}; this build implements "
            f"{sorted(supported)} [ADR-0003]"
        )
