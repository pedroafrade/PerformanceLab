"""Regression coverage for the shared 30-day window and dashboard presentation."""
import ast
from collections import namedtuple
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path
import runpy
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
RECENT = runpy.run_path(str(ROOT / "performancelab/presentation/recent_activity_summary.py"))


def functions(path, names, **scope):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), path, "exec"), scope)
    return scope


def workout(day, sport="Running", distance=10):
    return SimpleNamespace(date=day, sport=sport, distance=distance, duration=timedelta(hours=1))


def test_inclusive_window_and_shared_summary_do_not_mutate_history():
    end = date(2026, 9, 3)
    history = [workout(end-timedelta(days=30)), workout(end-timedelta(days=29)),
               workout(datetime(2026, 9, 3, tzinfo=timezone.utc), "Trail Running", 5),
               workout(end, "Cycling", 40), workout(end+timedelta(days=1))]
    before = [vars(w).copy() for w in history]
    result = RECENT["recent_activity_summary"](history, end)
    assert result.workouts == 3 and result.training_days == 2
    assert result.total_duration == timedelta(hours=3)
    assert result.running_distance == 15 and result.cycling_distance == 40
    assert result.sports == 3
    assert [vars(w) for w in history] == before


@pytest.mark.parametrize("value", [None, float("nan"), float("inf"), -1, "invalid"])
def test_missing_distance_is_not_reported_as_zero(value):
    end = date(2026, 9, 3)
    result = RECENT["recent_activity_summary"]([workout(end, distance=value)], end)
    assert result.running_distance is None and result.running_missing == 1
    assert result.cycling_distance == 0


def test_partial_and_empty_totals():
    end = date(2026, 9, 3)
    result = RECENT["recent_activity_summary"]([workout(end, distance=None), workout(end, distance=3)], end)
    assert result.running_distance == 3 and result.running_missing == 1
    empty = RECENT["recent_activity_summary"]([], end)
    assert empty.workouts == 0 and empty.running_distance == 0


@dataclass(frozen=True)
class Card:
    key: str = "running-pace"
    icon: str = "≈"
    label: str = "Running pace"
    value: str = "5:00"
    trend: str = "Stable"
    context: str = "28 days"


@pytest.mark.parametrize("sport,value,label", [("Running", "10.0 km", "Total Running Distance"),
                                               ("Cycling", "40.0 km", "Total Cycling Distance")])
def test_distance_card_switches_without_changing_original_card(sport, value, label):
    helper = functions("app/components/development_page.py", {"_distance_summary_card"}, replace=replace)
    totals = RECENT["recent_activity_summary"]([workout(date.today()), workout(date.today(), "Cycling", 40)], date.today())
    original = Card()
    card = helper["_distance_summary_card"](original, totals, sport)
    assert card.label == label and card.value == value
    assert card.trend == "Last 30 days" and original == Card()


def test_selection_is_saved_separately_from_widget_state():
    st = SimpleNamespace(session_state={"_development_distance_sport": "Cycling"})
    scope = functions("app/components/development_page.py", {"_remember_distance_sport"}, st=st)
    scope["_remember_distance_sport"]()
    assert st.session_state["development_distance_sport"] == "Cycling"


@pytest.mark.parametrize("choice", ["Running", "Cycling", "invalid"])
def test_four_cards_render_with_one_distance_menu(choice):
    st = MagicMock()
    st.session_state = {"development_distance_sport": choice}
    st.columns.return_value = [MagicMock() for _ in range(4)]
    names = {"_show_development_summary_cards", "_development_summary_cards_html",
             "_development_summary_styles", "_distance_summary_card", "_remember_distance_sport"}
    scope = functions("app/components/development_page.py", names, st=st, replace=replace,
                      escape=escape, recent_activity_summary=RECENT["recent_activity_summary"])
    cards = [Card(key="duration"), Card(), Card(key="load"), Card(key="vo2")]
    athlete = SimpleNamespace(history=[workout(date.today()), workout(date.today(), "Cycling", 40)])
    scope["_show_development_summary_cards"](cards, athlete, date.today())
    st.columns.assert_called_once_with(4, gap="small")
    st.popover.assert_called_once()
    markup = " ".join(call.args[0] for call in st.markdown.call_args_list)
    assert ("Total Cycling Distance" if choice == "Cycling" else "Total Running Distance") in markup


def test_recovery_uses_exact_current_state_and_shared_today_context():
    shared = runpy.run_path(str(ROOT / "app/components/current_state_summary.py"))
    capture = MagicMock()
    Metric = namedtuple("Metric", "value label")
    Detail = namedtuple("Detail", "label value")
    scope = functions("app/components/dashboard/cards/recovery_card.py", {"recovery_card"},
                      RecoveryCardData=object, CurrentStateSummaryData=shared["CurrentStateSummaryData"],
                      _recovery_context=shared["_recovery_context"], MetricCardMetric=Metric,
                      MetricCardDetail=Detail, metric_card_body=capture,
                      metric_status_color=lambda status: "#16a34a")
    state = SimpleNamespace(recovery_score=64.7, recovery_balance=12.3, recovery_status="Good",
                            ctl=20, atl=15, form=5, reference_time=datetime(2026, 9, 3, 12),
                            hours_since_last_workout=23, recovery_is_time_aware=True,
                            recovery_recommendation="Ready for a normal training session.")
    scope["recovery_card"](None, current_state=state)
    result = capture.call_args.kwargs
    assert result["metrics"][0].value == "65"
    assert result["progress"] == state.recovery_score
    assert result["details"][0].value == state.recovery_status
    assert "23 h since last session" in result["details"][1].value
    assert "Updated 12:00" in result["details"][1].value


@pytest.mark.parametrize("status,color", [("Good", "#16a34a"), ("Recovery needed", "#dc2626"),
    ("Optimal", "#16a34a"), ("High load", "#ea580c"), ("Overreaching", "#dc2626"),
    ("No load", "#6b7280")])
def test_status_colours_and_progress_clamping(status, color):
    scope = functions("app/components/dashboard/cards/metric_card_body.py",
                      {"metric_status_color", "_progress_html"}, escape=escape)
    assert scope["metric_status_color"](status) == color
    assert color in scope["_progress_html"](50, color)
    assert "width:100%" in scope["_progress_html"](150, color)
    assert "width:0%" in scope["_progress_html"](-1, color)


def test_dashboard_removes_only_requested_widgets_and_uses_shared_window():
    source = (ROOT / "app/components/dashboard/dashboard_view.py").read_text(encoding="utf-8")
    assert 'title="Performance Status"' not in source
    assert 'title="Performance"' not in source and 'title="Monthly Summary"' not in source
    assert 'title="Training Load & Recovery"' in source
    assert 'title="Estimated Recovery"' not in source
    assert 'title="Training Load"' not in source
    assert "(1, 3.2, 1)" in source
    assert "_show_activity_summary(activities," in source
    assert "training_state_at(reference_time=reference_time)" in source
