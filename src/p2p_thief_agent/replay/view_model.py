"""What the replay screen shows, as data (`M8-006`, `M8-006a`, `M8-008b`).

`M8-006`'s condition is "no widget touches domain or protocol code directly"; `M8-006a`'s
is "the view cannot mutate game state". Both hold the same way: this module turns a
`Replay` cursor into **display-ready strings and primitives**, and the widget layer reads
nothing else. Asked directly, the reference draws the boundary in the same place — its
widgets are "dumb" components handed dictionaries of ready-made strings, with a controller
between them and the domain.

That split is what makes the screenshot testable. A Tk window cannot be asserted about in
CI, but `ReplayFrame` can, so the picture in the README is backed by an assertion rather
than by someone having looked at it once.

**What the screen must carry**, asked directly: "the nonce, move, and the original commit
hash from the log entry" (p.56/142), plus a verdict indicator and controls to move back and
forth in time (p.56/141). The board is *not* required — the mandatory screenshot is about
the verdict — so the frame carries evidence rather than geometry, and the belief map stays
with the live GUI where the book puts it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from p2p_thief_agent.replay.cursor import Replay
from p2p_thief_agent.replay.verify import Verdict

# The reference's palette, so a grader comparing two teams' screenshots sees the same
# green for a good state rather than wondering whether the colour itself means something.
COLOUR_OK = "#2ecc71"
COLOUR_TAMPERED = "#c0392b"
COLOUR_NEUTRAL = "#546e7a"
COLOUR_TEXT_ON_STAMP = "#ffffff"
DASH = "—"


def _text(value: object) -> str:
    return DASH if value is None else str(value)


def _short(value: str, keep: int = 12) -> str:
    """Abbreviate a digest for the list. A 64-character wall reads as noise in a
    screenshot; the full value is shown for the step under the cursor, where it counts."""
    return value if len(value) <= keep else f"{value[:keep]}…"


@dataclass(frozen=True)
class StepRow:
    """One record as the panel shows it. Frozen, so a widget cannot write back."""

    index: int
    step: str
    sender: str
    move: str
    verdict: str
    reason: str
    commit: str
    nonce: str
    is_current: bool
    ok: bool

    @property
    def commit_short(self) -> str:
        return _short(self.commit)


@dataclass(frozen=True)
class ReplayFrame:
    """Everything one cursor position needs on screen. Carries no domain object."""

    origin: str
    game_id: str
    sub_game: str
    position: int
    total: int
    stamp: str
    stamp_colour: str
    banner: str
    sequence_summary: str
    sequence_ok: bool
    rows: tuple[StepRow, ...]

    @property
    def position_label(self) -> str:
        return f"step {self.position + 1} of {self.total}"

    @property
    def current(self) -> StepRow:
        return self.rows[self.position]


def _row(index: int, record: object, check, current: int,
         default_sender: object = None) -> StepRow:
    """Render one record, including one damaged badly enough not to be an object.

    A viewer that raises on a forged record shows nothing at all where it is supposed to
    show `TAMPERED`, which is the worst possible failure for this particular screen.

    Step, sender, and move are read from the record's top level and then from its sealed
    `payload`: fixture logs and the companion's artifacts carry them flat, while our own
    emitted log keeps them inside the payload — found the first time a *real* match log
    reached this screen and every row read `step ? — —`.
    """
    fields: Mapping[str, object] = record if isinstance(record, Mapping) else {}
    payload = fields.get("payload")
    sealed: Mapping[str, object] = payload if isinstance(payload, Mapping) else {}
    return StepRow(
        index=index,
        step=_text(fields.get("step", sealed.get("step", "?"))),
        sender=_text(fields.get("sender", sealed.get("sender", default_sender))),
        move=_text(fields.get("move", sealed.get("move"))),
        verdict=check.verdict.value,
        reason=check.reason,
        commit=_text(fields.get("commit")),
        nonce=_text(fields.get("nonce")),
        is_current=index == current,
        ok=check.ok,
    )


def frame_of(replay: Replay) -> ReplayFrame:
    """Snapshot the replay for rendering. Reads only; never moves the cursor.

    The verdict comes from `replay.verdict`, which recomputes on every access
    (`M8-008a`), so a frame is a live computation rather than a remembered result — which
    is precisely what makes a screenshot of it evidence.
    """
    verdict = replay.verdict
    sequence = replay.sequence
    # Our own records carry no per-record sender — every one is ours, so the log's own
    # declared role fills the column instead of a page of dashes.
    summary = replay.log.document.get("summary")
    role = summary.get("role") if isinstance(summary, dict) else None
    return ReplayFrame(
        origin=replay.log.origin,
        game_id=_text(replay.log.game_id),
        sub_game=_text(replay.log.sub_game),
        position=replay.position,
        total=replay.total,
        stamp=verdict.verdict.value,
        stamp_colour=COLOUR_OK if verdict.ok else COLOUR_TAMPERED,
        banner=verdict.banner,
        sequence_summary=sequence.summary,
        sequence_ok=sequence.contiguous,
        rows=tuple(
            _row(index, record, check, replay.position, role)
            for index, (record, check) in enumerate(
                zip(replay.log.records, verdict.checks, strict=True)
            )
        ),
    )


def stamp_is_green(frame: ReplayFrame) -> bool:
    """The single question a submission screenshot has to answer (`M8-015b`)."""
    return frame.stamp == Verdict.VERIFIED_OK.value and frame.stamp_colour == COLOUR_OK
