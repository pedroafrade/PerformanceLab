"""
Tests for the Today page.
"""

from datetime import datetime, timedelta
from types import SimpleNamespace

from app.components.today_page import (
    _adaptation_change_label,
    _duration_label,
    _form_label,
    _guidance_item_html,
    _navigate_to,
    _readiness_score_label,
    _recent_load_label,
    _recovery_context_label,
    _recovery_updated_label,
    _session_step_html,
    _today_session_metadata,
    _today_session_status,
    _today_session_title,
    show_today_page,
)

import app.components.today_page as today_page


def create_session(
    *,
    title="Easy Run",
    completed=False,
    outcome_status=None,
):
    return SimpleNamespace(
        title=title,
        sport="Running",
        duration=timedelta(
            minutes=45,
        ),
        intensity="Easy",
        structure=(),
        completed=completed,
        completed_title=(
            "Morning Run"
            if completed
            else None
        ),
        completed_sport=(
            "Running"
            if completed
            else None
        ),
        outcome_status=(
            outcome_status
        ),
    )


def test_show_today_page_exists():

    assert callable(
        show_today_page
    )


def test_navigates_from_today(
    monkeypatch,
):

    session_state = SimpleNamespace(
        page="today"
    )

    monkeypatch.setattr(
        today_page.st,
        "session_state",
        session_state,
    )

    _navigate_to(
        "calendar"
    )

    assert session_state.page == "calendar"


def test_formats_today_duration():

    assert (
        _duration_label(
            timedelta(
                minutes=45,
            )
        )
        == "45 min"
    )


def test_formats_latest_adaptation_change():

    adaptation = SimpleNamespace(
        previous_minutes=50,
        revised_minutes=38,
    )

    assert (
        _adaptation_change_label(
            adaptation
        )
        == "50 min → 38 min"
    )

    assert (
        _duration_label(
            timedelta(
                minutes=90,
            )
        )
        == "1h 30m"
    )


def test_displays_planned_session():

    session = create_session()

    assert (
        _today_session_title(
            session
        )
        == "Easy Run"
    )

    assert (
        _today_session_status(
            session
        )
        == "Planned"
    )

    assert (
        _today_session_metadata(
            session
        )
        == "Running · 45 min · Easy"
    )


def test_displays_completed_session():

    session = create_session(
        completed=True,
        outcome_status="equivalent",
    )

    assert (
        _today_session_title(
            session
        )
        == "Morning Run"
    )

    assert (
        _today_session_status(
            session
        )
        == "Equivalent"
    )


def test_displays_rest_day():

    session = create_session(
        title=None,
    )

    assert (
        _today_session_title(
            session
        )
        == "Rest day"
    )

    assert (
        _today_session_status(
            session
        )
        == "Recovery"
    )


def test_builds_monochrome_session_step():

    result = _session_step_html(
        index=2,
        step="3×7 min at LT2",
    )

    assert ">2<" in result
    assert "3×7 min at LT2" in result
    assert "color:" not in result
    assert "background:" not in result


def test_escapes_session_step():

    result = _session_step_html(
        index=1,
        step="Run < controlled",
    )

    assert "Run &lt; controlled" in result


def test_builds_monochrome_guidance_item():

    result = _guidance_item_html(
        index=1,
        text="Recovery < expected",
    )

    assert ">1<" in result
    assert "Recovery &lt; expected" in result
    assert "color:" not in result
    assert "background:" not in result


def test_formats_daily_readiness():

    assert (
        _readiness_score_label(
            72.3417269
        )
        == "72/100"
    )

    assert (
        _form_label(
            22.3
        )
        == "+22.3"
    )

    assert (
        _form_label(
            -7.25
        )
        == "-7.2"
    )

    assert (
        _recent_load_label(
            234.94
        )
        == "234.9"
    )

def test_formats_time_aware_recovery_context():

    readiness = SimpleNamespace(
        recovery_status="Moderate",
        recovery_balance=-9.4,
        recovery_is_time_aware=True,
        hours_since_last_workout=(
            30.4
        ),
        reference_time=datetime(
            2026,
            8,
            12,
            14,
            5,
        ),
    )

    assert (
        _recovery_context_label(
            readiness
        )
        == (
            "Moderate · "
            "Balance -9.4 · "
            "30 h since last session"
        )
    )

    assert (
        _recovery_updated_label(
            readiness
        )
        == "Updated 14:05"
    )


def test_formats_daily_recovery_fallback():

    readiness = SimpleNamespace(
        recovery_status=(
            "Recovery needed"
        ),
        recovery_balance=-18.0,
        recovery_is_time_aware=False,
        hours_since_last_workout=None,
        reference_time=datetime(
            2026,
            8,
            12,
            18,
            0,
        ),
    )

    assert (
        _recovery_context_label(
            readiness
        )
        == (
            "Recovery needed · "
            "Balance -18.0 · "
            "Daily estimate"
        )
    )


def test_omits_missing_recovery_update_time():

    readiness = SimpleNamespace(
        reference_time=None,
    )

    assert (
        _recovery_updated_label(
            readiness
        )
        is None
    )