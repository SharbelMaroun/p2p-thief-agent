"""The league evidence bundle: every counted game, and what still backs it (`M9-010`).

One place to answer the question a submission actually turns on — *for each counted game, do
we still have the artifacts, the commit that ran it, and evidence it was reported?* Each of
those exists somewhere already; none of them was assembled per game, and a gap is only
visible when they are read together.

`SendReceipt` lives next door in `send_receipt.py`, because what a sender can prove is a
different question from what a bundle contains, and conflating them is how "we sent it"
quietly becomes "they received it".

Every gap-finding method **returns rather than raises**. This is the pre-submission question
and the useful answer is the whole list at once; stopping at the first missing receipt turns
one review into six.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from p2p_thief_agent.reporting.league_ledger import PlayedGame, check_declared_count
from p2p_thief_agent.reporting.send_receipt import EvidenceError, SendReceipt

REQUIRED_KINDS = frozenset({"declaration", "config", "log", "result"})


@dataclass
class EvidenceBundle:
    """Every counted game's evidence, assembled for submission."""

    games: list[PlayedGame] = field(default_factory=list)
    receipts: dict[str, SendReceipt] = field(default_factory=dict)
    provenance: dict[str, dict] = field(default_factory=dict)

    def add_game(self, game: PlayedGame, *, provenance: Mapping[str, object]) -> None:
        """Record a played game and the commit that ran it (`M9-010b`)."""
        if any(existing.game_id == game.game_id for existing in self.games):
            raise EvidenceError(f"{game.game_id!r} is already in the bundle")
        commit = provenance.get("github_commit")
        if not isinstance(commit, str) or len(commit) != 40:
            raise EvidenceError(
                f"{game.game_id!r} has no resolved commit; rule 53 requires the hash of the "
                "code that played, and 'unknown' identifies nothing [AE-53]")
        self.games.append(game)
        self.provenance[game.game_id] = dict(provenance)

    def add_receipt(self, receipt: SendReceipt) -> None:
        if receipt.game_id in self.receipts:
            raise EvidenceError(
                f"{receipt.game_id!r} already has a receipt; two sends for one game risks "
                "the rule 35 conflict verdict, which scores 0 for BOTH teams")
        self.receipts[receipt.game_id] = receipt

    def unreported_games(self) -> tuple[str, ...]:
        """Counted games with no send receipt — each scores nothing (`AE-32`)."""
        return tuple(sorted(game.game_id for game in self.games
                            if game.counted and game.game_id not in self.receipts))

    def reconcile(self, declared: Mapping[str, int]) -> None:
        """Check every declared per-opponent count against the games on file (`M9-010d`).

        Every opponent is checked before anything raises. Rule 38's sanction is absolute
        disqualification of the project, which is not something to discover one opponent at
        a time.
        """
        problems: list[str] = []
        for opponent, count in sorted(declared.items()):
            try:
                check_declared_count(count, self.games, opponent)
            except ValueError as exc:
                problems.append(str(exc))
        if problems:
            raise EvidenceError("; ".join(problems))

    def summary(self, declared: Mapping[str, int] | None = None) -> dict[str, object]:
        """The bundle as it would be submitted."""
        counted = [game for game in self.games if game.counted]
        return {
            "counted_games": len(counted),
            "opponents": sorted({game.opponent_group_id for game in counted}),
            "warm_ups": len(self.games) - len(counted),
            "receipts": [self.receipts[gid].as_record() for gid in sorted(self.receipts)],
            "unreported_games": list(self.unreported_games()),
            "commits": {gid: prov.get("github_commit")
                        for gid, prov in sorted(self.provenance.items())},
            "declared_counts": dict(declared or {}),
        }


def archive_is_complete(files: Sequence[str]) -> bool:
    """Whether an archived set holds all four artifact kinds (`M9-010a`).

    Three of four is not a set: the missing one is invariably what an auditor asks for.
    """
    return {name.split("_", 1)[0] for name in files} >= REQUIRED_KINDS


def missing_evidence(bundle: EvidenceBundle,
                     archives: Mapping[str, Sequence[str]]) -> dict[str, list[str]]:
    """Per counted game, everything the bundle still lacks."""
    gaps: dict[str, list[str]] = {}
    for game in bundle.games:
        if not game.counted:
            continue
        missing = []
        if not archive_is_complete(archives.get(game.game_id) or ()):
            missing.append("archived artifact set")
        if game.game_id not in bundle.receipts:
            missing.append("send receipt")
        if game.game_id not in bundle.provenance:
            missing.append("commit hash")
        if missing:
            gaps[game.game_id] = missing
    return gaps


def league_minimums_met(bundle: EvidenceBundle, *, minimum_games: int = 2,
                        minimum_opponents: int = 2) -> tuple[bool, str]:
    """Whether the league minimum is actually met (`M9-021`, `AE-31`).

    Returns a reason, not a bare bool: "not met" a week before submission is only useful if
    it says *which* half is short, because scheduling a new opponent and replaying an
    existing one are different amounts of work.
    """
    counted = [game for game in bundle.games if game.counted]
    opponents = {game.opponent_group_id for game in counted}
    unreported = bundle.unreported_games()
    if unreported:
        return False, f"reported nothing for {', '.join(unreported)}; each scores 0 [AE-32]"
    if len(counted) < minimum_games:
        return False, f"{len(counted)} counted game(s), {minimum_games} required [AE-31]"
    if len(opponents) < minimum_opponents:
        return False, (f"{len(opponents)} distinct opponent(s), {minimum_opponents} "
                       "required — repeat games do not accumulate score [AE-52]")
    return True, f"{len(counted)} counted games against {len(opponents)} groups, all reported"
