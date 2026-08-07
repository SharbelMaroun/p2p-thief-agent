"""`M8-004b` / `M8-010`: nothing grows without bound, and shutdown releases what it took.

Appendix F table 19 sets `queue_depth` to **100, status Minimum** — "may be raised by
agreement but never lowered". Unbounded is not "raised": a mailbox with no ceiling is one a
flood drives out of memory, and an out-of-memory kill is a technical loss scored 0/0 under
Table 2. Rule 29 (Mandatory) requires DOS detectors "to protect network resources", and
rule 6 makes a freeze while awaiting a response a "system deadlock and loss due to timeout".

**Those two rules pull in opposite directions, and both apply here.** The mailbox must
refuse rather than grow (rule 29) *and* refuse rather than block (rule 6). A blocking `put`
on a full queue satisfies the first and violates the second, which is why `_enqueue` uses
`put_nowait`.

The reference bounds only its **outbound** gatekeeper and leaves its inbound queues
unbounded. We bound the inbound side too, because that is the side an opponent controls.
"""

from __future__ import annotations

import gc
import queue
import weakref

import pytest

from p2p_thief_agent.adapters.fastmcp_server import (
    QUEUE_DEPTH_MINIMUM,
    PeerInboxes,
    _enqueue,
)

MAILBOXES = ("agreements", "turns", "audits", "controls")


# --- M8-04c: no unbounded queue ----------------------------------------------------------


def test_every_mailbox_is_bounded_at_or_above_the_appendix_f_minimum() -> None:
    """`queue_depth` is a **Minimum**, so a bound below 100 is an illegal configuration —
    and a bound of 0, Python's "unlimited", is no bound at all."""
    inboxes = PeerInboxes()
    for name in MAILBOXES:
        maxsize = getattr(inboxes, name).maxsize
        assert maxsize != 0, f"{name} is unbounded; `queue.Queue()` defaults to no limit"
        assert maxsize >= QUEUE_DEPTH_MINIMUM, f"{name} bound {maxsize} is below the minimum"


def test_a_full_mailbox_refuses_the_next_message_rather_than_growing() -> None:
    inboxes = PeerInboxes()
    for step in range(QUEUE_DEPTH_MINIMUM):
        inboxes.turns.put_nowait({"step": step})
    assert inboxes.depths()["turns"] == QUEUE_DEPTH_MINIMUM
    with pytest.raises(queue.Full):
        inboxes.turns.put_nowait({"step": "one too many"})


def test_enqueue_reports_a_refusal_instead_of_blocking_the_request_thread() -> None:
    """**The rule-6 half.** A blocking `put` would hold the MCP request thread until the
    runtime drained the mailbox, converting a flood into a hang — and a hang is a deadlock
    loss, which is worse than a refused message.

    Tested against `_enqueue` rather than through the FastMCP server. The first version
    reached into the framework's private tool registry to call the decorated function; that
    is a test of a dependency's internals, and it would break on a version bump for reasons
    having nothing to do with this behaviour. `_enqueue` is our code and is where the
    decision actually lives.
    """
    inbox: queue.Queue = queue.Queue(maxsize=2)
    assert _enqueue(inbox, {"step": 1}) is True
    assert _enqueue(inbox, {"step": 2}) is True
    assert _enqueue(inbox, {"step": 3}) is False, "a full mailbox must refuse, not block"
    assert inbox.qsize() == 2, "the refused message must not have displaced anything"


def test_a_refused_message_leaves_the_earlier_ones_intact() -> None:
    """Refusing rather than dropping the oldest. Discarding a turn the opponent believes we
    received would desynchronise the match silently, which is far worse than a refusal they
    can see and retry."""
    inbox: queue.Queue = queue.Queue(maxsize=2)
    for step in (1, 2, 3):
        _enqueue(inbox, {"step": step})
    assert [inbox.get_nowait()["step"], inbox.get_nowait()["step"]] == [1, 2]


def test_each_mailbox_is_bounded_independently() -> None:
    """One flooded mailbox must not starve the others: an opponent spamming turns cannot
    also block the audit that ends the game."""
    inboxes = PeerInboxes()
    for step in range(QUEUE_DEPTH_MINIMUM):
        inboxes.turns.put_nowait({"step": step})
    inboxes.audits.put_nowait({"reveal": True})
    assert inboxes.depths() == {"agreements": 0, "turns": QUEUE_DEPTH_MINIMUM,
                                "audits": 1, "controls": 0}


# --- M8-10 / M8-10a: a long series does not accumulate -----------------------------------


def test_draining_returns_a_mailbox_to_empty_so_depth_does_not_creep() -> None:
    """The leak that matters is not one flood but slow accumulation: a mailbox ending each
    sub-game slightly fuller than it started is fine once and fatal by the sixth."""
    inboxes = PeerInboxes()
    for sub_game in range(6):
        for step in range(35):
            inboxes.turns.put_nowait({"sub_game": sub_game, "step": step})
        while not inboxes.turns.empty():
            inboxes.turns.get_nowait()
        assert inboxes.depths()["turns"] == 0, f"depth crept after sub-game {sub_game}"


def test_a_full_six_sub_game_load_never_exceeds_the_bound() -> None:
    """Six sub-games at the Appendix F step limit is 210 turns — twice the queue depth. It
    fits only because the runtime drains as it goes, which is the property worth pinning."""
    inboxes = PeerInboxes()
    high_water = 0
    for _ in range(6 * 35):
        inboxes.turns.put_nowait({"turn": True})
        high_water = max(high_water, inboxes.depths()["turns"])
        inboxes.turns.get_nowait()
    assert high_water == 1, f"a drained mailbox should hold at most one, held {high_water}"


# --- M8-10b: shutdown releases what it took ----------------------------------------------


def test_dropping_the_inboxes_releases_their_contents() -> None:
    """`M8-010b` asks that shutdown release every resource. The mailboxes are what this
    process owns outright, so this pins that they are collectable — a lingering reference
    from a tool closure would keep a whole series' messages alive after the game ended."""
    inboxes = PeerInboxes()
    for step in range(50):
        inboxes.turns.put_nowait({"step": step})
    witness = weakref.ref(inboxes.turns)

    del inboxes
    gc.collect()
    assert witness() is None, "the turn mailbox outlived its owner"
