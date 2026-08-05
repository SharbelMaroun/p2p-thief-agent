"""Record belief-driven vs blind survival as research evidence (`M6-015b`).

Runs the fixed-scenario comparison and writes the totals to
``results/strategy_comparison.json``. Reuses the harness that
``tests/unit/test_strategy_comparison.py`` gates, so the recorded figures are exactly the
ones the test asserts. Run with ``uv run python scripts/strategy_comparison.py``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.unit.test_strategy_comparison import run_comparison  # noqa: E402


def run() -> dict:
    result = run_comparison()
    out = Path(__file__).resolve().parents[1] / "results" / "strategy_comparison.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    figures = run()
    print(
        f"blind {figures['blind_total_survival']} vs belief "
        f"{figures['belief_total_survival']} survival over {figures['scenarios']} "
        f"scenarios (max {figures['max_steps']} each)"
    )
