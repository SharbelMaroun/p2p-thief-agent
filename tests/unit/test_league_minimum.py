"""`M9-021`: is the league minimum actually met, and is the answer actionable?

Split from `test_evidence.py`, which asks what the bundle contains. This asks whether the
contents satisfy rule 31's minimum — two counted games against two different groups, both
reported — and, more importantly, whether a failure says which half is short.

Order matters here and is asserted: an unreported game is checked **before** the counting,
because two games played and not reported score zero, so "minimum met" would be the more
misleading answer.
"""

from __future__ import annotations

from p2p_thief_agent.reporting.evidence import EvidenceBundle, league_minimums_met
from p2p_thief_agent.reporting.league_ledger import PlayedGame
from p2p_thief_agent.reporting.send_receipt import SendReceipt

PROV = {"github_commit": "a" * 40, "working_tree_clean": True}


def game(gid: str, opponent: str, *, counted: bool = True) -> PlayedGame:
    return PlayedGame(game_id=gid, opponent_group_id=opponent, counted=counted, won=True)


def bundle(*games: PlayedGame, receipts: bool = True) -> EvidenceBundle:
    b = EvidenceBundle()
    for g in games:
        b.add_game(g, provenance=PROV)
        if receipts:
            b.add_receipt(SendReceipt.from_api_response(
                {"id": f"msg-{g.game_id}"}, game_id=g.game_id, sent_at="t",
                recipient="rmisegal+uoh26finalgame@gmail.com"))
    return b


# --- M9-021: the league minimum ------------------------------------------------------------------


def test_two_counted_games_against_two_groups_meets_the_minimum() -> None:
    met, why = league_minimums_met(bundle(game("g1", "rival"), game("g2", "other")))
    assert met, why


def test_two_games_against_one_group_does_not() -> None:
    """Rule 52: repeat games against the same opponent do not accumulate score, so the
    second one cannot substitute for a second opponent."""
    met, why = league_minimums_met(bundle(game("g1", "rival"), game("g2", "rival")))
    assert not met
    assert "distinct opponent" in why


def test_the_reason_says_which_half_is_short() -> None:
    """A bare False a week before submission is not actionable: scheduling a new opponent
    and replaying an existing one are different amounts of work."""
    met, why = league_minimums_met(bundle(game("g1", "rival")))
    assert not met
    assert "1 counted game" in why


def test_an_unreported_game_fails_the_minimum_before_the_counting_does() -> None:
    """Checked first on purpose: two games that were played and not reported score zero,
    so reporting "minimum met" would be the more misleading answer."""
    met, why = league_minimums_met(bundle(game("g1", "rival"), game("g2", "other"),
                                          receipts=False))
    assert not met
    assert "AE-32" in why
