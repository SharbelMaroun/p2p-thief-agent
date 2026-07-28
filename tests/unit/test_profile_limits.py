"""Canonical wire size, depth, cycle, and JSON-domain limits."""

import pytest

from p2p_thief_agent.protocol.profile import (
    ConformanceError,
    rejection,
    require_limits,
)


def nested_containers(depth: int) -> object:
    value: object = None
    for _ in range(depth):
        value = [value]
    return value


def test_root_container_has_depth_one() -> None:
    require_limits(nested_containers(64), 1_000, 64)


def test_container_depth_above_limit_is_malformed() -> None:
    with pytest.raises(ConformanceError) as captured:
        require_limits(nested_containers(65), 1_000, 64)

    assert captured.value.code == "MALFORMED"


def test_canonical_utf8_byte_limit_is_enforced() -> None:
    with pytest.raises(ConformanceError) as captured:
        require_limits({"value": "😀"}, 12)

    assert captured.value.code == "MALFORMED"


def test_non_json_value_is_malformed() -> None:
    with pytest.raises(ConformanceError) as captured:
        require_limits({"value": {1, 2}}, 1_000)

    assert captured.value.code == "MALFORMED"


def test_cycles_are_malformed() -> None:
    value: list[object] = []
    value.append(value)

    with pytest.raises(ConformanceError) as captured:
        require_limits(value, 1_000)

    assert captured.value.code == "MALFORMED"


@pytest.mark.parametrize("message_id", [None, 1, "x" * 32, "a" * 31])
def test_rejection_only_acknowledges_a_valid_message_id(message_id: object) -> None:
    result = rejection(message_id, ConformanceError("MALFORMED", "bad request"))

    assert result["acknowledges"] is None


def test_rejection_acknowledges_valid_message_id() -> None:
    result = rejection("a" * 32, ConformanceError("MALFORMED", "bad request"))

    assert result["acknowledges"] == "a" * 32
