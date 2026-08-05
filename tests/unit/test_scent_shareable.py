"""`M6-018`: the scent physics is a self-contained unit, offered to the opponent for parity.

Book §6 recommends sharing the scent source so both peers run identical logic. `scent.py`
depends on nothing in this project — only `from __future__` — so it can be offered verbatim.
A peer that adopts it, or reproduces the documented model, produces byte-identical fields,
which the `M6-005` scent-model lock then verifies at negotiation. Under `THIEF-002` the offer
is one-directional: we publish our scent logic and its hash and consume nothing back.
"""

from pathlib import Path

SCENT = Path(__file__).resolve().parents[2] / "src" / "p2p_thief_agent" / "perception" / "scent.py"


def test_the_scent_physics_is_self_contained_and_shareable() -> None:
    imports = [
        line.strip()
        for line in SCENT.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith(("import ", "from "))
    ]
    assert imports == ["from __future__ import annotations"]
    assert not any("p2p_thief_agent" in line for line in imports)  # no project dependency
