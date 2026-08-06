"""`M9-007b`: the charts encode their data, and say so in words as well as colour.

The reason these charts are SVG rather than a raster library's output is that a chart
emitted as text can be **asserted**. A picture file can only be looked at, and "someone
looked at it once" is exactly the standard the rest of this project refuses.

So these tests check that a bar's height actually encodes its value, that every axis and
caption `M9-007b` asks for is present, and that no chart depends on colour alone.
"""

from __future__ import annotations

import re

import pytest

from p2p_thief_agent.analysis import (
    Series,
    bar_chart,
    box_plot,
    heatmap,
    line_chart,
    summarise,
)

COMMON = {"title": "T", "caption": "C", "x_label": "X", "y_label": "Y"}


def _rects(svg: str) -> list[dict[str, float]]:
    return [
        {k: float(v) for k, v in re.findall(r'(x|y|width|height)="([-\d.]+)"', tag)}
        for tag in re.findall(r"<rect [^>]*>", svg)
    ]


def _bars(svg: str) -> list[float]:
    """Bar heights only — not the page background, and not the 11x11 legend swatches,
    which is what the first version of this test accidentally measured."""
    rects = _rects(svg)
    legend = {(r["width"], r["height"]) for r in rects if r["width"] == r["height"] == 11}
    return sorted(
        r["height"] for r in rects
        if r["height"] > 0 and (r["width"], r["height"]) not in legend and r["width"] < 200
    )


def test_a_bars_height_actually_encodes_its_value() -> None:
    """**The test the whole SVG choice was made for.** A bar twice the value must be twice
    the height, or the picture is decoration that happens to sit near some numbers."""
    svg = bar_chart(**COMMON, categories=["a", "b"], series=[Series("s", [1.0, 2.0])])
    heights = _bars(svg)
    assert len(heights) == 2, f"expected two bars, measured {heights}"
    assert heights[1] == pytest.approx(2 * heights[0], rel=0.02)


def test_three_bars_stay_proportional_across_the_whole_range() -> None:
    """Two points can be proportional by accident; three cannot."""
    heights = _bars(bar_chart(**COMMON, categories=["a", "b", "c"],
                              series=[Series("s", [1.0, 2.0, 4.0])]))
    assert len(heights) == 3
    assert heights[1] == pytest.approx(2 * heights[0], rel=0.02)
    assert heights[2] == pytest.approx(4 * heights[0], rel=0.02)


def test_every_chart_carries_its_title_caption_and_both_axis_labels() -> None:
    """`M9-007b`'s literal condition: "clear axes, legend, caption"."""
    charts = (
        bar_chart(**COMMON, categories=["a"], series=[Series("s", [1.0])]),
        line_chart(**COMMON, x_values=[1, 2], series=[Series("s", [1.0, 2.0])]),
        box_plot(**COMMON, labels=["a"], summaries=[summarise([1.0, 2.0, 3.0])]),
        heatmap(**COMMON, x_values=[1], y_values=["r"], rows=[[0.5]]),
    )
    for svg in charts:
        assert "<title>T</title>" in svg and "<desc>C</desc>" in svg
        assert ">X<" in svg and ">Y<" in svg


def test_a_bar_and_line_chart_both_print_a_legend_entry_per_series() -> None:
    for svg in (bar_chart(**COMMON, categories=["a"], series=[Series("alpha", [1.0]),
                                                              Series("beta", [2.0])]),
                line_chart(**COMMON, x_values=[1], series=[Series("alpha", [1.0]),
                                                           Series("beta", [2.0])])):
        assert ">alpha<" in svg and ">beta<" in svg


def test_every_bar_prints_its_own_value_so_colour_is_not_the_only_signal() -> None:
    """The accessibility condition, and the reason a greyscale print of the report still
    carries the measurement."""
    svg = bar_chart(**COMMON, categories=["a", "b"], series=[Series("s", [0.25, 0.75])])
    assert ">0.25<" in svg and ">0.75<" in svg


def test_a_line_chart_marks_each_measured_point_rather_than_only_joining_them() -> None:
    """A smooth line hides how many measurements there were. `M9-006c` cares about run
    counts; a reader should be able to count the points."""
    svg = line_chart(**COMMON, x_values=[1, 2, 3], series=[Series("s", [1.0, 2.0, 1.5])])
    assert len(re.findall(r"<circle ", svg)) == 3


def test_a_flat_series_still_renders_instead_of_collapsing() -> None:
    """Two of the real sweeps came back perfectly flat. A chart that divided by the range
    would have crashed on exactly the results that needed explaining."""
    svg = line_chart(**COMMON, x_values=[1, 2, 3], series=[Series("s", [0.975] * 3)])
    assert len(re.findall(r"<circle ", svg)) == 3


def test_an_all_zero_series_does_not_divide_by_zero() -> None:
    assert "<svg" in bar_chart(**COMMON, categories=["a"], series=[Series("s", [0.0])])
