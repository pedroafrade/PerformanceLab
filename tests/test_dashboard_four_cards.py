"""Dashboard composition, shared summary and removal of Today shortcuts."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "app/components"


def test_dashboard_has_exact_requested_card_order():
    source = (ROOT / "dashboard/dashboard_view.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    view = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_show_dashboard_content")
    titles = [k.value.value for n in ast.walk(view) if isinstance(n, ast.Call)
              and isinstance(n.func, ast.Name) and n.func.id == "dashboard_widget"
              for k in n.keywords if k.arg == "title"]
    assert titles == ["Latest Activity", "Weekly Plan", "Upcoming Events",
                      "Training Load & Recovery", "Daily Brief", "Next Workout",
                      "Activities Summary"]
    assert 'getattr(daily_brief_resolution, "narrative", None)' in source
    assert "Automatic Training Coach" in source
    assert "_daily_brief_metadata(daily_brief_resolution)" in source
    assert "Local guidance from Today · Fallback" in source
    assert "TodayPresenter(athlete).build(reference_time=reference_time)" in source
    assert "show_title=False" in source


def test_today_session_has_no_navigation_buttons():
    tree = ast.parse((ROOT / "today_page.py").read_text(encoding="utf-8"))
    session = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_show_today_session")
    assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                   and n.func.attr == "button" for n in ast.walk(session))
    assert "session_card.structure" in ast.unparse(session)


def test_weekly_plan_has_seven_equal_columns_and_preserves_navigation():
    source = (ROOT / "dashboard/cards/planning_card.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
    day_columns = next(n for n in calls if isinstance(n.func, ast.Attribute)
                       and n.func.attr == "columns" and n.args
                       and isinstance(n.args[0], ast.List) and len(n.args[0].elts) == 9)
    assert [n.value for n in day_columns.args[0].elts] == [0.45] + [1] * 7 + [0.45]
    assert next(k.value.value for k in day_columns.keywords if k.arg == "gap") is None
    assert "_show_previous_button()" in source and "_show_next_button()" in source
    assert "selector_columns" not in source and "timeline_columns" not in source


def test_summary_defaults_preserve_activities_page_heading():
    tree = ast.parse((ROOT / "activities_page.py").read_text(encoding="utf-8"))
    show = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_show_activity_summary")
    assert show.args.kwonlyargs[-1].arg == "show_title"
    assert show.args.kw_defaults[-1].value is True
