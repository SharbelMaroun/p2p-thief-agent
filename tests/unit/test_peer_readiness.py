"""`M9-040`: readiness must mean *served*, not merely *routable*.

**Found in a live match attempt on 2026-08-09, not by any test.** `serve_and_play` waits up to
`connect_timeout_seconds` for the opponent, probing with `port_answers` -- a TCP connect to
the host and port parsed out of the opponent's URL. Through a tunnel that host is a CDN edge
which accepts on 443 whether or not the opponent's process exists, so the probe returned
`True` immediately, the wait never ran, and the first `negotiate` came back `502 Bad Gateway`.

The probe was correct on localhost, where the only thing that can accept a connection is the
peer itself -- and every rehearsal was on localhost. That is why the suite was green.

The distinction the old probe protected still matters and is pinned below: "not up yet" must
stay separable from "up and refused the match", so only gateway statuses count as down.
"""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from p2p_thief_agent.adapters.serving import peer_answers, port_answers


def _server(status: int) -> tuple[HTTPServer, str]:
    """A local endpoint that answers every request with one status."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler's spelling
            self.send_response(status)
            self.end_headers()

        def log_message(self, *_args: object) -> None:
            return

    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}/mcp"


@pytest.mark.parametrize("status", [502, 503, 504])
def test_a_gateway_error_means_the_peer_is_not_up(status: int) -> None:
    """**The bug this module exists for.** A tunnel with no origin answers 502; the peer is
    not there, however routable its hostname is."""
    httpd, url = _server(status)
    try:
        assert peer_answers(url, timeout=5.0) is False
    finally:
        httpd.shutdown()


@pytest.mark.parametrize("status", [200, 400, 406])
def test_a_peer_that_answers_anything_else_is_up(status: int) -> None:
    """`406` is what an MCP endpoint returns to a bare GET, and it means **present**.

    Readiness asks only whether somebody is there. What that somebody thinks of the request
    -- or of the match -- is negotiation's business, and conflating the two is what the
    original TCP probe was written to avoid. That concern was right; its implementation was
    fooled by a CDN.
    """
    httpd, url = _server(status)
    try:
        assert peer_answers(url, timeout=5.0) is True
    finally:
        httpd.shutdown()


def test_an_unreachable_host_is_not_up() -> None:
    assert peer_answers("http://127.0.0.1:1/mcp", timeout=1.0) is False


def test_a_malformed_url_is_reported_rather_than_raised() -> None:
    """A readiness probe that raises turns "the opponent is late" into a crash."""
    assert peer_answers("not-a-url", timeout=1.0) is False


def test_the_tcp_probe_still_answers_for_a_local_port() -> None:
    """`port_answers` is kept: on localhost it is correct, cheaper, and used by tests."""
    httpd, _ = _server(200)
    try:
        assert port_answers("127.0.0.1", httpd.server_address[1], timeout=1.0) is True
    finally:
        httpd.shutdown()


def test_the_two_probes_disagree_exactly_where_the_bug_was() -> None:
    """The regression in one assertion: a served port that answers 502 is **not** ready.

    `port_answers` sees a listening socket and says yes -- which is what a CDN edge looks
    like in front of a dead tunnel. `peer_answers` asks and is told there is no origin.
    """
    httpd, url = _server(502)
    try:
        port = httpd.server_address[1]
        assert port_answers("127.0.0.1", port, timeout=1.0) is True
        assert peer_answers(url, timeout=5.0) is False
    finally:
        httpd.shutdown()
