"""The heatmap §9.3 asks for specifically: "Heatmaps for parameter sensitivity".

Two swept parameters against one measured outcome. This is the chart that answers the
question a one-at-a-time sweep cannot — whether two parameters interact, or whether their
effects simply add.

Kept in its own module because it is the only chart with a two-dimensional domain, and
folding it into `charts.py` would have pushed that file past the length cap for no gain in
cohesion.

**Every cell prints its value.** The colour carries the pattern; the number carries the
measurement. `M9-007b` asks for accessible charts and a heatmap read by hue alone is the
least accessible chart there is.
"""

from __future__ import annotations

from collections.abc import Sequence
from html import escape

from p2p_thief_agent.analysis.charts import INK, MUTED, heat_cell_colour

CELL_WIDTH, CELL_HEIGHT = 78, 46
MARGIN_LEFT, MARGIN_TOP = 96, 78
MARGIN_RIGHT, MARGIN_BOTTOM = 30, 70


def heatmap(
    *,
    title: str,
    caption: str,
    x_label: str,
    y_label: str,
    x_values: Sequence[object],
    y_values: Sequence[object],
    rows: Sequence[Sequence[float]],
    value_format: str = "{:.2f}",
) -> str:
    """Render `rows[y][x]` as a coloured grid with the number in every cell."""
    if len(rows) != len(y_values):
        raise ValueError(f"{len(rows)} rows for {len(y_values)} y values")
    flat = [value for row in rows for value in row]
    low, high = (min(flat), max(flat)) if flat else (0.0, 1.0)
    width = MARGIN_LEFT + CELL_WIDTH * len(x_values) + MARGIN_RIGHT
    height = MARGIN_TOP + CELL_HEIGHT * len(y_values) + MARGIN_BOTTOM

    def text(x: float, y: float, body: str, *, size: int = 11, colour: str = INK,
             anchor: str = "middle", weight: str = "normal") -> str:
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Segoe UI,Arial,sans-serif" '
                f'font-size="{size}" fill="{colour}" text-anchor="{anchor}" '
                f'font-weight="{weight}">{escape(body)}</text>')

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img">',
        f'<title>{escape(title)}</title><desc>{escape(caption)}</desc>',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        text(width / 2, 26, title, size=15, weight="bold"),
        text(width / 2, 44, caption, size=10, colour=MUTED),
        text(width / 2, height - 26, x_label, size=11, colour=MUTED),
        f'<g transform="translate(18,{height / 2}) rotate(-90)">'
        + text(0, 0, y_label, size=11, colour=MUTED) + "</g>",
    ]
    for column, x_value in enumerate(x_values):
        parts.append(text(MARGIN_LEFT + CELL_WIDTH * (column + 0.5), MARGIN_TOP - 10,
                          str(x_value), size=10, colour=MUTED))
    for row_index, y_value in enumerate(y_values):
        y = MARGIN_TOP + CELL_HEIGHT * row_index
        parts.append(text(MARGIN_LEFT - 10, y + CELL_HEIGHT / 2 + 4, str(y_value),
                          size=10, colour=MUTED, anchor="end"))
        for column, value in enumerate(rows[row_index]):
            x = MARGIN_LEFT + CELL_WIDTH * column
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL_WIDTH}" height="{CELL_HEIGHT}" '
                f'fill="{heat_cell_colour(value, low, high)}" stroke="#cfd8dc"/>')
            parts.append(text(x + CELL_WIDTH / 2, y + CELL_HEIGHT / 2 + 4,
                              value_format.format(value), size=11))
    parts.append(text(width / 2, height - 8,
                      f"scale: {value_format.format(low)} (white) "
                      f"to {value_format.format(high)} (red)", size=9, colour=MUTED))
    parts.append("</svg>")
    return "\n".join(parts)
