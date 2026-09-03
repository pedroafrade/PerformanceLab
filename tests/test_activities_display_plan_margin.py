"""Presentation-only RPE, BPM colors, and Plan layout checks."""
import ast
from datetime import date
from html import escape
from pathlib import Path
from unittest.mock import MagicMock

import altair as alt
import pytest


COMPONENTS = Path(__file__).resolve().parents[1] / "app/components"


def helper(filename, name, **namespace):
    tree = ast.parse((COMPONENTS / filename).read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = {"date": date, "escape": escape, "alt": alt, **namespace}
    exec(compile(ast.Module(body=[node], type_ignores=[]), filename, "exec"), scope)
    return scope[name]


@pytest.mark.parametrize("value,label", [(None, "—"), (0, "0"), (7.1, "7"),
    (7.8, "8"), (7.5, "8"), (6.5, "6"), (10, "10")])
def test_rpe_display_uses_consistent_nearest_even_rounding(value, label):
    assert helper("activities_page.py", "_rpe_label")(value) == label


@pytest.mark.parametrize("comparison", [False, True])
def test_current_heart_rate_is_red_even_if_comparison_sorts_first(comparison):
    rows = [{"Activity": "Z current"}]
    if comparison:
        rows += [{"Activity": "A comparison"}]
    color = helper("activity_analysis.py", "_metric_activity_color")(
        "Heart rate", rows, alt.Legend() if comparison else None)
    spec = color.to_dict()
    assert spec["scale"]["domain"] == [row["Activity"] for row in rows]
    assert spec["scale"]["range"] == ["#e53935", "#2563eb"]


def test_power_uses_purple_color_scale():
    spec = helper(
        "activity_analysis.py",
        "_metric_activity_color",
    )(
        "Power",
        [{"Activity": "Current"}],
        None,
    ).to_dict()

    assert spec["scale"]["domain"] == ["Current"]
    assert spec["scale"]["range"] == [
        "#9333ea",
        "#2563eb",
    ]


def test_plan_overview_keeps_svg_capable_renderer_and_explicit_gap():
    text = (COMPONENTS / "plan_page.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute)
             and any(isinstance(v, ast.Constant) and isinstance(v.value, str)
                     and 'class="plan-overview"' in v.value for v in ast.walk(n))]
    assert len(calls) == 1
    assert calls[0].func.attr == "markdown"
    assert any(k.arg == "unsafe_allow_html" and ast.literal_eval(k.value) for k in calls[0].keywords)
    assert ".plan-overview > * { flex-shrink: 0; }" in text


def test_plan_bottom_adjustment_is_scoped_to_weeks_on_desktop():
    st = MagicMock()
    helper("plan_page.py", "_compact_plan_layout_styles", st=st)("Plan")
    css = st.markdown.call_args.args[0]
    desktop = css.split("@media (min-width: 1100px)", 1)[1].split("@media (max-width: 1099px)", 1)[0]
    assert "calc(100dvh - 46rem)" in desktop
    assert "plan_weeks_section" in desktop
    assert "margin-top: -0.5rem" in desktop
    assert "justify-content: space-between" in desktop
