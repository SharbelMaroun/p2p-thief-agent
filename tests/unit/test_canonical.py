"""RFC 8785 canonical JSON vectors and fail-closed input tests."""

import hashlib

import pytest

from p2p_thief_agent.protocol.canonical import (
    CanonicalizationError,
    agreed_configuration_sha256,
    canonical_sha256,
    canonicalize,
    loads,
    source_sha256,
)


def test_rfc_8785_canonicalization_vector() -> None:
    """Section 3.2 canonicalizes literals, numbers, escaping, and key order."""
    value = {
        "numbers": [333333333.33333329, 1e30, 4.50, 2e-3, 1e-27],
        "string": '€$\x0f\nA\'B"\\\\"/',
        "literals": [None, True, False],
    }
    expected = (
        b'{"literals":[null,true,false],"numbers":[333333333.3333333,'
        b'1e+30,4.5,0.002,1e-27],"string":"\xe2\x82\xac$\\u000f\\n'
        b'A\'B\\"\\\\\\\\\\"/"}'
    )

    assert canonicalize(value) == expected


def test_rfc_8785_utf16_property_sorting_vector() -> None:
    """Section 3.2.3 sorting uses unsigned UTF-16 code units, not code points."""
    value = {
        "€": "Euro Sign",
        "\r": "Carriage Return",
        "דּ": "Hebrew Letter Dalet With Dagesh",
        "1": "One",
        "😀": "Emoji: Grinning Face",
        "\x80": "Control",
        "ö": "Latin Small Letter O With Diaeresis",
    }

    assert list(loads(canonicalize(value)).values()) == [
        "Carriage Return",
        "One",
        "Control",
        "Latin Small Letter O With Diaeresis",
        "Euro Sign",
        "Emoji: Grinning Face",
        "Hebrew Letter Dalet With Dagesh",
    ]


def test_strings_use_exact_jcs_escaping_and_utf8() -> None:
    """Controls use lowercase escapes; slash and non-BMP Unicode stay unescaped."""
    value = '\x00\b\t\n\f\r\x1f"\\/😀'

    assert canonicalize(value) == b'"\\u0000\\b\\t\\n\\f\\r\\u001f\\"\\\\/\xf0\x9f\x98\x80"'


@pytest.mark.parametrize(
    "source",
    [
        '{"a":1,"a":2}',
        '{"x":9007199254740992}',
        '{"x":-9007199254740992}',
        '{"x":1e400}',
        '{"x":NaN}',
        '{"x":-0}',
        '"\\ud800"',
    ],
)
def test_loads_rejects_non_i_json(source: str) -> None:
    """Duplicate names, unsafe numbers, nonfinite values, and surrogates fail."""
    with pytest.raises(CanonicalizationError):
        loads(source)


@pytest.mark.parametrize(
    "value",
    [
        {1: "non-string key"},
        9007199254740992,
        -9007199254740992,
        float("nan"),
        float("inf"),
        "\udfff",
        ("arrays", "must", "be", "lists"),
    ],
)
def test_programmatic_non_i_json_values_are_rejected(value: object) -> None:
    """Programmatic values receive the same validation as parsed input."""
    with pytest.raises((CanonicalizationError, TypeError)):
        canonicalize(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "call",
    [
        lambda: canonicalize({"\ud800": 0}),
        lambda: source_sha256("other.json", b""),
        lambda: source_sha256("game.json", ""),  # type: ignore[arg-type]
        lambda: agreed_configuration_sha256([], {}),  # type: ignore[arg-type]
        lambda: loads(1),  # type: ignore[arg-type]
    ],
)
def test_boundary_helpers_reject_wrong_domains_and_types(call) -> None:
    """Hash domains and strict loading reject ambiguous inputs."""
    with pytest.raises((CanonicalizationError, TypeError)):
        call()


def test_nested_objects_sort_without_reordering_arrays() -> None:
    """Object sorting is recursive while array order remains unchanged."""
    assert canonicalize({"z": [{"b": 1, "a": 2}, 0], "a": "first"}) == (
        b'{"a":"first","z":[{"a":2,"b":1},0]}'
    )


def test_loads_accepts_utf8_and_digest_hashes_canonical_bytes() -> None:
    """Byte input is UTF-8 only and the digest is over canonical output."""
    first = loads(b'{"z":"\xe2\x82\xac","a":1}')
    second = loads(' { "a" : 1, "z" : "€" } ')

    assert first == second
    assert canonical_sha256(first) == canonical_sha256(second)
    source = b'{"z":1}\r\n'
    expected = hashlib.sha256(b"p2p-thief/config-source/game.json/v1|" + source).hexdigest()
    assert source_sha256("game.json", source) == expected
    assert agreed_configuration_sha256({"a": 1}, {"b": 2}) == canonical_sha256(
        {"domain": "p2p-thief/agreed-config/v1", "game": {"a": 1}, "rate_limits": {"b": 2}}
    )
    with pytest.raises(CanonicalizationError):
        loads(b'"\xff"')
