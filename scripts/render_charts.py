"""Render the measured results as charts (`M9-007b`).

Guidelines §9.3 names the types: "Bar charts for comparisons, Line charts for trends …
Heatmaps for parameter sensitivity, Box plots for distributions". `M9-007b` adds the
condition: "clear axes, legend, caption".

    uv run python scripts/run_experiments.py     # measure
    uv run python scripts/render_charts.py       # draw

Every chart reads `results/*.json`. This script computes nothing and invents nothing, which
is the separation that lets a reader check a picture against the file behind it.

The headline chart is `chart-metric-disagreement.svg`, which exists because two reasonable
metrics — survival steps and the points Appendix F actually pays — once ranked the strategies
in **opposite** directions, and a reader who saw only the survival-steps chart would have
drawn the wrong conclusion.

**Its title and caption are derived from the data rather than written down (2026-08-08).**
They said "opposite directions" for a day after the policy was fixed and the metrics agreed
again — a chart asserting the opposite of its own bars. A hard-coded conclusion about a
measured quantity is a claim with an expiry date nobody is watching, so the wording is now
computed from the same numbers the bars are drawn from.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p2p_thief_agent.analysis import (  # noqa: E402
    Series,
    Summary,
    bar_chart,
    box_plot,
    heatmap,
    line_chart,
)

RESULTS, ASSETS = ROOT / "results", ROOT / "assets"


def load(name: str) -> dict:
    return json.loads((RESULTS / f"{name}.json").read_text("utf-8"))


def _summary(block: dict) -> Summary:
    return Summary(runs=block["runs"], mean=block["mean"], stdev=block["stdev"],
                   minimum=block["min"], q1=block["q1"], median=block["median"],
                   q3=block["q3"], maximum=block["max"])



def _metric_title(points: dict, total: dict) -> str:
    """Name what the bars show, computed from the bars (`M9-006`)."""
    leads_points = points["belief"] > points["blind"]
    leads_steps = total["belief"] > total["blind"]
    if leads_points and leads_steps:
        return "Both metrics now rank belief above blind"
    if leads_points != leads_steps:
        return "The two metrics rank the strategies in opposite directions"
    return "Both metrics rank blind above belief"


def _metric_caption(n: int, steps: int, points: dict, total: dict) -> str:
    """State the comparison in the direction the numbers actually run."""
    verb = "leads" if total["belief"] > total["blind"] else "trails"
    pays = "and also leads" if points["belief"] > points["blind"] else "but trails"
    return (f"{n} openings, {steps}-turn horizon. Belief {verb} on survival steps "
            f"({total['belief']:.0f} vs {total['blind']:.0f}) {pays} on the points the "
            f"scoring table actually pays ({points['belief']} vs {points['blind']}).")


def charts() -> dict[str, str]:
    arms = load("strategy_arms")
    board, horizon = load("sweep_board_size"), load("sweep_horizon")
    n, steps = arms["scenarios"], arms["max_steps"]
    paired = arms["paired_belief_vs_blind"]
    points, total = arms["league_points"], arms["total_steps"]

    return {
        "chart-metric-disagreement.svg": bar_chart(
            title=_metric_title(points, total),
            caption=_metric_caption(n, steps, points, total),
            x_label="metric", y_label="value (steps ÷ 10, points as scored)",
            categories=["total steps ÷ 10", "league points"],
            series=[Series("blind", [total["blind"] / 10, points["blind"]]),
                    Series("belief", [total["belief"] / 10, points["belief"]])]),

        "chart-survival-distribution.svg": box_plot(
            title="Survival steps by evasion arm",
            caption=f"{n} perimeter openings. Blind is bimodal — {arms['survived_full_horizon']['blind']} "
                    f"total escapes and the rest caught early — while belief is consistent "
                    f"but escapes outright only {arms['survived_full_horizon']['belief']} times.",
            x_label="evasion arm", y_label="steps survived (max 35)",
            labels=["blind", "belief"],
            summaries=[_summary(arms["blind"]), _summary(arms["belief"])]),

        "chart-full-escapes.svg": bar_chart(
            title="Outright escapes: reaching the survival threshold",
            caption=f"The only outcome the scoring table pays 10 for. Belief wins "
                    f"{paired['wins']} of {paired['pairs']} paired scenarios on steps but "
                    f"converts fewer of them into escapes.",
            x_label="evasion arm", y_label="scenarios reaching the horizon",
            categories=["blind", "belief"],
            series=[Series("full escapes",
                           [arms["survived_full_horizon"]["blind"],
                            arms["survived_full_horizon"]["belief"]])]),

        "chart-sweep-board-size.svg": line_chart(
            title="Mean survival against board size",
            caption=f"Appendix F status {board['appendix_f_status']}, minimum "
                    f"{board['minimum']} — swept upward only, because a Minimum may be "
                    f"raised and never lowered. {board['points'][0]['scenarios']}+ openings per point.",
            x_label=board["parameter"], y_label="mean steps survived",
            x_values=[p["value"] for p in board["points"]],
            series=[Series("blind", [p["blind"]["mean"] for p in board["points"]]),
                    Series("belief", [p["belief"]["mean"] for p in board["points"]])]),

        "chart-sweep-horizon.svg": line_chart(
            title="League points against the survival threshold",
            caption=f"Appendix F status {horizon['appendix_f_status']}, minimum "
                    f"{horizon['minimum']}. A longer game is more time to be caught, and "
                    f"the gap widens against belief rather than closing.",
            x_label=horizon["parameter"], y_label="league points",
            x_values=[p["value"] for p in horizon["points"]],
            series=[Series("blind", [p["league_points"]["blind"] for p in horizon["points"]]),
                    Series("belief", [p["league_points"]["belief"] for p in horizon["points"]])]),

        "chart-parameter-sensitivity.svg": heatmap(
            title="Parameter sensitivity: mean survival by arm and board size",
            caption="Each row is one arm; each column one board size swept upward from the "
                    "Appendix F minimum of 7. Numbers are mean steps survived.",
            x_label="board size", y_label="evasion arm",
            x_values=[p["value"] for p in board["points"]],
            y_values=["blind", "belief"],
            rows=[[p["blind"]["mean"] for p in board["points"]],
                  [p["belief"]["mean"] for p in board["points"]]],
            value_format="{:.1f}"),
    }


def main() -> int:
    ASSETS.mkdir(exist_ok=True)
    for name, svg in charts().items():
        (ASSETS / name).write_text(svg, "utf-8")
        print(f"assets/{name}  ({len(svg):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
