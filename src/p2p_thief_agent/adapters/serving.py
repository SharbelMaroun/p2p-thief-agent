"""Host this peer's mailbox on a background thread, reachable through a tunnel (M5-019e).

``FastMCP.run`` blocks forever, so a peer that both serves and plays must put one of
them on another thread. The reference threads the *server* and keeps the game loop in
the main thread; this module does the same `[ADR-0009]`.

**`daemon=True` is load-bearing.** The mailbox must never keep the process alive after
the game ends. The game loop decides when to exit, and a lingering server thread would
turn a finished match into a hang -- the exact failure the watchdog exists to catch,
reintroduced one level up.

**The bind host defaults to ``0.0.0.0``, and that is the whole point.** The book is
explicit: ``mcp.run(transport="http", host="0.0.0.0", port=8000)`` with the comment
"Bind the server so a tunnel can expose it publicly"
(`police_thief_p2p_Summary.md:657`), and rule 10 makes tunnelling **mandatory** with
the sanction "Inability to compete against opponents" (`:3326`). The **reference binds
``127.0.0.1``** because it runs both peers on one machine -- single-machine
convenience, not the requirement, and the book outranks the simulator. Binding
loopback here would produce a peer that passes every local check and is invisible
through the tunnel, failing only at the stage-5 rehearsal and looking like a network
fault. Localhost is "permitted only during the early development stages" (`:673`).

This module and the two FastMCP client/server modules are the only places ``fastmcp``
is imported, so the transport-neutral core stays testable without a socket.
"""

from __future__ import annotations

import socket
import threading
import urllib.error
import urllib.request

from p2p_thief_agent.adapters.fastmcp_server import PeerInboxes, build_server

# Bind on every interface so a tunnel (ngrok/Localtonet/self-hosted) can reach us
# `[AE-10]`. Overridable so tests can hold a loopback port without the production
# default depending on what a test happened to choose.
DEFAULT_BIND_HOST = "0.0.0.0"  # noqa: S104 - required by [AE-10]; see module docstring


class ServingError(RuntimeError):
    """Raised when this peer's mailbox cannot be hosted."""


def ensure_port_free(host: str, port: int) -> None:
    """Fail loudly now if the port is taken, rather than quietly later.

    A stale peer still holding the port would otherwise produce a server thread that
    never binds while the game loop waits for messages that cannot arrive -- a hang
    whose cause is invisible. The reference runs the same pre-check before starting
    its thread.
    """
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Deliberately NOT SO_REUSEADDR. The first version set it out of habit and
        # the check silently never fired: on Windows that option lets a socket bind
        # a port another process already holds, which is exactly the condition this
        # function exists to detect. A detection probe wants the strictest bind
        # available, not the most permissive one.
        probe.bind((host, port))
    except OSError as exc:
        raise ServingError(
            f"cannot host the Thief mailbox on {host}:{port}: {exc}. "
            "Another peer may still be running; stop it or choose a different "
            "[network].my_port"
        ) from exc
    finally:
        probe.close()


def serve_in_background(
    inboxes: PeerInboxes,
    *,
    port: int,
    host: str = DEFAULT_BIND_HOST,
    name: str = "p2p-thief",
) -> threading.Thread:
    """Start the four-tool mailbox on a daemon thread and return it.

    The thread is returned rather than joined: the caller owns the process lifetime,
    and this function's job ends once the mailbox is accepting. Readiness of the
    *opponent* is a separate concern (:mod:`p2p_thief_agent.services.readiness`).
    """
    ensure_port_free(host, port)
    server = build_server(inboxes, name)
    thread = threading.Thread(
        target=lambda: server.run(transport="http", host=host, port=port),
        daemon=True,
        name=f"mcp-{name}",
    )
    thread.start()
    return thread


def port_answers(host: str, port: int, timeout: float = 1.0) -> bool:
    """Return whether something is listening -- the readiness probe's concrete half.

    Deliberately a TCP connect rather than an MCP call: at startup we only need to
    know the opponent's process exists. Asking it a protocol question before
    negotiation has begun would conflate "not up yet" with "refused the match", and
    those must stay distinguishable.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


# Gateway statuses meaning "the tunnel is routable but nothing is serving behind it".
# A peer that answers *anything* else -- including 406, which is what an MCP endpoint
# returns to a bare GET -- is up, whatever it thinks of the request.
# 530 added 2026-08-12: Cloudflare returns it (body "error code: 1033") when the hostname
# exists but NO tunnel is registered for it -- the opponent's route is not up. Without it,
# dialling a 530 endpoint passed readiness on the first probe and failed inside negotiate
# seconds later, instead of the readiness loop waiting out its budget. Same "no origin"
# condition as 502, one layer up.
_NO_ORIGIN = frozenset({502, 503, 504, 530})


def peer_answers(url: str, timeout: float = 2.0) -> bool:
    """Return whether the opponent's endpoint is actually **served**, not merely routable.

    **`port_answers` cannot answer this through a tunnel, and that cost us a match.**
    A TCP connect to `<name>.trycloudflare.com:443` succeeds against the CDN edge whether
    or not the peer's process exists, so the readiness wait passed instantly and the first
    `negotiate` came back `502 Bad Gateway`. The probe was right on localhost -- where the
    only thing that can accept a connection is the peer itself -- and every rehearsal was
    on localhost.

    The distinction the TCP probe was protecting still holds: "not up yet" must stay
    separable from "up and refused the match". That is why only the gateway statuses count
    as down. A peer that replies `406`, `200` or `400` is present, and whatever it says
    about the match is negotiation's business, not readiness's.
    """
    try:
        # Built inside the try: an unparseable URL raises from the constructor, and a
        # readiness probe that raises turns "the opponent is late" into a crash.
        # A User-Agent is not optional. Cloudflare answers urllib's default agent with a
        # 403 (bot protection), not the true 502/530, so readiness read every tunnelled peer
        # as "up" and never waited -- the 8s failure on game 2 (2026-08-12).
        request = urllib.request.Request(
            url, method="GET", headers={"User-Agent": "p2p-thief/1.0 (readiness probe)"})
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return response.status not in _NO_ORIGIN
    except urllib.error.HTTPError as exc:
        return exc.code not in _NO_ORIGIN
    except (urllib.error.URLError, OSError, ValueError):
        return False
