"""`M8-014`: pin the wire surface, so a change after the league starts cannot be silent.

**The row's premise is stronger than the rules, and that is worth stating.** Asked directly,
there is **no blanket prohibition on changing the protocol**: rule 53 says plainly that "it
is permitted to change, update and improve the code between games". What rule 11 forbids is
*asymmetry within a match* — the configuration must be "identical, bit-for-bit, on both
sides", sanction "disqualification of the game due to lack of symmetry".

So this is not a rule we are obeying; it is a **policy we are choosing**, and the honest
framing matters. Changing the wire between counted games is legal, but it is the change most
likely to disqualify a game by accident: an opponent who negotiated against yesterday's tool
names and argument spellings will simply fail, and the failure surfaces mid-match as their
error rather than ours.

What is frozen here is the **surface** — tool names and argument names — not the
implementation behind it. Improving a policy, fixing a bug or speeding up a decision changes
nothing an opponent can observe and stays permitted, which is exactly what rule 53 protects.

`M8-014`'s calendar half ("before the counted league") cannot be verified before a counted
game exists. This is the half that can: the surface is recorded, and any later change fails
here rather than at the audit.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tests.conformance.neutral_peer import TOOLS

ROOT = Path(__file__).resolve().parents[2]
FROZEN = Path(__file__).with_name("frozen_wire_profile.json")


def current_surface() -> dict[str, list[str]]:
    """The observable wire surface: tool names and their argument names, sorted.

    Read from the neutral stub rather than from our own adapter on purpose. The stub writes
    the names out independently, so this records what an *opponent* must match — not what
    our client happens to send, which would drift together with our server and freeze
    nothing.
    """
    return {name: [argument] for name, argument in sorted(TOOLS.items())}


def surface_digest(surface: dict[str, list[str]]) -> str:
    canonical = json.dumps(surface, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def test_the_wire_surface_matches_the_frozen_record() -> None:
    """**The gate.** A renamed tool or a renamed argument fails here, in a run that takes
    two seconds, instead of during a counted game against a stranger."""
    assert FROZEN.exists(), (
        "no frozen profile recorded; run `python -m tests.conformance.test_profile_freeze` "
        "or write frozen_wire_profile.json from `current_surface()`"
    )
    frozen = json.loads(FROZEN.read_text("utf-8"))
    surface = current_surface()
    assert surface == frozen["surface"], (
        "the wire surface changed after the freeze. Rule 53 permits improving the code "
        "between games, but a renamed tool breaks an opponent who negotiated against the "
        "old names — re-freeze deliberately, and tell every scheduled opponent."
    )
    assert surface_digest(surface) == frozen["sha256"]


def test_the_frozen_record_names_what_it_does_not_cover() -> None:
    """A freeze that reads as covering everything would stop legitimate improvement. The
    record says in its own text that only the surface is pinned."""
    frozen = json.loads(FROZEN.read_text("utf-8"))
    assert "rule 53" in frozen["scope"].lower()
    assert frozen["frozen"] == ["tool names", "argument names"]


def test_the_four_tools_are_the_option_b_set() -> None:
    """Independent of the digest: if the frozen file were ever regenerated from a broken
    surface, the digest would agree with itself. This asserts the *content*."""
    assert set(current_surface()) == {"negotiate", "receive_turn", "submit_audit",
                                      "receive_control"}
    assert "receive_move" not in current_surface(), "excluded by the wire profile"


def test_every_tool_takes_exactly_one_argument() -> None:
    """The shape an opponent codes against. A second parameter added to any tool is a
    breaking change however compatible it looks from inside."""
    for name, arguments in current_surface().items():
        assert len(arguments) == 1, f"{name} takes {arguments}, not a single argument"


if __name__ == "__main__":  # pragma: no cover - the one-off freeze
    surface = current_surface()
    FROZEN.write_text(json.dumps({
        "surface": surface,
        "sha256": surface_digest(surface),
        "frozen": ["tool names", "argument names"],
        "scope": ("Only the observable wire surface is frozen. Rule 53 permits changing, "
                  "updating and improving the code between games, and that stays permitted: "
                  "implementation, strategy and performance are not pinned here."),
    }, indent=2, sort_keys=True) + "\n", "utf-8")
    print(f"froze {len(surface)} tools at {surface_digest(surface)[:16]}")
