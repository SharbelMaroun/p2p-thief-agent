"""`M9-007b`: the two chart types §9.3 names for distributions and sensitivity.

Split from `test_analysis_charts.py`, which covers the encoding contract shared by every
chart. These two have their own contract: a heatmap must print each cell's number, and a
box plot must survive a zero-variance group — a zero-variance arm is a real outcome here, which
is a real result that a naive box height would erase.
"""

from __future__ import annotations

import re

import pytest

from p2p_thief_agent.analysis import box_plot, heat_cell_colour, heatmap, summarise

COMMON = {"title": "T", "caption": "C", "x_label": "X", "y_label": "Y"}


def _rects(svg: str) -> list[dict[str, float]]:
    return [
        {k: float(v) for k, v in re.findall(r'(x|y|width|height)="([-\d.]+)"', tag)}
        for tag in re.findall(r"<rect [^>]*>", svg)
    ]


# --- heatmap: §9.3's named use, parameter sensitivity ------------------------------------


def test_the_heatmap_prints_every_cells_number() -> None:
    """A heatmap read by hue alone is the least accessible chart there is."""
    svg = heatmap(**COMMON, x_values=[1, 2], y_values=["r"], rows=[[0.1, 0.9]],
                  value_format="{:.1f}")
    assert ">0.1<" in svg and ">0.9<" in svg


def test_the_heatmap_refuses_a_row_count_that_disagrees_with_its_labels() -> None:
    """Silently zipping would mislabel every row — a wrong picture rather than no picture."""
    with pytest.raises(ValueError, match="1 rows for 2 y values"):
        heatmap(**COMMON, x_values=[1], y_values=["a", "b"], rows=[[0.5]])


def test_the_heat_ramp_runs_white_to_red_and_is_monotonic() -> None:
    assert heat_cell_colour(0.0, 0.0, 1.0) == "#ffffff"
    assert heat_cell_colour(1.0, 0.0, 1.0) == "#ff3333"
    channels = [int(heat_cell_colour(v / 10, 0.0, 1.0)[3:5], 16) for v in range(11)]
    assert channels == sorted(channels, reverse=True)


# --- box plot: §9.3's "box plots for distributions" --------------------------------------


def test_the_box_plot_labels_each_group_with_its_run_count() -> None:
    """A box drawn from three runs and one drawn from forty look identical otherwise."""
    svg = box_plot(**COMMON, labels=["arm"], summaries=[summarise([1.0, 2.0, 3.0])])
    assert ">n=3<" in svg


def test_the_box_plot_refuses_mismatched_labels_and_summaries() -> None:
    with pytest.raises(ValueError, match="1 labels for 2 summaries"):
        box_plot(**COMMON, labels=["a"],
                 summaries=[summarise([1.0]), summarise([2.0])])


def test_a_zero_variance_group_still_draws_a_visible_box() -> None:
    """A zero-spread group is a real outcome and would vanish if the box height came
    straight from `q3 - q1`."""
    svg = box_plot(**COMMON, labels=["arm"], summaries=[summarise([20.0] * 5)])
    boxes = [r for r in _rects(svg) if r.get("width", 0) < 200 and r.get("height", 0) >= 1]
    assert boxes, "a zero-spread arm must still be drawn"
