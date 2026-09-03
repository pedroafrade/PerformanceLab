"""Plan weeks remain accessible while desktop columns share a lower edge."""
import ast
from datetime import date
from html import escape
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest


PLAN_PATH = Path(__file__).resolve().parents[1] / "app/components/plan_page.py"


def load_helper(name, **namespace):
    tree = ast.parse(PLAN_PATH.read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = {"date": date, "escape": escape, **namespace}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(PLAN_PATH), "exec"), scope)
    return scope[name]


@pytest.mark.parametrize("week_count", [0, 1, 8, 52])
def test_all_weeks_and_details_are_rendered_inside_scroll_container(week_count):
    st = MagicMock()
    weeks = tuple(range(week_count))
    labels = MagicMock(side_effect=lambda week, **kwargs: f"Week {week}")
    details = MagicMock(side_effect=lambda week: f"<div>Details {week}</div>")
    show = load_helper("_show_plan_weeks", st=st,
                       _week_summary_label=labels, _week_html=details)
    today = date(2026, 9, 3)
    show(SimpleNamespace(weeks=weeks), reference_day=today)
    st.container.assert_called_once_with(height=220, border=True, key="plan_weeks_scroll")
    assert labels.call_args_list == [call(week, reference_day=today) for week in weeks]
    assert details.call_args_list == [call(week) for week in weeks]
    assert st.expander.call_args_list == [call(f"Week {week}", expanded=False) for week in weeks]
    assert st.markdown.call_args_list == [
        call(f"<div>Details {week}</div>", unsafe_allow_html=True) for week in weeks]
    # The parent context encloses all child expanders and their contents.
    events = [c[0] for c in st.mock_calls]
    assert events.index("container().__enter__") < events.index("container().__exit__")
    if weeks:
        assert events.index("container().__enter__") < events.index("expander")
        assert max(i for i, e in enumerate(events) if e == "markdown") < events.index("container().__exit__")


def test_scroll_sizing_and_card_alignment_are_desktop_only():
    st = MagicMock()
    load_helper("_compact_plan_layout_styles", st=st)("Plan")
    css = st.markdown.call_args.args[0]
    desktop = css.split("@media (min-width: 1100px)", 1)[1].split("@media (max-width: 1099px)", 1)[0]
    assert "calc(100dvh - 46rem)" in desktop
    assert "overflow-y: auto" in desktop
    assert "align-items: stretch" in desktop
    assert "justify-content: space-between;" in desktop
    assert ".plan-sidebar-card:last-child { margin-top: 0; }" in desktop
    assert "flex-shrink: 0" in desktop
    assert "overflow: hidden" not in desktop
    mobile = css.split("@media (max-width: 1099px)", 1)[1].split(".plan-page-header", 1)[0]
    assert "height: auto !important" in mobile
    assert "overflow: visible !important" in mobile


def test_plan_uses_one_weeks_helper_and_scoped_column_container():
    tree = ast.parse(PLAN_PATH.read_text(encoding="utf-8"))
    show = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "show_plan_page")
    calls = [n for n in ast.walk(show) if isinstance(n, ast.Call)]
    assert sum(isinstance(n.func, ast.Name) and n.func.id == "_show_plan_weeks" for n in calls) == 1
    keys = [k.value.value for n in calls for k in n.keywords
            if k.arg == "key" and isinstance(k.value, ast.Constant)]
    assert "plan_page_columns" in keys and "plan_summary_cards" in keys
