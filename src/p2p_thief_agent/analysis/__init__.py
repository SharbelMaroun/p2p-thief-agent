"""Parameter research and result visualisation (`M9-006`, `M9-007`).

Guidelines §9.1 asks for "systematic experiments with controlled changes to parameters",
§9.3 for bar, line, heatmap and box-plot visualisations. The book sets the standard: the
research must be "based on numbers and not on guesses" (p.142/266).

**This repository measures survival, not capture.** The Thief's question is how long it
lasts against a pursuing Cop, so every figure is in steps survived — and the harness is
*deterministic*, which changes what a run count means. See `statistics` for why the
scenario set is widened rather than repeated.

SVG rather than a plotting library: resolution-independent by construction, no dependency
to pin (`M8-009c`), and a chart emitted as text can be **asserted** rather than eyeballed.
"""

from p2p_thief_agent.analysis.boxplot import box_plot
from p2p_thief_agent.analysis.charts import Series, bar_chart, heat_cell_colour, line_chart
from p2p_thief_agent.analysis.heatmap import heatmap
from p2p_thief_agent.analysis.statistics import (
    PairedResult,
    Summary,
    paired_compare,
    quantile,
    summarise,
)

__all__ = [
    "PairedResult",
    "Series",
    "Summary",
    "bar_chart",
    "box_plot",
    "heat_cell_colour",
    "heatmap",
    "line_chart",
    "paired_compare",
    "quantile",
    "summarise",
]
