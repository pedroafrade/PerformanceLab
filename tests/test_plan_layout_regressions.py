"""Plan layout regression tests, without authentication or athlete loading."""

import ast
from datetime import date
from html import escape
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


PLAN_PATH = (
    Path(__file__).resolve().parents[1]
    / "app" / "components" / "plan_page.py"
)


def plan_tree():
    return ast.parse(PLAN_PATH.read_text(encoding="utf-8"))


def load_helper(name, **namespace):
    node = next(
        node for node in plan_tree().body
        if isinstance(node, ast.FunctionDef) and node.name == name
    )
    scope = {"date": date, "escape": escape, **namespace}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(PLAN_PATH), "exec"), scope)
    return scope[name]


@pytest.mark.parametrize("has_plan", [False, True])
def test_plan_generation_is_full_width_without_export(has_plan):
    streamlit = MagicMock()
    streamlit.button.return_value = False
    export = MagicMock(return_value="calendar-content")
    confirmation = MagicMock()
    show = load_helper(
        "_show_plan_actions",
        st=streamlit,
        _plan_calendar_ics=export,
        _show_plan_generation_confirmation=confirmation,
    )
    plan = SimpleNamespace(weeks=(object(),) if has_plan else ())
    show(plan, object(), None)

    assert streamlit.button.call_args.kwargs["use_container_width"] is True
    assert streamlit.button.call_args.kwargs["disabled"] is True
    streamlit.download_button.assert_not_called()
    export.assert_not_called()
    confirmation.assert_not_called()


def test_generation_still_requires_confirmation():
    streamlit = MagicMock()
    streamlit.button.return_value = True
    confirmation = MagicMock()
    show = load_helper(
        "_show_plan_actions",
        st=streamlit,
        _plan_calendar_ics=MagicMock(return_value="calendar-content"),
        _show_plan_generation_confirmation=confirmation,
    )
    athlete = object()
    callback = MagicMock()
    show(SimpleNamespace(weeks=()), athlete, callback)
    confirmation.assert_called_once_with(athlete, callback)
    callback.assert_not_called()


def test_actions_and_cards_share_the_same_column():
    show = next(
        node for node in plan_tree().body
        if isinstance(node, ast.FunctionDef) and node.name == "show_plan_page"
    )
    column_calls = [
        node for node in ast.walk(show)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "columns"
    ]
    assert len(column_calls) == 1
    assert ast.literal_eval(column_calls[0].args[0]) == [3.4, 1]

    right_blocks = [
        node for node in show.body
        if isinstance(node, ast.With)
        and any(
            isinstance(item.context_expr, ast.Name)
            and item.context_expr.id == "sidebar_column"
            for item in node.items
        )
    ]
    calls = {
        node.func.id
        for block in right_blocks
        for node in ast.walk(block)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert {"_show_plan_actions", "_sidebar_phase_html", "_sidebar_week_html"} <= calls


def test_no_action_row_or_spacer_above_main_content():
    source = PLAN_PATH.read_text(encoding="utf-8")
    assert "plan-generate-button-spacer" not in source
    assert "title_column, action_column" not in source


def test_plan_styles_do_not_target_sidebar_widgets():
    streamlit = MagicMock()
    load_helper("_compact_plan_layout_styles", st=streamlit)("Subtitle")
    css = streamlit.markdown.call_args.args[0]
    for widget in ("stDivider", "stCaptionContainer", "stAltairChart", "stExpander", "stExpanderDetails"):
        lines = [
            line.strip() for line in css.splitlines()
            if f'div[data-testid="{widget}"]' in line
        ]
        assert lines
        assert all(line.startswith('section[data-testid="stMain"] ') for line in lines)
    assert 'button[kind="primary"]' not in css
    assert '.st-key-plan_generate button' in css
