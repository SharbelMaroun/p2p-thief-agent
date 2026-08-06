"""`M8-009d`: the language model cannot reach the move decision.

Appendix E rule 25 is a **Recommendation**, not Mandatory, and the book says so outright:
"Recommendation not to transfer the decision on the movement move itself to the language
model. It is better to use it for creating a behavioural profile and for producing text
only. **Note: there is no mandatory sanction**, but blind reliance may lead to logical
malfunctions and a technical loss" (p.130/273). This repository already records that
reading — `README.md` states rule 25 is "a recommendation, not an automatic mandatory
sanction (`AE-025`)".

Having no sanction makes it *more* worth proving structurally, not less. The cost arrives
indirectly and in full: a hallucinated move is an **illegal** move, rule 13's sanction is
"illegal move and technical loss", and Table 2 scores that 0/0.

**The layout here makes the boundary easy to state.** The move deciders live in
`strategy/`, and the language layer is a separate top-level package, `verbal/`. So the
assertion is that no module under `strategy/` reaches `verbal/` transitively — direct
imports are the easy half, and the failure worth catching is a helper three hops down.

What the model may still do is unchanged: produce hints and behavioural profiling. What it
may not do is choose where the Thief runs.
"""

from __future__ import annotations

import ast
import inspect
import re
from pathlib import Path

import pytest

from p2p_thief_agent.strategy import baseline, belief_policy

SRC = Path(__file__).resolve().parents[2] / "src" / "p2p_thief_agent"

MOVE_DECIDERS = ("strategy/baseline.py", "strategy/belief_policy.py",
                 "strategy/metrics.py")
LANGUAGE_LAYER = ("p2p_thief_agent.verbal", "llm")


def _imports(relative: str) -> set[str]:
    tree = ast.parse((SRC / relative).read_text("utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
        elif isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
    return found


def _closure(relative: str, seen: set[str] | None = None) -> set[str]:
    """Every module a decider reaches, transitively."""
    seen = set() if seen is None else seen
    for module in _imports(relative):
        if not module.startswith("p2p_thief_agent") or module in seen:
            continue
        seen.add(module)
        path = SRC / (module.removeprefix("p2p_thief_agent.").replace(".", "/") + ".py")
        if path.exists():
            _closure(str(path.relative_to(SRC)).replace("\\", "/"), seen)
    return seen


@pytest.mark.parametrize("decider", MOVE_DECIDERS)
def test_no_move_deciding_module_can_reach_the_language_layer(decider: str) -> None:
    """**The test this module exists for.** Transitive, so an indirect route fails too."""
    leaked = sorted(m for m in _closure(decider)
                    if any(part in m for part in LANGUAGE_LAYER))
    assert not leaked, (
        f"{decider} reaches the language layer via {leaked}; rule 25 recommends the move "
        "decision stay algorithmic, and a hallucinated move is an illegal move [AE-13]"
    )


@pytest.mark.parametrize(
    "function",
    [baseline.choose_action, baseline.rank_actions, belief_policy.choose_evasive_action,
     belief_policy.believed_cop_cell],
)
def test_no_move_function_accepts_free_text(function) -> None:
    """A second, independent check. Even with the imports clean, a caller could hand a
    decider a generated string; none of these takes one.

    Matched on `\\bstr\\b` rather than a substring — the substring version flags
    `AbstractSet[...]` because "Ab**str**actSet" contains it, and a guard that cries wolf
    on a set of coordinates is a guard someone deletes.
    """
    hints = inspect.get_annotations(function, eval_str=False)
    suspicious = {name: annotation for name, annotation in hints.items()
                  if name != "return" and re.search(r"\bstr\b", str(annotation))}
    assert not suspicious, f"{function.__name__} accepts free text: {suspicious}"


def test_the_language_layer_does_exist_so_this_is_not_vacuous() -> None:
    """A boundary test passes trivially when there is nothing on the other side of it."""
    assert (SRC / "verbal").is_dir()
    assert list((SRC / "verbal").glob("*.py")), "verbal/ is empty; is the layer a stub?"


def test_the_verbal_layer_does_not_import_a_move_decider_either() -> None:
    """The reverse direction, which matters for a different reason: if hint generation
    imported the evasion policy it could *report* the intended move, and rule 26 confines
    the verbal channel to natural language. Not the same failure, same boundary."""
    for module in sorted((SRC / "verbal").glob("*.py")):
        reached = _closure(f"verbal/{module.name}")
        leaked = [m for m in reached if "strategy.belief_policy" in m or "strategy.baseline" in m]
        assert not leaked, f"verbal/{module.name} reaches a move decider via {leaked}"
