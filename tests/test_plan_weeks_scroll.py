"""Plan weeks remain accessible while desktop columns share a lower edge."""
import ast
from datetime import date, timedelta
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
    weeks = tuple(
        SimpleNamespace(
            start_date=date(2026, 9, 7) + timedelta(weeks=index),
            end_date=date(2026, 9, 13) + timedelta(weeks=index),
        )
        for index in range(week_count)
    )
    labels = MagicMock(side_effect=lambda week, **kwargs: f"Week {week}")
    details = MagicMock(side_effect=lambda week: f"<div>Details {week}</div>")
    components = MagicMock()
    show = load_helper("_show_plan_weeks", st=st, components=components,
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


def test_current_week_is_first_visible_and_previous_weeks_remain_above():
    st = MagicMock()
    components = MagicMock()
    weeks = tuple(
        SimpleNamespace(
            start_date=date(2026, 8, 24) + timedelta(weeks=index),
            end_date=date(2026, 8, 30) + timedelta(weeks=index),
        )
        for index in range(4)
    )
    labels = MagicMock(
        side_effect=lambda week, **kwargs: week.start_date.isoformat()
    )
    show = load_helper(
        "_show_plan_weeks",
        st=st,
        components=components,
        _week_summary_label=labels,
        _week_html=lambda week: str(week.start_date),
    )

    show(SimpleNamespace(weeks=weeks), reference_day=date(2026, 9, 8))

    st.popover.assert_not_called()
    assert st.expander.call_args_list == [
        call("2026-08-24", expanded=False),
        call("2026-08-31", expanded=False),
        call("2026-09-07", expanded=False),
        call("2026-09-14", expanded=False),
    ]
    assert st.markdown.call_args_list[2] == call(
        '<span class="plan-current-week-anchor"></span>',
        unsafe_allow_html=True,
    )
    components.html.assert_called_once()
    script = components.html.call_args.args[0]
    assert ".st-key-plan_weeks_scroll" in script
    assert ".plan-current-week-anchor" in script
    assert "root.scrollTop" in script


def test_scroll_sizing_and_card_alignment_are_desktop_only():
    st = MagicMock()
    load_helper("_compact_plan_layout_styles", st=st)("Plan")
    css = st.markdown.call_args.args[0]
    desktop = css.split("@media (min-width: 1100px)", 1)[1].split("@media (max-width: 1099px)", 1)[0]
    assert "calc(100dvh - 46rem)" in desktop
    assert "overflow-y: auto" in desktop
    assert "align-items: stretch" in desktop
    assert "justify-content: space-between;" in desktop
    assert (
        ".plan-sidebar-card:last-child"
        in desktop
    )
    assert "margin-top: 0;" in desktop
    assert "flex: 1 1 0;" in desktop
    assert "flex-shrink: 0" in desktop
    plan_weeks_rule = (
        desktop
        .split(
            ".st-key-plan_weeks_scroll {",
            1,
        )[1]
        .split(
            "}",
            1,
        )[0]
    )

    assert (
        "overflow: hidden"
        not in plan_weeks_rule
    )

    assert (
        ".plan-sidebar-card:last-child"
        in desktop
    )
    assert "overflow: hidden;" in desktop
    assert ".upcoming-events" in desktop
    assert "overflow-y: auto;" in desktop
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
    source = PLAN_PATH.read_text(encoding="utf-8")
    equal_lower_columns = [
        node
        for node in calls
        if (
            isinstance(
                node.func,
                ast.Attribute,
            )
            and node.func.attr == "columns"
            and node.args
            and isinstance(
                node.args[0],
                ast.List,
            )
            and ast.literal_eval(
                node.args[0]
            )
            == [1, 1]
        )
    ]

    assert len(equal_lower_columns) == 1
    assert "upcoming_events_html(upcoming_events)" in source
    assert "plan_lower_row" in keys
    assert "plan_latest_adaptation" in keys

    assert (
        'vertical_alignment="top"'
        in source
    )

    assert (
        ".st-key-plan_latest_adaptation"
        in source
    )

    assert (
        ".upcoming-events"
        in source
    )

    assert "overflow-y: auto" in source
