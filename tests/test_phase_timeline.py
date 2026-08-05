"""
PerformanceLab

Tests for the reusable phase timeline.
"""

from datetime import date
from types import SimpleNamespace

from app.components.phase_timeline import (
    phase_range_segments,
    phase_segments,
    phase_timeline_from_phases_html,
    phase_timeline_html,
    phase_timeline_styles,
)

def phase_day(
    day: int,
    phase: str,
):
    return SimpleNamespace(
        day=date(
            2026,
            8,
            day,
        ),
        phase=phase,
    )


def test_groups_consecutive_phase_days():

    timeline = SimpleNamespace(
        days=(
            phase_day(3, "Build"),
            phase_day(4, "Build"),
            phase_day(5, "Peak"),
            phase_day(6, "Peak"),
            phase_day(7, "Race"),
        )
    )

    assert phase_segments(
        timeline
    ) == (
        (
            "Build",
            (
                date(2026, 8, 3),
                date(2026, 8, 4),
            ),
        ),
        (
            "Peak",
            (
                date(2026, 8, 5),
                date(2026, 8, 6),
            ),
        ),
        (
            "Race",
            (
                date(2026, 8, 7),
            ),
        ),
    )


def test_builds_phase_timeline_html():

    timeline = SimpleNamespace(
        days=(
            phase_day(3, "Build"),
            phase_day(4, "Peak"),
            phase_day(5, "Race"),
        )
    )

    result = phase_timeline_html(
        timeline=timeline,
        current_date=date(
            2026,
            8,
            4,
        ),
        visible_start=date(
            2026,
            8,
            3,
        ),
        visible_end=date(
            2026,
            8,
            5,
        ),
    )

    assert "Build" in result
    assert "Peak" in result
    assert "Race" in result
    assert (
        "weekly-phase-dot-current"
        in result
    )
    assert (
        "weekly-phase-dot-race"
        in result
    )
    assert "04 Aug 2026" in result


def test_returns_empty_timeline_without_data():

    assert (
        phase_timeline_html(
            timeline=None,
            current_date=date(
                2026,
                8,
                4,
            ),
            visible_start=date(
                2026,
                8,
                1,
            ),
            visible_end=date(
                2026,
                8,
                7,
            ),
        )
        == ""
    )


def test_exposes_shared_timeline_styles():

    styles = (
        phase_timeline_styles()
    )

    assert (
        ".weekly-phase-timeline"
        in styles
    )
    assert (
        ".weekly-phase-dot-current"
        in styles
    )

def test_expands_phase_ranges_into_daily_segments():

    phases = (
        SimpleNamespace(
            name="Build",
            start_date=date(
                2026,
                8,
                3,
            ),
            end_date=date(
                2026,
                8,
                4,
            ),
        ),
        SimpleNamespace(
            name="Race",
            start_date=date(
                2026,
                8,
                5,
            ),
            end_date=date(
                2026,
                8,
                5,
            ),
        ),
    )

    assert phase_range_segments(
        phases
    ) == (
        (
            "Build",
            (
                date(2026, 8, 3),
                date(2026, 8, 4),
            ),
        ),
        (
            "Race",
            (
                date(2026, 8, 5),
            ),
        ),
    )


def test_builds_timeline_from_phase_ranges():

    phases = (
        SimpleNamespace(
            name="Build",
            start_date=date(
                2026,
                8,
                3,
            ),
            end_date=date(
                2026,
                8,
                4,
            ),
        ),
        SimpleNamespace(
            name="Race",
            start_date=date(
                2026,
                8,
                5,
            ),
            end_date=date(
                2026,
                8,
                5,
            ),
        ),
    )

    result = (
        phase_timeline_from_phases_html(
            phases=phases,
            current_date=date(
                2026,
                8,
                4,
            ),
            visible_start=date(
                2026,
                8,
                3,
            ),
            visible_end=date(
                2026,
                8,
                5,
            ),
        )
    )

    assert "Build" in result
    assert "Race" in result
    assert (
        "weekly-phase-dot-current"
        in result
    )
    assert (
        "weekly-phase-dot-race"
        in result
    )
    assert "04 Aug 2026" in result

def test_timeline_shows_phase_date_ranges():

    phases = (
        SimpleNamespace(
            name="Build",
            start_date=date(
                2026,
                8,
                3,
            ),
            end_date=date(
                2026,
                8,
                16,
            ),
        ),
        SimpleNamespace(
            name="Race",
            start_date=date(
                2026,
                9,
                13,
            ),
            end_date=date(
                2026,
                9,
                13,
            ),
        ),
    )

    result = (
        phase_timeline_from_phases_html(
            phases=phases,
            current_date=date(
                2026,
                8,
                10,
            ),
            visible_start=date(
                2026,
                8,
                10,
            ),
            visible_end=date(
                2026,
                8,
                16,
            ),
        )
    )

    assert "03 – 16 Aug" in result
    assert "13 Sep 2026" in result


def test_timeline_marks_current_phase():

    phases = (
        SimpleNamespace(
            name="Build",
            start_date=date(
                2026,
                8,
                3,
            ),
            end_date=date(
                2026,
                8,
                16,
            ),
        ),
        SimpleNamespace(
            name="Peak",
            start_date=date(
                2026,
                8,
                17,
            ),
            end_date=date(
                2026,
                9,
                6,
            ),
        ),
    )

    result = (
        phase_timeline_from_phases_html(
            phases=phases,
            current_date=date(
                2026,
                8,
                20,
            ),
            visible_start=date(
                2026,
                8,
                17,
            ),
            visible_end=date(
                2026,
                8,
                23,
            ),
        )
    )

    assert (
        "weekly-phase-segment-current"
        in result
    )

    assert "Peak · week 1 of 3" in result


def test_timeline_shows_next_phase_countdown():

    phases = (
        SimpleNamespace(
            name="Peak",
            start_date=date(
                2026,
                8,
                17,
            ),
            end_date=date(
                2026,
                9,
                6,
            ),
        ),
        SimpleNamespace(
            name="Taper",
            start_date=date(
                2026,
                9,
                7,
            ),
            end_date=date(
                2026,
                9,
                12,
            ),
        ),
    )

    result = (
        phase_timeline_from_phases_html(
            phases=phases,
            current_date=date(
                2026,
                8,
                26,
            ),
            visible_start=date(
                2026,
                8,
                24,
            ),
            visible_end=date(
                2026,
                8,
                30,
            ),
        )
    )

    assert (
        "Next phase: Taper in 12 days"
        in result
    )


def test_timeline_styles_current_phase():

    styles = (
        phase_timeline_styles()
    )

    assert (
        ".weekly-phase-segment-current"
        in styles
    )

    assert (
        ".weekly-phase-footer"
        in styles
    )