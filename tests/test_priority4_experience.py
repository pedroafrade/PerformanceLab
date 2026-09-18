from datetime import date
from pathlib import Path

from performancelab import Athlete
from performancelab.recovery_log import RecoveryLogEntry
from performancelab.storage.json import athlete_from_dict, athlete_to_dict


def test_recovery_log_round_trips_with_private_athlete_export():
    athlete = Athlete(name="Pedro")
    athlete.recovery_log.append(RecoveryLogEntry(
        day=date(2026, 9, 18), category="Pain", body_area="Left calf",
        severity=4, notes="After hills",
    ))

    restored = athlete_from_dict(athlete_to_dict(athlete))

    assert restored.recovery_log == athlete.recovery_log


def test_today_reuses_daily_brief_and_preserves_card_key():
    source = Path("app/components/today_page.py").read_text(encoding="utf-8")
    app = Path("app/app.py").read_text(encoding="utf-8")
    assert 'key="today-recommendation-card"' in source
    assert '"DAILY BRIEF"' in source
    assert "daily_brief_resolution=daily_brief_resolution" in app
    assert 'key="today_brief_recovery_row"' in source
    assert "brief_column, recovery_column" in source


def test_today_contains_equivalents_and_private_recovery_controls():
    source = Path("app/components/today_page.py").read_text(encoding="utf-8")
    assert 'key="today_session_equivalent"' in source
    assert "Cycling reduces impact" in source
    assert "running economy, tendon loading" in source
    assert "calf raises, split squats and hip hinges" in source
    assert 'key="today_recovery_log"' in source
    assert "does not diagnose" in source


def test_strategy_adviser_is_local_six_month_pattern_analysis():
    source = Path("app/components/plan_page.py").read_text(encoding="utf-8")
    assert "timedelta(days=183)" in source
    assert '"Build plan", "Typical week", "Plan recovery"' in source
    assert "def _typical_week" in source
    assert "def _typical_week_html" in source
    assert 'class="typical-week-slot"' in source
    assert "range(start_hour, end_hour + 1)" in source
    assert "repeat(7,minmax(8rem,1fr))" in source
    assert "len(weekdays) < 3" in source
    assert "not a safety rule" in source
    assert 'category = f"{recurring_title} sessions"' in source
    assert 'r"^T\\d+[_\\s-]*"' in source
    assert 'category = "Cycling"' in source
    assert "weekend_count / len(weekdays) >= 0.6" in source


def test_pre_race_session_is_not_treated_as_an_event():
    source = Path("app/components/plan_page.py").read_text(encoding="utf-8")
    assert 'title in {"race", "competition", "event"}' in source
    assert '"race" in str(workout.title' not in source


def test_today_rows_share_the_same_grid_and_have_explicit_spacing():
    source = Path("app/components/today_page.py").read_text(encoding="utf-8")
    assert source.count("[1.7, 1]") >= 2
    assert ".st-key-today_brief_recovery_row" in source
    assert "margin-bottom: 1.25rem" in source
