"""Focused UI tests without starting authentication or loading athlete data."""

import ast
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import altair as alt
import pytest


ROOT = Path(__file__).resolve().parents[1] / "app" / "components"


def functions_from(filename, *names, **globals_):
    """Execute only the selected presentation helpers, without app startup."""
    tree = ast.parse((ROOT / filename).read_text(encoding="utf-8"))
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in names
    ]
    assert len(nodes) == len(names)
    namespace = {"alt": alt, "timedelta": timedelta, **globals_}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), filename, "exec"), namespace)
    return namespace


def development_data(count=100):
    return SimpleNamespace(
        dates=tuple(date(2026, 1, 1) + timedelta(days=i) for i in range(count)),
        daily_load=tuple(float(i) for i in range(count)),
        fitness=tuple(float(i) for i in range(count)),
        fatigue=tuple(float(i + 1) for i in range(count)),
        form=tuple(-1.0 for _ in range(count)),
    )


def chart_functions():
    return functions_from(
        "development_page.py",
        "_mobile_chart_cutoff",
        "_mobile_chart_predicate",
        "_daily_load_chart_rows",
        "_development_chart_rows",
        "_daily_training_load_chart",
        "_development_load_form_chart",
    )


@pytest.mark.parametrize("builder", [
    "_daily_training_load_chart",
    "_development_load_form_chart",
])
def test_mobile_chart_limits_display_without_truncating_source(builder):
    functions = chart_functions()
    data = development_data()
    before = vars(data).copy()
    spec = functions[builder](data, mobile=True).to_dict()
    assert vars(data) == before
    cutoff = max(data.dates) - timedelta(days=59)
    boundary = {"year": cutoff.year, "month": cutoff.month, "date": cutoff.day}
    for layer in spec["layer"]:
        if "transform" not in layer:
            continue
        predicates = [t["filter"] for t in layer["transform"] if "filter" in t]
        assert {"field": "Date", "gte": boundary} in predicates
    assert spec["layer"][0]["encoding"]["x"]["axis"]["tickCount"] == 4


@pytest.mark.parametrize("builder,height", [
    ("_daily_training_load_chart", 175),
    ("_development_load_form_chart", 225),
])
def test_desktop_chart_keeps_full_history_and_original_dimensions(builder, height):
    spec = chart_functions()[builder](development_data()).to_dict()
    assert spec["height"] == height
    for layer in spec["layer"]:
        for transform in layer.get("transform", []):
            assert "filter" not in transform
    assert spec["layer"][0]["encoding"]["x"]["axis"]["tickCount"] == 10


def test_rolling_average_is_calculated_before_mobile_display_filter():
    spec = chart_functions()["_daily_training_load_chart"](
        development_data(), mobile=True,
    ).to_dict()
    transforms = spec["layer"][0]["transform"]
    window_index = next(i for i, value in enumerate(transforms) if "window" in value)
    filter_index = next(i for i, value in enumerate(transforms) if "filter" in value)
    assert window_index < filter_index


def test_mobile_cutoff_handles_empty_short_and_unsorted_history():
    cutoff = chart_functions()["_mobile_chart_cutoff"]
    assert cutoff(development_data(0)) is None
    short = development_data(3)
    assert cutoff(short) <= min(short.dates)
    short.dates = tuple(reversed(short.dates))
    assert cutoff(short) == max(short.dates) - timedelta(days=59)


@pytest.mark.parametrize("stale", [False, True])
def test_saved_context_notice_is_after_narrative_and_only_when_stale(stale):
    streamlit = MagicMock()
    namespace = functions_from(
        "activities_page.py",
        "_activity_coach_display_text",
        "_show_activity_coach_narrative",
        st=streamlit,
    )
    narrative = SimpleNamespace(
        prudent_interpretation="Interpretation",
        recommendations="Recommendation",
        measured_facts="Facts",
        deterministic_signals="Signals",
        data_limitations="Limits",
        provider="Provider",
        model="Model",
    )
    namespace["_show_activity_coach_narrative"](narrative, stale=stale)
    calls = streamlit.mock_calls
    notices = [
        i for i, call in enumerate(calls)
        if call[0] == "caption" and "This saved interpretation" in call.args[0]
    ]
    assert bool(notices) is stale
    if stale:
        narrative_positions = [i for i, call in enumerate(calls) if call[0] == "markdown"]
        assert notices[0] > max(narrative_positions)


def test_filters_are_after_and_outside_the_scroll_container():
    tree = ast.parse((ROOT / "activities_page.py").read_text(encoding="utf-8"))

    def container_key(node):
        if not isinstance(node, ast.With):
            return None
        for item in node.items:
            expr = item.context_expr
            if isinstance(expr, ast.Call):
                for kw in expr.keywords:
                    if kw.arg == "key" and isinstance(kw.value, ast.Constant):
                        return kw.value.value
        return None

    browser = next(n for n in ast.walk(tree) if container_key(n) == "activities_browser")
    filters = next(n for n in ast.walk(tree) if container_key(n) == "activities_browser_filters")
    assert filters.lineno > browser.end_lineno
    assert filters not in list(ast.walk(browser))


def test_sidebar_uses_inherited_page_background():
    streamlit = MagicMock()
    namespace = functions_from("sidebar.py", "_sidebar_styles", st=streamlit)
    namespace["_sidebar_styles"]("dashboard")
    css = streamlit.markdown.call_args.args[0]
    assert 'background: var(--background-color)' not in css
    assert '[data-testid="stAppViewContainer"]' in css
    assert '[data-testid="stSidebarContent"]' in css
    assert "background: inherit;" in css


def test_calendar_does_not_force_black_text_or_today_border():
    streamlit = MagicMock()
    namespace = functions_from("calendar_page.py", "_calendar_styles", st=streamlit)
    namespace["_calendar_styles"]()
    css = streamlit.markdown.call_args.args[0]
    assert "color: #000" not in css
    assert "color: rgba(0, 0, 0," not in css
    assert "color: inherit !important;" in css
    assert "currentColor !important;" in css


def test_compact_charts_are_selected_by_css_viewport_not_user_agent():
    source = (ROOT / "development_page.py").read_text(encoding="utf-8")
    assert "@media (max-width: 700px)" in source
    assert ".st-key-development_load_form_mobile" in source
    assert ".st-key-development_load_form_desktop" in source
