"""Reading the signed `board_and_agents` terms the Thief's policy can be sharpened with.

Split from `play_command.py` under the file-length gate. The seam is real rather than
convenient: everything here answers one question -- *what did both peers agree in writing
before move one?* -- and the answers feed optional sharpeners, never the protocol.

That distinction sets the contract: **nothing here raises.** A missing, malformed or
oddly-typed terms object costs the sharpener and returns the neutral default, because a
config problem must cost a worse first move and never a technical loss at the top of a
counted series. It is the same never-raise rule the private readers keep.

Why the values matter at all:

* ``cop_start`` is public and agreed. Without it the Thief's first belief is uniform over
  all 49 cells, discarding a fact that was signed before the game began. It shapes belief
  only until the first scent observation lands -- but that is precisely the window in
  which the Thief is otherwise blind and commits to an opening direction.
* ``grid_size`` was hardcoded to 7 at the call site. It has always *been* 7 against every
  opponent so far, which is exactly why a hardcoded 7 survives untested until the first
  peer who negotiates something else.
"""

from __future__ import annotations

from collections.abc import Mapping

DEFAULT_GRID_SIZE = 7


def board_terms(game_config: object) -> dict:
    """Return the signed `board_and_agents` table, or an empty one."""
    if isinstance(game_config, Mapping):
        section = game_config.get("board_and_agents")
        if isinstance(section, Mapping):
            return dict(section)
    return {}


def cop_start(game_config: object) -> tuple[int, int] | None:
    """The Cop's opening cell from the signed terms, for the Thief's first belief."""
    cell = board_terms(game_config).get("cop_start")
    if isinstance(cell, (list, tuple)) and len(cell) == 2:
        try:
            return int(cell[0]), int(cell[1])
        except (TypeError, ValueError):
            return None
    return None


def grid_size(game_config: object) -> int:
    """The negotiated board size, defaulting to the 7x7 both peers have always played."""
    size = board_terms(game_config).get("grid_size")
    return size if isinstance(size, int) and size > 0 else DEFAULT_GRID_SIZE
