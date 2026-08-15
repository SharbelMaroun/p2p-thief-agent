"""A reusable MCP session: one connection held across many calls (companion `C-049`).

Split out of `fastmcp_client` at a real seam rather than to satisfy the line counter.
Owning a connection's lifetime — open lazily, reuse, discard on fault, close at
settlement — is a different job from shaping the four Option-B tool arguments, and only
this half needs to reason about event loops at all.

**Why the loop is held too.** A live MCP session cannot span event loops, and the old
per-call design used a fresh `asyncio.run()` each time, which is precisely why it could
not keep a connection. Holding the session therefore means holding its loop; both are
created on first use, so constructing one costs nothing and touches no network.

**A broken session is discarded, never reused.** Any fault clears both, so the next call
reconnects — which is what makes the caller's bounded re-send meaningful: a retry that
re-used the connection that just failed would retry the failure.
"""

from __future__ import annotations

import asyncio
import contextlib

from fastmcp import Client


class ReusableSession:
    """One MCP connection, opened on demand and reused until it faults or is closed."""

    __slots__ = ("_target", "_loop", "_client")

    def __init__(self, target: object) -> None:
        self._target = target
        self._loop: asyncio.AbstractEventLoop | None = None
        self._client: object | None = None

    @property
    def live(self) -> bool:
        """Whether a session is currently open (the drop-on-fault tests read this)."""
        return self._client is not None

    def call(self, tool: str, arguments: dict, timeout: float | None = None) -> object:
        """Invoke one tool on the live session, discarding it if the call faults."""
        try:
            loop, client = self._open()
            request = client.call_tool(tool, arguments)  # type: ignore[attr-defined]
            if timeout is not None:
                request = asyncio.wait_for(request, timeout)
            return loop.run_until_complete(request)
        except BaseException:
            # Discard before propagating: the fault may have left the connection
            # half-open, and the caller's retry must get a fresh one.
            self.close()
            raise

    def close(self) -> None:
        """Tear the session and its loop down. Safe to call repeatedly.

        Shutdown faults are suppressed on purpose: this runs on the failure path, and a
        failure *while closing* an already-broken session carries no new information —
        reporting it would replace the original cause with its aftermath.
        """
        client, loop = self._client, self._loop
        self._client = self._loop = None
        if client is not None and loop is not None:
            with contextlib.suppress(Exception):
                loop.run_until_complete(client.__aexit__(None, None, None))  # type: ignore[attr-defined]
        if loop is not None:
            with contextlib.suppress(Exception):
                loop.close()

    def _open(self) -> tuple[asyncio.AbstractEventLoop, object]:
        """Return the live (loop, client), creating either if it is missing."""
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
        if self._client is None:
            client = Client(self._target)
            self._loop.run_until_complete(client.__aenter__())  # type: ignore[attr-defined]
            self._client = client
        return self._loop, self._client
