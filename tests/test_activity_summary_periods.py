"""Independent summary filters, calendar boundaries, and available-value totals."""
import ast
from calendar import monthrange
from datetime import date, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


PATH = Path(__file__).resolve().parents[1] / "app/components/activities_page.py"


def load_summary(st=None):
    tree = ast.parse(PATH.read_text(encoding="utf-8"))
    names = {"_summary_start_date", "_summary_sport", "_summary_activities", "_summary_totals",
             "_activities_summary_html", "_show_activity_summary"}
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    scope = {"date": date, "datetime": datetime, "timedelta": timedelta,
             "monthrange": monthrange, "st": st,
             "_SUMMARY_PERIODS": ("All time", "1 year", "6 months", "1 month"),
             "format_duration": lambda v: "—" if v is None else str(v),
             "format_distance": lambda v: "—" if v is None else f"{v:.2f} km",
             "format_elevation": lambda v: "—" if v is None else f"{v:.0f} m"}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(PATH), "exec"), scope)
    return scope


def activity(day, sport="Running", duration=timedelta(hours=1), distance=10, elevation=100):
    return SimpleNamespace(workout_date=day, sport=sport, duration=duration,
                           distance=distance, elevation_gain=elevation)


@pytest.mark.parametrize("period,reference,expected", [
    ("All time", date(2026, 9, 3), None),
    ("1 month", date(2026, 9, 3), date(2026, 8, 3)),
    ("6 months", date(2026, 9, 3), date(2026, 3, 3)),
    ("1 year", date(2026, 9, 3), date(2025, 9, 3)),
    ("1 month", date(2026, 3, 31), date(2026, 2, 28)),
    ("1 month", date(2024, 3, 31), date(2024, 2, 29)),
    ("1 year", date(2024, 2, 29), date(2023, 2, 28)),
    ("6 months", date(2026, 1, 31), date(2025, 7, 31)),
])
def test_calendar_month_boundaries(period, reference, expected):
    assert load_summary()["_summary_start_date"](period, reference_day=reference) == expected


def test_inclusive_dates_and_future_exclusion():
    rows = [activity(date(2026, 8, 2)), activity(date(2026, 8, 3)),
            activity(datetime(2026, 9, 3, 23, 59)), activity(date(2026, 9, 4)), activity(None)]
    select = load_summary()["_summary_activities"]
    assert select(rows, period="1 month", sport=None, reference_day=date(2026, 9, 3)) == tuple(rows[1:3])
    assert select(rows, period="All time", sport=None, reference_day=date(2026, 9, 3)) == tuple(rows[:3])


def test_global_and_per_sport_totals_without_mutating_rows():
    day = date(2026, 9, 3)
    rows = (activity(day), activity(day, "Cycling", timedelta(hours=2), 40, 500))
    scope = load_summary()
    total = scope["_summary_totals"](rows)
    assert total == {"count": 2, "duration": timedelta(hours=3), "distance": 50,
                     "elevation_gain": 600, "partial": False}
    selected = scope["_summary_activities"](rows, period="1 month", sport="Cycling", reference_day=day)
    assert selected == (rows[1],)
    assert scope["_summary_totals"](selected)["distance"] == 40
    assert rows[0].distance == 10 and rows[1].duration == timedelta(hours=2)


def test_missing_measurements_are_not_invented():
    scope = load_summary()
    missing = activity(date(2026, 9, 3), duration=None, distance=None, elevation=None)
    totals = scope["_summary_totals"]((missing,))
    assert totals["count"] == 1 and totals["partial"] is True
    assert all(totals[key] is None for key in ("duration", "distance", "elevation_gain"))
    partial = scope["_summary_totals"]((missing, activity(date(2026, 9, 3))))
    assert partial["distance"] == 10 and partial["partial"] is True


def test_zero_values_and_empty_selection_are_distinct_from_missing():
    total = load_summary()["_summary_totals"]
    for rows in ((), (activity(date(2026, 9, 3), duration=timedelta(), distance=0, elevation=0),)):
        result = total(rows)
        assert result["distance"] == 0 and result["elevation_gain"] == 0
        assert result["duration"] == timedelta() and result["partial"] is False


def test_controls_default_to_one_month_and_ignore_list_filters():
    st = MagicMock()
    st.session_state = {"activities_search": "no matches", "activities_sport": "Swimming"}
    st.columns.return_value = (MagicMock(), MagicMock())
    st.selectbox.side_effect = ("1 month", None)
    scope = load_summary(st)
    scope["_show_activity_summary"]((activity(date(2026, 9, 3)),), reference_day=date(2026, 9, 3))
    options = st.selectbox.call_args_list
    assert options[0].kwargs["index"] == 3
    assert options[0].kwargs["key"] == "activities_summary_period"
    assert options[1].kwargs["key"] == "activities_summary_sport"
    assert "10.00 km" in st.html.call_args.args[0]
    assert st.session_state["activities_search"] == "no matches"


def test_removed_sport_selection_is_reset_safely():
    st = MagicMock()
    st.session_state = {"activities_summary_sport": "Deleted sport", "activities_summary_period": "Old period"}
    st.columns.return_value = (MagicMock(), MagicMock())
    st.selectbox.side_effect = ("1 month", None)
    load_summary(st)["_show_activity_summary"]((), reference_day=date(2026, 9, 3))
    assert st.session_state["activities_summary_sport"] is None
    assert st.session_state["activities_summary_period"] == "1 month"
    assert "No activities" in st.caption.call_args.args[0]


def test_summary_uses_unfiltered_source_and_desktop_alignment_is_scoped():
    text = PATH.read_text(encoding="utf-8")
    tree = ast.parse(text)
    show = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "show_activities_page")
    calls = [n for n in ast.walk(show) if isinstance(n, ast.Call)]
    summary = next(n for n in calls if isinstance(n.func, ast.Name) and n.func.id == "_show_activity_summary")
    assert isinstance(summary.args[0], ast.Name) and summary.args[0].id == "all_activities"
    assert "@media (min-width: 1100px)" in text
    assert "@media (max-width: 1099px)" in text
    for key in ("activities_utility", "activities_bottom_slot", "activities_browser"):
        assert any(any(k.arg == "key" and isinstance(k.value, ast.Constant) and k.value.value == key
                       for k in n.keywords) for n in calls)
