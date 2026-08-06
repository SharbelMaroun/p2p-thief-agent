"""Stepping through a replay, recomputing the verdict every time (`M8-008`, `M8-008a`).

`:1689`: the viewer "allows the user to navigate forward and backward in time using
playback controls"; `DEV-SPEC.md:426` restates it. The reference ships `Play / Pause`,
`Step >`, `Restart`, a sub-game selector and `Go to step`.

**The verdict is a property, not a field.** `M8-008a` asks that verification be recomputed
on every navigation rather than cached at load, and the cheapest way to guarantee that is
to leave nowhere to cache it: this class stores a cursor position and nothing else. A stale
verdict is unrepresentable rather than merely avoided.

That is not ceremony. The `Verified OK` banner is submission evidence (`:1769`, and the
README screenshot the book calls "absolute mandatory"), and evidence computed once at load
and painted thereafter is a claim about the past tense. If the document underneath changes,
the banner has to change with it or it is decoration.

**Navigation cannot leave the log.** `go_to` clamps rather than raising: a viewer whose
`Next` button throws at the last record crashes during the demonstration it exists to
produce.
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_thief_agent.replay.load import ReplayLog
from p2p_thief_agent.replay.sequence import SequenceReport, inspect_sequence
from p2p_thief_agent.replay.verify import MatchVerdict, RecordCheck, Verdict, verify_records


class Replay:
    """A cursor over a loaded log. Holds a position; derives everything else."""

    def __init__(self, log: ReplayLog) -> None:
        self._log = log
        self._position = 0

    @property
    def log(self) -> ReplayLog:
        return self._log

    @property
    def position(self) -> int:
        return self._position

    @property
    def total(self) -> int:
        return len(self._log.records)

    @property
    def record(self) -> Mapping[str, object]:
        return self._log.records[self._position]

    # --- derived, never stored ----------------------------------------------------------

    @property
    def verdict(self) -> MatchVerdict:
        """Re-verify the whole log, now. Recomputed on every read by construction."""
        return verify_records(self._log.records)

    @property
    def sequence(self) -> SequenceReport:
        """Structural findings, reported beside the verdict and never folded into it."""
        return inspect_sequence(self._log.records)

    @property
    def check(self) -> RecordCheck:
        """The verdict for the record under the cursor, also recomputed on every read."""
        return self.verdict.checks[self._position]

    @property
    def banner(self) -> str:
        """What a viewer paints for the match — green stamp or red banner."""
        return self.verdict.banner

    @property
    def stamp(self) -> Verdict:
        return self.verdict.verdict

    # --- navigation ---------------------------------------------------------------------

    def step_forward(self) -> int:
        """`Step >`. Stops at the last record rather than running off the end."""
        return self.go_to(self._position + 1)

    def step_back(self) -> int:
        """The half `:1689` asks for that a forward-only player would miss."""
        return self.go_to(self._position - 1)

    def go_to(self, position: int) -> int:
        """`Go to step` by index, clamped into the log."""
        self._position = max(0, min(position, self.total - 1))
        return self._position

    def go_to_step(self, step: object) -> int:
        """Jump by the record's own `step` value, which is what an auditor cites.

        Falls back to the current position when no record carries that step: a log whose
        numbering we do not recognise is exactly the log we still want to look at.
        """
        for index, record in enumerate(self._log.records):
            if isinstance(record, Mapping) and record.get("step") == step:
                return self.go_to(index)
        return self._position

    def restart(self) -> int:
        """`Restart`."""
        return self.go_to(0)

    def go_to_first_divergence(self) -> int | None:
        """Jump straight to the step that voided the match, if any.

        The one navigation an auditor performs: `:1769` has already decided the match, so
        the only remaining question is *which step*, and making someone click through a
        hundred records to find it is how that answer gets recorded wrong.
        """
        bad = self.verdict.first_bad
        return None if bad is None else self.go_to(bad.index)
