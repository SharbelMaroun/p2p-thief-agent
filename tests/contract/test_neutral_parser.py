"""Raw-byte I-JSON and resource-limit evidence from the independent process."""

import base64

import pytest

from tests.contract.neutral_helpers import node_raw, node_result, offer, offer_context


@pytest.mark.parametrize(
    "raw",
    [
        b'{"op":"sha256","data_utf8":"a","data_utf8":"b"}',
        b"\xef\xbb\xbf" + b'{"op":"sha256","data_utf8":"a"}',
        b'{"op":"sha256","data_utf8":"\\ud800"}',
        b'{"op":"sha256","data_utf8":"a","integer":9007199254740992}',
    ],
)
def test_duplicate_bom_surrogate_and_unsafe_integer_reject(raw: bytes) -> None:
    result = node_raw(raw)

    assert result["ok"] is False
    assert result["rejection"]["error"]["code"] == "MALFORMED"


def test_invalid_utf8_is_not_replaced() -> None:
    raw = b'{"op":"sha256","data_utf8":"' + bytes([0xFF]) + b'"}'

    assert node_raw(raw)["rejection"]["error"]["code"] == "MALFORMED"


def test_unsafe_integer_in_canonical_config_source_rejects() -> None:
    source = b'{"x":9007199254740992}'
    result = node_result({
        "op": "source_hash",
        "logical_name": "game.json",
        "source_base64": base64.b64encode(source).decode(),
    })

    assert result["rejection"]["error"]["code"] == "MALFORMED"


@pytest.mark.parametrize("limit", ["bytes", "depth"])
def test_offer_limits_reject_before_schema(limit: str) -> None:
    proposed = offer("alpha", "beta", "limited-game")
    if limit == "bytes":
        proposed["step_zero"]["os"] = "x" * 66_000
    else:
        nested: object = 0
        for _ in range(65):
            nested = [nested]
        proposed["extension"] = nested
    result = node_result({
        "op": "accept_offer",
        "offer": proposed,
        "context": offer_context(proposed),
    })

    assert result["rejection"]["error"]["code"] == "MALFORMED"


def test_raw_command_rejection_has_null_acknowledgement() -> None:
    result = node_raw(b"{not-json")

    assert result["rejection"]["status"] == "rejected"
    assert result["rejection"]["acknowledges"] is None
    assert set(result["rejection"]) == {"status", "acknowledges", "error"}
