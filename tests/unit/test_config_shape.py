"""`M1-017b`: a shared config whose *shape* is wrong, and one announcing a version we
do not implement.

`test_appendix_f.py` covers `M1-017a` by inspecting values; `test_config_privacy.py`
covers `M1-017c` by inspecting membership. This file inspects the document itself.

Appendix E rule 11 (Mandatory) requires the configuration to be "identical, bit-for-bit,
on both sides", sanction "disqualification of the game due to lack of symmetry". A
repeated key defeats that silently, because Python resolves the collision and forgets it
before any of our code sees the object.
"""


from __future__ import annotations

import json

import pytest

from p2p_thief_agent.protocol.config_integrity import (
    SUPPORTED_CONFIG_SCHEMA_VERSIONS,
    ConfigIntegrityError,
    check_config_schema_version,
    loads_no_duplicates,
)

GOOD = {
    "board_size": 7, "smell_grid_size": 5, "decay_per_step": 0.1, "emit_intensity": 0.9,
    "max_steps": 35, "barriers_max": 14, "thief_start": [0, 0], "cop_start": [6, 6],
}


# --- M1-017b: duplicate keys ---------------------------------------------------------


def test_python_silently_keeps_the_last_duplicate_which_is_why_this_guard_exists() -> None:
    """The hazard, stated as a fact about the platform rather than a worry.

    Nothing raises. The collision is resolved and forgotten before any of our code sees
    the object, so a check that inspects the parsed dict can never find it.
    """
    assert json.loads('{"board_size": 7, "board_size": 99}') == {"board_size": 99}


def test_a_duplicate_key_is_refused_and_named() -> None:
    with pytest.raises(ConfigIntegrityError, match="duplicate key 'board_size'"):
        loads_no_duplicates('{"board_size": 7, "board_size": 99}')


def test_a_duplicate_nested_deeper_in_the_document_is_still_refused() -> None:
    """A repeat inside a nested object breaks reproducibility exactly as badly."""
    with pytest.raises(ConfigIntegrityError, match="duplicate key 'r'"):
        loads_no_duplicates('{"terms": {"grid": {"r": 1, "r": 2}}}')


def test_the_same_key_in_two_different_objects_is_not_a_duplicate() -> None:
    """`{"a": {"x": 1}, "b": {"x": 2}}` repeats nothing — the guard must not overreach."""
    assert loads_no_duplicates('{"a": {"x": 1}, "b": {"x": 2}}') == {"a": {"x": 1}, "b": {"x": 2}}


def test_an_ordinary_config_parses_unchanged() -> None:
    """The guard is a filter, not a transform: identical output to `json.loads`."""
    text = json.dumps(GOOD)
    assert loads_no_duplicates(text) == json.loads(text)


def test_duplicate_keys_would_have_changed_the_agreed_hash() -> None:
    """Why rule 11 is the right citation: the two readings are different documents, so
    they hash differently, and a signature over one would verify the other's contents."""
    from p2p_thief_agent.protocol.crypto import canonical_sha256

    first, second = json.loads('{"a": 1, "a": 2}'), {"a": 1}
    assert canonical_sha256(first) != canonical_sha256(second)


# --- M1-017b, second half: unsupported versions --------------------------------------


def test_an_unsupported_config_schema_version_is_refused() -> None:
    with pytest.raises(ConfigIntegrityError, match="unsupported schema_version '9.9'"):
        check_config_schema_version({**GOOD, "schema_version": "9.9"})


def test_the_negotiated_version_is_accepted_and_an_absent_one_is_not_an_error() -> None:
    """Term dictionaries routinely carry no version. Refusing those would refuse the very
    template teams are meant to share."""
    check_config_schema_version({**GOOD, "schema_version": "1.2"})
    check_config_schema_version(GOOD)


def test_the_artifact_versions_are_a_separate_space_and_are_not_refused() -> None:
    """Caught while writing this: `reporting/declaration.SCHEMA_VERSION` is `1.1` while
    the match config is `1.2`. A single global set would have made this guard refuse our
    own declaration artifact, so the supported set is a parameter."""
    from p2p_thief_agent.reporting.declaration import SCHEMA_VERSION

    assert SCHEMA_VERSION not in SUPPORTED_CONFIG_SCHEMA_VERSIONS
    check_config_schema_version({"schema_version": SCHEMA_VERSION}, frozenset({SCHEMA_VERSION}))
