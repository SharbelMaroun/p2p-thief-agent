"""How many games we have played, and what that is worth (`M7-007`, `M7-010`, `M7-017`).

Rule 37 (Mandatory): "Declare accurately the number of games actually played at the start
of each game." Rule 38 (Prohibited): "Do not make false declarations regarding the number
of games; a false declaration **disqualifies the project**. Sanction: absolute
disqualification for disciplinary and integrity reasons."

That sanction is why this counts from **emitted artifacts** rather than from a tally
somebody maintains. A hand-kept counter is a number a human can be wrong about; a count
derived from the result files on disk is a number that agrees with the evidence the
lecturer receives, because it *is* that evidence. Rule 38 does not distinguish a lie from a
mistake.

**Warm-ups do not count** (rule 52, and `:2028`): "Only one game is played against each
opponent (no repetitions for score accumulation); warm-up games that do not count are
permitted." So the count that matters is *counted games against this opponent*, and a
warm-up must be marked at emission — deciding later which games "were really warm-ups"
after seeing the scores is precisely the false declaration rule 38 forbids.

**The diversity reward** is 10 points, Fixed (`:3541`), for a **win against an opponent not
played before** (`:2028`, p.70/166). Not for a draw and not for a loss: `:2028` says "a
victory against an opponent earns full points", and the bonus row is titled "Reward for a
win against a new opponent".
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

DIVERSITY_REWARD = 10  # Appendix F, Fixed


class LeagueLedgerError(ValueError):
    """Raised when the declared history would not match the artifacts on disk."""


@dataclass(frozen=True)
class PlayedGame:
    """One finished game as its result artifact records it."""

    game_id: str
    opponent_group_id: str
    counted: bool
    won: bool

    @classmethod
    def from_result(cls, result: Mapping[str, object]) -> PlayedGame:
        """Read a game from its result artifact.

        `counted` defaults to **True** on purpose. A result file that forgot to say it was
        a warm-up is more likely a counted game with a missing flag than a warm-up nobody
        labelled, and over-declaring is safe under rule 38 while under-declaring is the
        false declaration it disqualifies for.
        """
        agreement = result.get("mutual_agreement")
        opponent = ""
        if isinstance(agreement, Mapping):
            opponent = str(agreement.get("opponent_group_id") or "")
        final = result.get("final_result")
        won = bool(isinstance(final, Mapping) and final.get("winner_group")
                   and final.get("winner_group") == result.get("our_group_id"))
        if not opponent:
            raise LeagueLedgerError(
                f"result {result.get('game_id')!r} names no opponent; rule 37 needs a count "
                "per opponent and an unattributed game cannot be counted against anyone")
        return cls(game_id=str(result.get("game_id") or ""), opponent_group_id=opponent,
                   counted=bool(result.get("counted", True)), won=won)


def games_against(played: Iterable[PlayedGame], opponent: str) -> int:
    """`M7-007a`/`M7-007b`: counted games against one opponent, warm-ups excluded."""
    return sum(1 for game in played if game.opponent_group_id == opponent and game.counted)


def declare_games_played(played: Sequence[PlayedGame], opponent: str) -> dict[str, object]:
    """The declaration block rule 37 requires, derived rather than asserted."""
    counted = games_against(played, opponent)
    return {
        "opponent_group_id": opponent,
        "games_played_including_this": counted + 1,
        "counted_games_before_this": counted,
        "first_meeting_between_groups": counted == 0,
        "warm_ups_excluded": sum(1 for g in played
                                 if g.opponent_group_id == opponent and not g.counted),
    }


def diversity_reward(played: Sequence[PlayedGame], opponent: str, *, won: bool) -> int:
    """`M7-017b`. Ten points for a **win** against a group not met before.

    Both conditions matter and are easy to conflate: a first meeting that we lose earns
    nothing, and a win against a familiar opponent earns nothing either — rule 52 says
    repeat games do not accumulate score at all.
    """
    if not won:
        return 0
    return DIVERSITY_REWARD if games_against(played, opponent) == 0 else 0


def series_total(sub_games: Iterable[Mapping[str, object]]) -> dict[str, int]:
    """`M7-017a`: recompute the series from the stored sub-game lines.

    Recomputed rather than carried forward. A total that travels alongside the lines can
    disagree with them, and rule 35 scores a contradicting report 0 for **both** teams —
    so the number we send has to be one the artifacts can reproduce.
    """
    lines = list(sub_games)
    if not lines:
        raise LeagueLedgerError("a series with no sub-games has no total to report")
    return {
        "sub_games": len(lines),
        "total_score": sum(int(line.get("score", 0)) for line in lines),
        "tokens_total_series": sum(int(line.get("tokens", 0)) for line in lines),
    }


def check_declared_count(declared: int, played: Sequence[PlayedGame], opponent: str) -> None:
    """Refuse a declaration that disagrees with the artifacts (`M7-007`).

    Rule 38's sanction is absolute disqualification, and it does not care whether the
    mismatch was a lie or an arithmetic slip — so the check is here rather than in a
    reviewer's head.
    """
    actual = games_against(played, opponent) + 1
    if declared != actual:
        raise LeagueLedgerError(
            f"declared {declared} games against {opponent!r} but the result artifacts show "
            f"{actual}; rule 38 disqualifies the project for a false declaration [AE-38]")
