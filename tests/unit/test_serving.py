"""M5-019e: hosting the mailbox -- bind address, daemon thread, port pre-check.

The bind-address test is the one that matters. The reference binds `127.0.0.1`
because it runs both peers on one machine; the book mandates `0.0.0.0` so a tunnel can
reach us, and rule 10 sanctions failure to tunnel with "Inability to compete against
opponents". Copying the reference would pass every local check and be invisible at the
stage-5 rehearsal, so the default is pinned here rather than left to whoever edits the
call next `[ADR-0009]`.
"""

import socket
import threading

import pytest

from p2p_thief_agent.adapters import PeerInboxes
from p2p_thief_agent.adapters.serving import (
    DEFAULT_BIND_HOST,
    ServingError,
    ensure_port_free,
    port_answers,
    serve_in_background,
)


def a_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def test_the_default_bind_host_is_every_interface_not_loopback() -> None:
    """Book `:657` and rule 10 `:3326`; the reference's 127.0.0.1 is single-machine only.

    Pinned as a test because it is a one-word change that no local test would ever
    catch -- it fails only on a second machine, through a tunnel.
    """
    assert DEFAULT_BIND_HOST == "0.0.0.0"  # noqa: S104 - required by [AE-10]


def test_a_free_port_passes_the_pre_check() -> None:
    ensure_port_free("127.0.0.1", a_free_port())


def test_a_taken_port_fails_loudly_at_launch() -> None:
    """A stale peer holding the port must not yield a server that never binds.

    Without this the game loop would wait for messages that cannot arrive -- a hang
    whose cause is invisible.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as held:
        held.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        held.bind(("127.0.0.1", 0))
        held.listen(1)
        port = held.getsockname()[1]
        with pytest.raises(ServingError, match="cannot host the Thief mailbox"):
            ensure_port_free("127.0.0.1", port)


def test_the_error_names_the_likely_cause_and_the_key_to_change() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as held:
        held.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        held.bind(("127.0.0.1", 0))
        held.listen(1)
        with pytest.raises(ServingError) as caught:
            ensure_port_free("127.0.0.1", held.getsockname()[1])
    assert "my_port" in str(caught.value)


def test_port_answers_is_false_for_a_closed_port() -> None:
    """The readiness probe's concrete half: nothing listening means not up yet."""
    assert port_answers("127.0.0.1", a_free_port(), timeout=0.5) is False


def test_port_answers_is_true_once_something_listens() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as live:
        live.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        live.bind(("127.0.0.1", 0))
        live.listen(1)
        assert port_answers("127.0.0.1", live.getsockname()[1], timeout=1.0) is True


def test_the_server_thread_is_a_daemon_so_it_cannot_outlive_the_game() -> None:
    """A lingering mailbox would turn a finished match into a hang.

    Bound to loopback here on purpose: the production default is `0.0.0.0`, but a
    test must not open a port to the network to prove the thread is a daemon.
    """
    thread = serve_in_background(PeerInboxes(), port=a_free_port(), host="127.0.0.1")
    assert isinstance(thread, threading.Thread)
    assert thread.daemon is True


def test_the_thread_is_named_so_a_stuck_peer_is_identifiable() -> None:
    thread = serve_in_background(
        PeerInboxes(), port=a_free_port(), host="127.0.0.1", name="p2p-thief"
    )
    assert "p2p-thief" in thread.name
