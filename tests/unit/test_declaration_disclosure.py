"""`M7-22f`: a peer that declared nothing is recorded as such, never filled in.

This repository already nested `llm_model` and `hardware_spec` inside each group, which is
where rule 24 wants them — the sanction is denial of eligibility for the **computational
bonus**, and `inst/:1276` frames that as judging whether an agent on a phone raced one on a
workstation fairly. A comparison between two machines cannot be made from one machine's spec.

What was wrong here was narrower and easier to miss. A `null` spec for an opponent reached
`_require` and died on `TypeError: argument of type 'NoneType' is not iterable`. So a caller
holding a peer that declared nothing had two choices: drop the group from the declaration, or
invent a spec for them.

The reference implementation takes the second. It resolves the opponent as
`opp = series.peer_identity or own`; an empty peer identity is falsy in Python, so it copies
its **own** hardware and model into the opponent's slot, and its sample artifacts show two
groups sharing one machine. That reads as a match played on one laptop rather than as a
defect, which is exactly why it survives.

Refusing `null` is what manufactures the pressure to fabricate. So `null` is accepted and
`undeclared` must name what was withheld: the omission stays theirs, and rule 38 — absolute
disqualification for a false declaration — is not tempted.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.reporting.declaration import build_declaration
from p2p_thief_agent.reporting.naming import ArtifactError, MatchIdentity

HARDWARE = {"os": "Windows 11", "cpu_type": "x86_64", "cpu_freq_mhz": 3600, "cpu_cores": 8,
            "ram_gb": 32.0, "gpu_model": "RTX 3060", "vram_gb": 6.0}
THEIRS = {**HARDWARE, "os": "Ubuntu 24.04", "cpu_type": "Apple M1", "vram_gb": 0}


def group(gid: str, **overrides: object) -> dict:
    base = {"group_id": gid, "group_name": gid.title(), "members": ["student-1"],
            "repos": {"cop": f"https://x/{gid}/c", "thief": f"https://x/{gid}/t"},
            "mcp_servers": {"peer": f"https://{gid}.example.com/mcp"},
            "llm_model": "template-free", "hardware_spec": dict(HARDWARE),
            "signature": "sig"}
    base.update(overrides)
    return base


def declaration(**overrides: object) -> dict:
    kwargs: dict = {
        "identity": MatchIdentity(game_id="g1", game_uid="u1"),
        "groups": [group("sharnamr"), group("rival", llm_model="gpt-x",
                                            hardware_spec=dict(THEIRS))],
        "num_sub_games": 6, "max_tokens_per_game": 1000, "timezone": "UTC",
        "started_at": "2026-08-07T10:00:00Z", "ended_at": "2026-08-07T13:00:00Z",
        "links": {}, "github_commit": "abcdef1",
    }
    kwargs.update(overrides)
    return build_declaration(**kwargs)


def test_both_groups_carry_their_own_machine() -> None:
    ours, theirs = declaration()["groups"]
    assert ours["hardware_spec"] == HARDWARE and theirs["hardware_spec"] == THEIRS
    assert ours["hardware_spec"] != theirs["hardware_spec"], "fixture guard"


@pytest.mark.parametrize("withheld", [["llm_model"], ["hardware_spec"],
                                      ["hardware_spec", "llm_model"]])
def test_an_undeclared_peer_is_accepted_when_the_absence_is_named(withheld: list) -> None:
    """**The fix.** This raised `TypeError` before 2026-08-07, so the only way to emit a
    declaration against a silent peer was to make something up for them."""
    absent = dict.fromkeys(withheld)
    ours, theirs = declaration(groups=[group("sharnamr"),
                                       group("rival", undeclared=withheld, **absent)])["groups"]
    for name in withheld:
        assert theirs[name] is None
        assert theirs[name] != ours[name], "never our own value in their slot"


def test_withholding_without_saying_so_is_refused() -> None:
    """The `undeclared` marker is the whole point: a bare `null` is indistinguishable from
    a bug on our side, and an examiner cannot tell who failed to declare."""
    with pytest.raises(ArtifactError, match="undeclared"):
        declaration(groups=[group("sharnamr"), group("rival", llm_model=None)])


def test_the_marker_must_name_exactly_what_is_missing() -> None:
    """Otherwise it could be filled in once and left to rot, claiming an omission that was
    later supplied — or hiding one that was not."""
    with pytest.raises(ArtifactError, match="undeclared"):
        declaration(groups=[group("sharnamr"),
                            group("rival", llm_model=None, hardware_spec=None,
                                  undeclared=["llm_model"])])


def test_our_own_group_may_never_withhold() -> None:
    """Rule 24 is Mandatory. Tolerance is for what a classmate sends us, never for what we
    declare about ourselves."""
    for absent in ("llm_model", "hardware_spec"):
        with pytest.raises(ArtifactError, match="rule 24|AE-24"):
            declaration(groups=[group("sharnamr", **{absent: None}),
                                group("rival", llm_model="x")])


def test_a_present_peer_spec_is_still_checked_for_completeness() -> None:
    """Tolerating an omission is not tolerating a malformed one. A spec that is *there* and
    half-filled is a different thing from one that was never sent."""
    thin = {k: v for k, v in THEIRS.items() if k != "cpu_cores"}
    with pytest.raises(ArtifactError, match="cpu_cores"):
        declaration(groups=[group("sharnamr"), group("rival", hardware_spec=thin)])


def test_a_peer_spec_of_the_wrong_type_is_refused() -> None:
    with pytest.raises(ArtifactError, match="object or null"):
        declaration(groups=[group("sharnamr"), group("rival", hardware_spec="a fast one")])
