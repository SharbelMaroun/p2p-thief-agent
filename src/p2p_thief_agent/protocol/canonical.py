"""RFC 8785 JSON Canonicalization Scheme (JCS) for I-JSON values."""

from __future__ import annotations

import hashlib
import json
import math

JSONValue = None | bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"]
MAX_SAFE_INTEGER = 2**53 - 1
_SHORT_ESCAPES = {8: r"\b", 9: r"\t", 10: r"\n", 12: r"\f", 13: r"\r"}
_SOURCE_NAMES = {"game.json", "rate_limits.json"}


class CanonicalizationError(ValueError):
    """Raised when input cannot be represented as RFC 8785 canonical JSON."""


def _quote(value: str) -> str:
    chunks = ['"']
    for character in value:
        codepoint = ord(character)
        if 0xD800 <= codepoint <= 0xDFFF:
            raise CanonicalizationError("JSON strings must not contain lone surrogates")
        if codepoint in _SHORT_ESCAPES:
            chunks.append(_SHORT_ESCAPES[codepoint])
        elif codepoint < 0x20:
            chunks.append(f"\\u{codepoint:04x}")
        elif character in {'"', "\\"}:
            chunks.append("\\" + character)
        else:
            chunks.append(character)
    chunks.append('"')
    return "".join(chunks)


def _utf16_key(value: str) -> bytes:
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise CanonicalizationError("JSON property names must be valid Unicode")
    return value.encode("utf-16-be")


def _float_text(value: float) -> str:
    value = float(value)
    if not math.isfinite(value):
        raise CanonicalizationError("NaN and infinity are not valid JSON numbers")
    if value == 0:
        return "0"
    text = repr(value).lower()
    if "e" not in text:
        return text.removesuffix(".0")
    mantissa, exponent_text = text.split("e")
    exponent = int(exponent_text)
    sign = "-" if mantissa.startswith("-") else ""
    mantissa = mantissa.removeprefix("-")
    digits = mantissa.replace(".", "")
    decimal_point = exponent + 1
    if 0 < decimal_point <= 21:
        body = (
            digits + "0" * (decimal_point - len(digits))
            if decimal_point >= len(digits)
            else digits[:decimal_point] + "." + digits[decimal_point:]
        )
    elif -6 < decimal_point <= 0:
        body = "0." + "0" * -decimal_point + digits
    else:
        fraction = "." + digits[1:] if len(digits) > 1 else ""
        exponent_sign = "+" if exponent >= 0 else ""
        body = f"{digits[0]}{fraction}e{exponent_sign}{exponent}"
    return sign + body


def _serialize(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return _quote(value)
    if isinstance(value, int):
        return str(_safe_integer(value))
    if isinstance(value, float):
        return _float_text(value)
    if not isinstance(value, (list, dict)):
        raise TypeError(f"{type(value).__name__} is not a JSON-compatible type")
    if isinstance(value, list):
        return "[" + ",".join(_serialize(item) for item in value) + "]"
    if any(not isinstance(key, str) for key in value):
        raise CanonicalizationError("JSON object property names must be strings")
    keys = sorted(value, key=_utf16_key)
    members = (_quote(key) + ":" + _serialize(value[key]) for key in keys)
    return "{" + ",".join(members) + "}"


def canonicalize(value: JSONValue) -> bytes:
    """Return the RFC 8785 canonical UTF-8 representation of ``value``."""
    return _serialize(value).encode("utf-8")


def canonical_sha256(value: JSONValue) -> str:
    """Return the lowercase SHA-256 hex digest of canonical JSON bytes."""
    return hashlib.sha256(canonicalize(value)).hexdigest()


def source_sha256(logical_name: str, source: bytes) -> str:
    """Hash exact config source bytes in their versioned source domain."""
    if logical_name not in _SOURCE_NAMES:
        raise CanonicalizationError(f"unsupported config source name: {logical_name!r}")
    if not isinstance(source, bytes):
        raise TypeError("config source must be bytes")
    prefix = f"p2p-thief/config-source/{logical_name}/v1|".encode("ascii")
    return hashlib.sha256(prefix + source).hexdigest()


def agreed_configuration_sha256(
    game: dict[str, JSONValue], rate_limits: dict[str, JSONValue]
) -> str:
    """Hash the two parsed config objects in the agreed-config domain."""
    if not isinstance(game, dict) or not isinstance(rate_limits, dict):
        raise CanonicalizationError("game and rate_limits must be JSON objects")
    return canonical_sha256(
        {"domain": "p2p-thief/agreed-config/v1", "game": game, "rate_limits": rate_limits}
    )


def _object_without_duplicates(pairs: list[tuple[str, JSONValue]]) -> dict[str, JSONValue]:
    result: dict[str, JSONValue] = {}
    for key, value in pairs:
        if key in result:
            raise CanonicalizationError(f"duplicate JSON property name: {key!r}")
        result[key] = value
    return result


def _safe_integer(value: int) -> int:
    if not -MAX_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER:
        raise CanonicalizationError("integer exceeds the IEEE-754 safe integer range")
    return value


def loads(source: str | bytes | bytearray) -> JSONValue:
    """Decode one UTF-8 I-JSON value, rejecting duplicate names and unsafe numbers."""
    if isinstance(source, (bytes, bytearray)):
        try:
            source = bytes(source).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CanonicalizationError("JSON input bytes must be UTF-8") from exc
    elif not isinstance(source, str):
        raise TypeError("JSON input must be str, bytes, or bytearray")
    value = json.loads(
        source,
        object_pairs_hook=_object_without_duplicates,
        parse_int=_parse_integer,
    )
    canonicalize(value)
    return value


def _parse_integer(source: str) -> int:
    if source == "-0":
        raise CanonicalizationError("negative zero is not a valid profile integer")
    return _safe_integer(int(source))
