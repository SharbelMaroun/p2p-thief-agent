"""Simulator-conformant commit-reveal and canonical hashing.

Independently authored to match the reference simulator's `domain/crypto.py` and
`report/artifact_helpers.canonical_sha256`:

    commit = SHA256(canonical_json(payload) + "|" + nonce)
    canonical_json = json.dumps(sort_keys=True, ensure_ascii=False, separators=(",", ":"))

Verification re-hashes the revealed payload exactly as received, so it accepts any
opponent's committed field roster -- the payload field set is each peer's own choice and
never a cross-peer schema contract. The same canonical JSON hashes whole artifacts and
the agreed configuration, so every hash domain shares one serialization.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from typing import Any

# Crypto: nonce length in bytes for commit-reveal sealing (simulator constant).
NONCE_BYTES = 16


class CryptoError(ValueError):
    """Raised when a revealed (payload, nonce) does not reproduce its commitment."""


def canonical_json(value: Any) -> str:
    """Return stable JSON so hashing is key-order independent (simulator rule)."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def canonical_sha256(value: Any) -> str:
    """Return the lowercase SHA-256 hex digest of the canonical JSON of a value."""
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def new_nonce() -> str:
    """Return NONCE_BYTES CSPRNG bytes as lowercase hex (the book's token_hex(16))."""
    return secrets.token_hex(NONCE_BYTES)


def commit_of(payload: dict[str, Any], nonce: str) -> str:
    """Return SHA256(canonical_json(payload) + "|" + nonce)."""
    return hashlib.sha256(f"{canonical_json(payload)}|{nonce}".encode()).hexdigest()


def seal(payload: dict[str, Any]) -> dict[str, str]:
    """Generate a fresh nonce and the commit hash for a payload."""
    nonce = new_nonce()
    return {"nonce": nonce, "commit": commit_of(payload, nonce)}


def verify(payload: dict[str, Any], nonce: str, commit: str) -> None:
    """Raise CryptoError unless (payload, nonce) hashes to commit."""
    actual = commit_of(payload, nonce)
    if actual != commit:
        raise CryptoError(
            f"commit mismatch: expected {commit[:16]}..., recomputed {actual[:16]}..."
        )


def audit_records(records: list[dict]) -> dict:
    """Re-verify every {payload, nonce, commit} record and summarize the result.

    Returns {'passed', 'verified_steps', 'failed_steps'}; both peers run this over the
    opponent's revealed log and must agree for mutual consensus.
    """
    failed: list[int] = []
    for record in records:
        try:
            verify(record["payload"], record["nonce"], record["commit"])
        except CryptoError:
            failed.append(record["payload"].get("step", -1))
    return {
        "passed": not failed,
        "verified_steps": len(records) - len(failed),
        "failed_steps": failed,
    }
