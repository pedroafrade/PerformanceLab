"""
Tests for the Today page.
"""

from datetime import timedelta
from types import SimpleNamespace

from app.components.today_page import (
    _duration_label,
    _today_session_metadata,
    _today_session_status,
    _today_session_title,
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