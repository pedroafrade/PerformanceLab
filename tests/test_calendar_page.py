"""
Tests for the monthly calendar page.
"""

from datetime import date
from types import SimpleNamespace

from app.components.calendar_page import (
    _calendar_html,
    _calendar_item_label,
    _phase_label,
    _shift_month,
    show_calendar_page,
)
from performancelab.presentation import (
    CalendarDayData,
    CalendarItemData,
    CalendarMonthData,
)


def test_show_calendar_page_exists():

    assert callable(
        show_calendar_page
    )


def test_shifts_month_across_year_boundary():

    assert _shift_month(
        date(
            2026,
            1,
            1,
        ),
        -1,
    ) == date(
        2025,
        12,
        1,
    )

    assert _shift_month(
        date(
            2026,
            12,
            1,
        ),
        1,
    ) == date(
        2027,
        1,
        1,
    )


def test_event_label_includes_priority():

    item = CalendarItemData(
        kind="event",
        title="Sealand",
        sport="Road Running",
        priority="A",
    )

    assert _calendar_item_label(
        item
    ) == "[A] Sealand"


def test_calendar_html_escapes_titles():

    dangerous_title = (
        "<script>alert('x')</script>"
    )

    item = CalendarItemData(
        kind="completed",
        title=dangerous_title,
        sport="Running",
    )

    day = CalendarDayData(
        day=date(
            2026,
            8,
            3,
        ),
        is_current_month=True,
        is_today=True,
        phase="Peak",
        items=(
            item,
        ),
    )

    calendar = CalendarMonthData(
        year=2026,
        month=8,
        weeks=(
            (
                day,
            ),
        ),
    )

    html = _calendar_html(
        calendar
    )

    assert dangerous_title not in html
    assert "&lt;script&gt;" in html
    assert "training-calendar-day today" in html
    assert "PEAK" in html


def test_plain_item_label_uses_title():

    item = SimpleNamespace(
        kind="planned",
        priority=None,
        title="Long Run",
    )

    assert _calendar_item_label(
        item
    ) == "Long Run"


def test_formats_calendar_phase_progress():

    calendar_day = CalendarDayData(
        day=date(
            2026,
            8,
            14,
        ),
        is_current_month=True,
        is_today=True,
        phase="Regeneration",
        phase_day_number=2,
        phase_total_days=5,
    )

    assert (
        _phase_label(
            calendar_day
        )
        == "REGENERATION - d2 of 5"
    )


def test_calendar_html_contains_day_details():

    item = CalendarItemData(
        kind="planned",
        title="Easy Run",
        sport="Running",
        summary=(
            "1h05 · Z2 · 121–156 bpm"
        ),
    )

    calendar_day = CalendarDayData(
        day=date(
            2026,
            8,
            14,
        ),
        is_current_month=True,
        is_today=True,
        phase="Regeneration",
        items=(
            item,
        ),
        phase_day_number=2,
        phase_total_days=5,
    )

    calendar = CalendarMonthData(
        year=2026,
        month=8,
        weeks=(
            (
                calendar_day,
            ),
        ),
    )

    html = _calendar_html(
        calendar,
        selected_day=date(
            2026,
            8,
            14,
        ),
    )

    assert (
        "#calendar-detail-2026-08-14"
        in html
    )

    assert (
        "?calendar_day="
        not in html
    )

    assert (
        "training-calendar-day selected today"
        in html
    )

    assert (
        "1h05 · Z2 · 121–156 bpm"
        in html
    )

    assert (
        "REGENERATION - d2 of 5"
        in html
    )


def test_calendar_html_marks_rest_day():

    calendar_day = CalendarDayData(
        day=date(
            2026,
            8,
            15,
        ),
        is_current_month=True,
        is_today=False,
        phase="Regeneration",
        is_rest_day=True,
    )

    calendar = CalendarMonthData(
        year=2026,
        month=8,
        weeks=(
            (
                calendar_day,
            ),
        ),
    )

    html = _calendar_html(
        calendar
    )

    assert "Rest day" in html
    assert (
        "training-calendar-rest"
        in html
    )

def test_calendar_selection_does_not_reload_page():

    calendar_day = CalendarDayData(
        day=date(
            2026,
            8,
            14,
        ),
        is_current_month=True,
        is_today=True,
        phase="Peak",
    )

    calendar = CalendarMonthData(
        year=2026,
        month=8,
        weeks=(
            (
                calendar_day,
            ),
        ),
    )

    html = _calendar_html(
        calendar,
        selected_day=date(
            2026,
            8,
            14,
        ),
    )

    assert (
        'href="#calendar-detail-2026-08-14"'
        in html
    )

    assert 'target="_self"' not in html
    assert "?calendar_day=" not in html