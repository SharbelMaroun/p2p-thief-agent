"""C-030: the negotiation identity carries `git_commit_hash` when resolvable.

Group `uoh-ay26`'s `mutual_sign_off` requires `identity.git_commit_hash` to match
`^[0-9a-f]{40}$` in the **negotiation identity** and quietly voids the mutual result
when it is absent -- which turned the cleanly audited game-1 survival of 2026-08-12
into `mutual_sign_off=false` on their side. The book homes the hash in the sealed
Step-0 declaration instead (rules 24/53, `inst/:1295`), and the reference's wire
identity carries no code version at all, so this is an outbound peer accommodation:
attached when resolvable, omitted -- never fatal -- when not.
"""

import re

import p2p_thief_agent.adapters.negotiated as negotiated
from p2p_thief_agent.shared.git_info import GitInfoError

PRIVATE = {
    "game": {
        "group_id": "sharnamr",
        "group_name": "sharNamr",
        "members": ["Sharbel Maroun", "Amr safadi"],
        "repos": {"cop": "https://example.invalid/cop", "thief": "https://example.invalid/thief"},
    },
    "llm": {"model": "template"},
    "hardware": {"os": "Windows-11", "cpu": "x86_64"},
}


def build(tmp_path, monkeypatch=None):
    """Drive `negotiated_game` with an in-memory private config and shared file."""
    import json
    game = tmp_path / "game.json"
    game.write_text(json.dumps({"schema_version": "1.2"}), "utf-8")
    real_loader = negotiated.load_private_config
    negotiated.load_private_config = lambda _p: PRIVATE
    try:
        _, identity = negotiated.load_negotiation_inputs(
            game, "unused", "https://us.invalid/mcp", "https://them.invalid/mcp")
    finally:
        negotiated.load_private_config = real_loader
    return identity


def test_identity_carries_a_40_hex_commit_hash_from_a_git_checkout(tmp_path) -> None:
    """Running from this repository, the hash resolves and matches their regex."""
    identity = build(tmp_path)
    assert re.fullmatch(r"[0-9a-f]{40}", identity["git_commit_hash"])


def test_the_mandated_members_are_untouched_by_the_addition(tmp_path) -> None:
    """The accommodation extends the identity; it must not reshape it."""
    identity = build(tmp_path)
    for member in ("group_id", "group_name", "members", "repos", "mcp_servers",
                   "llm_model", "spec"):
        assert member in identity


def test_an_unresolvable_commit_omits_the_field_instead_of_failing(
    tmp_path, monkeypatch,
) -> None:
    """Best-effort on purpose: an optional duplicate must never refuse a match."""
    def refuse() -> str:
        raise GitInfoError("no git here")

    monkeypatch.setattr(negotiated, "running_git_commit", refuse)
    identity = build(tmp_path)
    assert "git_commit_hash" not in identity
    assert identity["group_id"] == "sharnamr"
