"""Canonicalization vectors (`M4-002a`/`M4-002b`, `M1-014a`/`b`/`c`).

`STAGE_C_ACCEPTANCE.md` flagged that `ensure_ascii=False` rested on reading the
simulator source, because every reference record is pure ASCII and so no vector
discriminated it. These vectors close that gap: they pin the exact canonical bytes for
escaping, control characters, and non-BMP codepoints, and they separate the hash
domains. If canonical serialization ever drifts, every commitment and config hash
diverges and no opponent can audit this peer — so the bytes are pinned here, not assumed.
"""

from p2p_thief_agent.protocol.crypto import (
    canonical_json,
    canonical_sha256,
    commit_of,
    seal,
    verify,
)

NONCE = "000102030405060708090a0b0c0d0e0f"


def test_object_keys_sort_but_array_order_and_number_forms_hold() -> None:
    """Keys sort; array order is preserved; floats render as the reference does."""
    a = {"b": [3, 2, {"z": 1, "a": 2}], "a": 6.0, "n": 31.8}
    b = {"n": 31.8, "a": 6.0, "b": [3, 2, {"a": 2, "z": 1}]}
    assert canonical_json(a) == canonical_json(b), "hashing is key-order independent"
    assert canonical_json(a) == '{"a":6.0,"b":[3,2,{"a":2,"z":1}],"n":31.8}'


def test_escapes_quotes_backslashes_and_control_characters() -> None:
    """Quotes, backslashes, newline, and a raw control char escape byte-exactly.

    The expected bytes are built from parts so no fragile mega-literal hides a drift:
    a quote becomes ``\\"``, a backslash ``\\\\``, a newline ``\\n``, and U+0001
    ``\\u0001`` — with ``ensure_ascii=False`` the low control char is still escaped.
    """
    value = {"s": 'a"b\\c\n\x01'}
    q, bs = chr(92) + '"', chr(92) + chr(92)
    nl, ctrl = chr(92) + "n", chr(92) + "u0001"
    assert canonical_json(value) == '{"s":"a' + q + "b" + bs + "c" + nl + ctrl + '"}'


def test_non_ascii_and_non_bmp_serialize_raw_not_escaped() -> None:
    """`ensure_ascii=False`: é and a non-BMP emoji stay raw UTF-8, never `\\uXXXX`."""
    out = canonical_json({"hint": "café \U0001F600"})
    assert out == '{"hint":"café \U0001F600"}'
    assert chr(92) + "u" not in out, "non-ASCII is raw UTF-8, not ASCII-escaped"


def test_a_non_bmp_payload_commits_and_verifies_end_to_end() -> None:
    """The whole seal/verify pipeline is byte-stable through a non-BMP payload."""
    payload = {"hint": "meet at the \U0001F309", "move": "N"}
    sealed = seal(payload)
    verify(payload, sealed["nonce"], sealed["commit"])


def test_commitment_and_config_hash_domains_do_not_collide() -> None:
    """`M4-002b`: the per-turn commitment and a bare config hash of the same value differ.

    The commitment binds a nonce behind a ``|`` separator, so it can never equal the
    plain canonical hash of the payload — the two hash domains cannot collide.
    """
    payload = {"step": 1, "move": "N"}
    assert commit_of(payload, NONCE) != canonical_sha256(payload)
