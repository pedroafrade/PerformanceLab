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
    assert 'with st.expander("Strategy adviser"' in source
    assert "len(weekdays) < 3" in source
    assert "preference is not a safety rule" in source
    assert 'category = f"{recurring_title} sessions"' in source
    assert 'r"^T\\d+[_\\s-]*"' in source
    assert 'category = "Cycling"' in source
    assert "weekend_count / len(weekdays) >= 0.6" in source
