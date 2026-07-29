"""Independent Node reproduction of every profile hash domain."""

import base64
import hashlib

from p2p_thief_agent.protocol.canonical import canonical_sha256, source_sha256
from p2p_thief_agent.protocol.commitment import audit_sha256, commitment_sha256
from tests.contract.conformance_fixtures import (
    NONCE_1,
    audit_record,
    make_payload,
    make_turn,
)
from tests.contract.neutral_helpers import node_result, session_context


def test_plain_sha256_and_source_domains() -> None:
    source = b'{"a":1}'
    encoded = base64.b64encode(source).decode()
    plain = node_result({"op": "sha256", "data_utf8": "abc"})
    game = node_result({
        "op": "source_hash", "logical_name": "game.json", "source_base64": encoded
    })
    rates = node_result({
        "op": "source_hash", "logical_name": "rate_limits.json", "source_base64": encoded
    })

    assert plain["sha256"] == hashlib.sha256(b"abc").hexdigest()
    assert game["sha256"] == source_sha256("game.json", source)
    assert rates["sha256"] == source_sha256("rate_limits.json", source)
    assert game["sha256"] != rates["sha256"]


def test_move_commitment_matches_simulator_construction() -> None:
    payload = make_payload()
    response = node_result({
        "op": "commitment_hash",
        "payload": payload,
        "nonce": NONCE_1,
        "context": session_context(),
    })

    assert response["sha256"] == commitment_sha256(payload, NONCE_1)
    assert response["sha256"] == "a26b45ff8012b59e29aa56cefe2de84e6cbde99dca5c92a9b4b5ffb3567d309c"


def test_named_cross_language_commitment_vector() -> None:
    payload = {
        "domain": "p2p-thief/move-commitment/v1",
        "game_id": "match-01",
        "game_uid": "match-01-sub-1",
        "sub_game_number": 1,
        "step": 1,
        "sender_group_id": "sharNamr",
        "role": "thief",
        "position": [3, 3],
        "move": "N",
        "intent": "lie",
        "hint": "Central Park",
        "barrier": None,
    }
    context = session_context()
    context["remote_group_id"] = "sharNamr"
    nonce = "000102030405060708090a0b0c0d0e0f"
    response = node_result({
        "op": "commitment_hash", "payload": payload, "nonce": nonce, "context": context
    })

    assert response["sha256"] == "349470332e9917b65f0ebe6dd23b63fadb18371ef5f790f50aed981a2a73cc3d"


def test_final_audit_and_idempotency_domains() -> None:
    message, payload, nonce = make_turn()
    records = [audit_record(message, payload, nonce)]
    context = session_context()
    audit = node_result({"op": "audit_hash", "records": records, "context": context})
    idempotency = node_result({"op": "idempotency_hash", "message": message})

    assert audit["sha256"] == audit_sha256(
        game_id=context["game_id"],
        game_uid=context["game_uid"],
        sub_game_number=context["sub_game_number"],
        sender_group_id=context["remote_group_id"],
        records=records,
    )
    assert idempotency["sha256"] == canonical_sha256({
        "domain": "p2p-thief/idempotency/v1",
        "message": message,
    })
