"""`M5-002e` / `M5-006`: the book's stage-2 milestone, over a real socket.

Book p. 105 asks that a message sent by peer A on localhost be **received
correctly** by peer B. Every other transport test here runs both halves inside
one interpreter, which proves the call shapes but cannot prove process
separation (`AE-1`, `AE-2`) or that anything ever crossed a socket.

This test starts a genuinely separate OS process, sends to it over HTTP, and
reads the transcript that process wrote.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

from p2p_thief_agent.adapters import FastMCPClient, TransportError
from p2p_thief_agent.protocol.crypto import seal

ROOT = Path(__file__).resolve().parents[2]
SERVER = Path(__file__).with_name("localhost_peer.py")
BOOT_TIMEOUT = 60.0

TURN = {"step": 1, "sender": "police", "hint": "near the park",
        "smell_grid": {"3,3": 0.9}, "commit": "a" * 64, "timestamp": "t"}


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _await_ready(client: FastMCPClient, process: subprocess.Popen) -> None:
    """Poll until the peer answers, failing fast if the process died."""
    deadline = time.monotonic() + BOOT_TIMEOUT
    while time.monotonic() < deadline:
        if process.poll() is not None:
            pytest.fail(f"peer process exited early with {process.returncode}")
        try:
            client.receive_control({"kind": "status", "sender": "police"})
            return
        except TransportError:
            time.sleep(0.4)
    pytest.fail(f"peer process was not reachable within {BOOT_TIMEOUT}s")


@pytest.fixture
def remote_peer(tmp_path: Path):
    """Start the peer in its own OS process and yield (client, transcript, pid)."""
    port = _free_port()
    transcript = tmp_path / "transcript.jsonl"
    process = subprocess.Popen(
        [sys.executable, str(SERVER), "--port", str(port), "--transcript", str(transcript)],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    client = FastMCPClient(f"http://127.0.0.1:{port}/mcp", timeout=30.0)
    try:
        _await_ready(client, process)
        yield client, transcript, process.pid
    finally:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()


def _entries(transcript: Path) -> list[dict]:
    text = transcript.read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def test_a_turn_crosses_a_real_socket_into_a_separate_process(remote_peer) -> None:
    """The stage-2 milestone: A sends on localhost, B receives it correctly."""
    client, transcript, peer_pid = remote_peer

    assert client.receive_turn(TURN) == {"ok": True}

    accepted = [e for e in _entries(transcript) if e["tool"] == "receive_turn"]
    assert accepted and accepted[0]["accepted"] is True

    # Validated by an interpreter that is not this one -- the point of AE-1/AE-2.
    # The handling PID is not asserted equal to the spawned PID: the HTTP server
    # serves requests from a worker process, so it is a descendant rather than
    # the child we started. "Not us" is the property that matters.
    assert peer_pid != os.getpid()
    assert accepted[0]["pid"] != os.getpid()


def test_a_tampered_audit_survives_the_socket_and_is_scored(remote_peer) -> None:
    """Rule 19 requires a decided loss to arrive, not to vanish as a network error."""
    client, transcript, _ = remote_peer

    payload = {"step": 1, "move": "MOVE:N"}
    sealed = seal(payload)
    audit = {
        "sender": "police",
        "records": [
            {"payload": {"step": 1, "move": "MOVE:S"},  # mutated after sealing
             "nonce": sealed["nonce"], "commit": sealed["commit"]}
        ],
        "result_claim": "survival",
    }
    assert client.submit_audit(audit) == {"ok": True}

    audits = [e for e in _entries(transcript) if e["tool"] == "submit_audit"]
    assert audits and audits[0]["accepted"] is False
    assert "audit failed" in audits[0]["reason"]


def test_an_unstarted_port_is_a_transport_error_not_a_hang() -> None:
    """A peer that was never started must fail fast, never wait forever."""
    client = FastMCPClient(f"http://127.0.0.1:{_free_port()}/mcp", timeout=10.0)
    with pytest.raises(TransportError):
        client.receive_turn(TURN)
