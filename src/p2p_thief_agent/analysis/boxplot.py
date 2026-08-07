"""Box plots — §9.3's "Box plots for distributions".

A mean alone cannot say whether a configuration is *reliable*. Two sweeps can share a mean
capture rate while one wins every match in half the runs and loses every match in the other
half; the box is what makes that visible, and it is the difference between a parameter
being safe to negotiate and merely being safe on average.

Drawn from `statistics.Summary`, so the picture and the reported table are the same five
numbers rather than two computations that might drift apart.
"""

from __future__ import annotations

from collections.abc import Sequence
from html import escape

from p2p_thief_agent.analysis.charts import INK, MUTED, SERIES_COLOURS
from p2p_thief_agent.analysis.statistics import Summary

WIDTH, HEIGHT = 720, 400
PAD_LEFT, PAD_RIGHT, PAD_TOP, PAD_BOTTOM = 70, 30, 56, 70


def box_plot(*, title: str, caption: str, x_label: str, y_label: str,
             labels: Sequence[str], summaries: Sequence[Summary]) -> str:
    """One box per measured group, each annotated with its own run count."""
    if len(labels) != len(summaries):
        raise ValueError(f"{len(labels)} labels for {len(summaries)} summaries")
    high = max((s.maximum for s in summaries), default=1.0) or 1.0
    plot_width, plot_height = WIDTH - PAD_LEFT - PAD_RIGHT, HEIGHT - PAD_TOP - PAD_BOTTOM

    def text(x, y, body, *, size=11, colour=INK, anchor="middle", weight="normal"):
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Segoe UI,Arial,sans-serif" '
                f'font-size="{size}" fill="{colour}" text-anchor="{anchor}" '
                f'font-weight="{weight}">{escape(str(body))}</text>')

    def y_of(value: float) -> float:
        return HEIGHT - PAD_BOTTOM - plot_height * (value / high)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}" role="img">',
        f'<title>{escape(title)}</title><desc>{escape(caption)}</desc>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#ffffff"/>',
        text(WIDTH / 2, 24, title, size=15, weight="bold"),
        text(WIDTH / 2, 42, caption, size=10, colour=MUTED),
        text(WIDTH / 2, HEIGHT - 8, x_label, size=11, colour=MUTED),
        f'<g transform="translate(16,{HEIGHT / 2}) rotate(-90)">'
        + text(0, 0, y_label, size=11, colour=MUTED) + "</g>",
    ]
    for index in range(6):
        value = high * index / 5
        y = y_of(value)
        parts.append(f'<line x1="{PAD_LEFT}" y1="{y:.1f}" x2="{WIDTH - PAD_RIGHT}" '
                     f'y2="{y:.1f}" stroke="#e0e0e0"/>')
        parts.append(text(PAD_LEFT - 8, y + 4, f"{value:.2f}", size=10, colour=MUTED,
                          anchor="end"))
    slot = plot_width / max(len(summaries), 1)
    for index, (label, summary) in enumerate(zip(labels, summaries, strict=True)):
        centre = PAD_LEFT + slot * (index + 0.5)
        colour = SERIES_COLOURS[index % len(SERIES_COLOURS)]
        half = min(slot * 0.28, 34)
        low, q1, median, q3, top = summary.five_number
        parts.append(f'<line x1="{centre}" y1="{y_of(low):.1f}" x2="{centre}" '
                     f'y2="{y_of(top):.1f}" stroke="{INK}"/>')
        for whisker in (low, top):
            parts.append(f'<line x1="{centre - half / 2}" y1="{y_of(whisker):.1f}" '
                         f'x2="{centre + half / 2}" y2="{y_of(whisker):.1f}" '
                         f'stroke="{INK}"/>')
        parts.append(f'<rect x="{centre - half:.1f}" y="{y_of(q3):.1f}" '
                     f'width="{half * 2:.1f}" height="{max(y_of(q1) - y_of(q3), 1):.1f}" '
                     f'fill="{colour}" fill-opacity="0.35" stroke="{colour}"/>')
        parts.append(f'<line x1="{centre - half:.1f}" y1="{y_of(median):.1f}" '
                     f'x2="{centre + half:.1f}" y2="{y_of(median):.1f}" '
                     f'stroke="{colour}" stroke-width="3"/>')
        parts.append(text(centre, HEIGHT - PAD_BOTTOM + 18, label, size=10, colour=MUTED))
        parts.append(text(centre, HEIGHT - PAD_BOTTOM + 32, f"n={summary.runs}", size=9,
                          colour=MUTED))
    parts.append("</svg>")
    return "\n".join(parts)
