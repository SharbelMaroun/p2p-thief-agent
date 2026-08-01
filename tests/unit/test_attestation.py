"""`M4-006c` (pre-move ordering) and `M4-006a` (running git commit).

Appendix E rule 24 requires the Step-0 host/code/token attestation to be sealed
*before the first move*. The ordering guard makes that checkable, and the git resolver
supplies the exact running commit the attestation binds. Both fail closed: a move that
slips ahead of the attestation, or a commit that cannot be resolved, must raise rather
than pass quietly.
"""

import pytest

from p2p_thief_agent.protocol.attestation import (
    AttestationError,
    require_pregame_attestation,
)
from p2p_thief_agent.shared.git_info import GitInfoError, running_git_commit

SHA = "0123456789abcdef0123456789abcdef01234567"


def spec_rec() -> dict:
    return {"payload": {"step": 0, "type": "system_spec"}, "nonce": "x", "commit": "y"}


def move_rec(step: int) -> dict:
    return {"payload": {"step": step, "move": "N"}, "nonce": "x", "commit": "y"}


def test_attestation_before_moves_is_accepted() -> None:
    require_pregame_attestation([spec_rec(), move_rec(1), move_rec(2)])


def test_no_records_is_accepted() -> None:
    """A game that sealed nothing has no move ahead of its attestation."""
    require_pregame_attestation([])


def test_a_move_before_the_attestation_is_refused() -> None:
    """`AE-024`: a move that precedes Step-0 is the exact ordering the rule forbids."""
    with pytest.raises(AttestationError, match="step 1 sealed before the step-0 attestation"):
        require_pregame_attestation([move_rec(1), spec_rec()])


def test_a_step_zero_that_is_not_a_system_spec_does_not_count() -> None:
    not_spec = {"payload": {"step": 0, "type": "something_else"}}
    with pytest.raises(AttestationError):
        require_pregame_attestation([not_spec, move_rec(1)])


def test_the_running_git_commit_is_a_lowercase_forty_hex_sha() -> None:
    value = running_git_commit()
    assert len(value) == 40 and value == value.lower()
    assert running_git_commit() == value, "the running commit is stable within one process"


def test_a_bound_commit_can_be_injected_for_deterministic_tests() -> None:
    assert running_git_commit(runner=lambda: SHA.upper() + "\n") == SHA


def test_an_unresolvable_commit_fails_closed() -> None:
    def broken() -> str:
        raise OSError("git not found")

    with pytest.raises(GitInfoError, match="could not resolve"):
        running_git_commit(runner=broken)


def test_a_malformed_commit_is_refused() -> None:
    with pytest.raises(GitInfoError, match="unexpected git commit format"):
        running_git_commit(runner=lambda: "not-a-sha")
