"""Grouped running filter and dashboard-only compact headers."""
import ast
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock

from runpy import run_path

_summary_helpers = run_path(
    str(
        Path(__file__).with_name(
            "test_activity_summary_periods.py"
        )
    )
)
load_summary = _summary_helpers["load_summary"]
activity = _summary_helpers["activity"]
from datetime import date

ROOT = Path(__file__).resolve().parents[1] / "app/components"


def test_all_running_keeps_separate_sports_and_does_not_duplicate():
    today = date(2026, 9, 4)
    rows = tuple(activity(today, sport=s) for s in (
        "Running", "Trail Running", "Road Running", "Cycling", "Trail Cycling", "Swimming", "Walking"))
    selected = load_summary()["_summary_activities"](
        rows, period="This year", sport="All Running", reference_day=today)
    assert selected == rows[:3]
    assert load_summary()["_summary_totals"](selected)["count"] == 3
    assert rows[1].sport == "Trail Running"


def test_real_period_order():
    tree = ast.parse((ROOT / "activities_page.py").read_text(encoding="utf-8"))
    periods = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "_SUMMARY_PERIODS" for t in n.targets))
    assert ast.literal_eval(periods) == ("All time", "1 year", "This year", "6 months", "1 month")


def test_dashboard_header_does_not_render_overflow_action():
    tree = ast.parse((ROOT / "dashboard/widget.py").read_text(encoding="utf-8"))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "dashboard_widget")
    future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
    module = ast.fix_missing_locations(ast.Module(body=[future, function], type_ignores=[]))
    st = MagicMock()
    scope = {"st": st, "contextmanager": contextmanager}
    exec(compile(module, "widget", "exec"), scope)
    with scope["dashboard_widget"](title="Next Event", key="dashboard_top_event", action=MagicMock()):
        pass
    st.button.assert_not_called()
    assert not any("⋮" in str(c) for c in st.markdown.call_args_list)
