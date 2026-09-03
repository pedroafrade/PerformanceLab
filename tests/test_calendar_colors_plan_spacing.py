"""Calendar session identity and Plan spacing regressions."""
import ast
from datetime import date
from html import escape
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


COMPONENTS = Path(__file__).resolve().parents[1] / "app/components"


def helper(filename, name, **namespace):
    node = next(n for n in ast.parse((COMPONENTS / filename).read_text(encoding="utf-8")).body
                if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = {"date": date, "escape": escape, **namespace}
    exec(compile(ast.Module(body=[node], type_ignores=[]), filename, "exec"), scope)
    return scope[name]


@pytest.mark.parametrize("title,expected", [
    ("Easy Run", "easy"), ("  EASY_run ", "easy"), ("Shakeout", "easy"),
    ("Shakeout Run", "easy"), ("Tempo Run", "tempo"), ("Intervals", "tempo"),
    ("LT2 Run", "tempo"), ("Hill Run", "hills"), ("Hill Reps", "hills"),
    ("Hills", "hills"), ("Long Run", "long"), ("Recovery Run", "other"),
    ("Not an easy run", "other"), (None, "other"), ("<script>", "other"),
])
def test_explicit_session_names_and_safe_fallback(title, expected):
    classify = helper("calendar_page.py", "_calendar_session_class")
    assert classify(SimpleNamespace(kind="planned", title=title)) == "session-" + expected


@pytest.mark.parametrize("kind", ["event", "completed"])
def test_events_and_completed_activities_keep_their_own_identity(kind):
    classify = helper("calendar_page.py", "_calendar_session_class")
    assert classify(SimpleNamespace(kind=kind, title="Long Run")) == ""


def test_grid_contains_type_status_and_escaped_content():
    classify = helper("calendar_page.py", "_calendar_session_class")
    label = helper("calendar_page.py", "_calendar_item_label")
    render = helper("calendar_page.py", "_calendar_html",
                    _calendar_session_class=classify, _calendar_item_label=label,
                    _phase_label=lambda day: None)
    items = (
        SimpleNamespace(kind="planned", title="Long Run", status="missed", summary="<test>"),
        SimpleNamespace(kind="event", title="Race & run", status=None, summary="", priority="A"),
    )
    day = SimpleNamespace(day=date(2026, 9, 3), is_current_month=True, is_today=False,
                          items=items, is_rest_day=False)
    html = render(SimpleNamespace(weeks=((day,),)))
    assert "status-missed session-long" in html
    assert "&lt;test&gt;" in html and "<test>" not in html
    assert "[A] Race &amp; run" in html


def test_type_colors_and_legend_match_and_race_background_is_preserved():
    st = MagicMock()
    helper("calendar_page.py", "_calendar_styles", st=st)()
    css = st.markdown.call_args.args[0]
    for group, color in {"easy": "#8bcf91", "tempo": "#e4b932",
                         "hills": "#287342", "long": "#a078cf"}.items():
        assert f".planned.session-{group} {{ border-color: {color}; }}" in css
        assert f".session-{group}::before {{ background: {color}; }}" in css
    assert "background: rgba(160, 160, 160, 0.14)" in css
    assert "background: rgba(224, 90, 90, 0.15)" in css


def test_plan_overview_has_one_flow_and_cards_use_equal_free_space():
    st = MagicMock()
    helper("plan_page.py", "_compact_plan_layout_styles", st=st)("Plan")
    css = st.markdown.call_args.args[0]
    assert ".plan-overview > * { flex-shrink: 0; }" in css
    assert ".plan-overview .weekly-phase-timeline { margin: 0; }" in css
    assert "justify-content: space-between;" in css
    assert ".plan-sidebar-card:last-child { margin-top: auto; }" not in css
    tree = ast.parse((COMPONENTS / "plan_page.py").read_text(encoding="utf-8"))
    overview = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute) and n.func.attr == "markdown"
                and any(isinstance(v, ast.Constant) and isinstance(v.value, str)
                        and 'class="plan-overview"' in v.value for v in ast.walk(n))]
    assert len(overview) == 1
    names = {n.id for n in ast.walk(overview[0]) if isinstance(n, ast.Name)}
    assert {"timeline_html", "summary_html"} <= names
