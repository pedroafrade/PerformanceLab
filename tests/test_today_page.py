"""
Tests for the Today page.
"""

from datetime import timedelta
from types import SimpleNamespace

from app.components.today_page import (
    _activity_outcome_summary,
    _duration_label,
    _form_label,
    _outcome_label,
    _today_session_metadata,
    _today_session_status,
    _today_session_title,
    _readiness_score_label,
    _recent_load_label,
    show_today_page,
)


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


def test_formats_today_duration():

    assert (
        _duration_label(
            timedelta(
                minutes=45,
            )
        )
        == "45 min"
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

def test_formats_activity_outcome():

    activity = SimpleNamespace(
        outcome_status="substitute",
        planned_title="Long Run",
        load_difference=744.0,
    )

    assert (
        _outcome_label(
            "substitute"
        )
        == "Substitute"
    )

    assert (
        _activity_outcome_summary(
            activity
        )
        == (
            "Substitute · "
            "Planned: Long Run · "
            "Load difference: +744 AU"
        )
    )


def test_formats_activity_outside_plan():

    activity = SimpleNamespace(
        outcome_status="outside_plan",
        planned_title=None,
        load_difference=None,
    )

    assert (
        _activity_outcome_summary(
            activity
        )
        == "Outside plan"
    )

def test_summarises_missing_recent_activity():

    assert (
        _activity_outcome_summary(
            None
        )
        == "No recent activity is available."
    )

def test_formats_daily_readiness():

    assert (
        _readiness_score_label(
            72
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