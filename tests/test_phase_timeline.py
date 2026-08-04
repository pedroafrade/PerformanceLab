"""
PerformanceLab

Tests for the reusable phase timeline.
"""

from datetime import date
from types import SimpleNamespace

from app.components.phase_timeline import (
    phase_segments,
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