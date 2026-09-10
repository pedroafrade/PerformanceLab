from dataclasses import replace
from datetime import date, datetime, timedelta

from performancelab.training.planning import (
    PlannedWorkout,
    assess_plan_builder_change,
)


def workout(day, title, intensity="Easy", minutes=45):
    return PlannedWorkout(
        scheduled_at=datetime(2026, 9, day, 8),
        sport="Running",
        title=title,
        intensity=intensity,
        duration=timedelta(minutes=minutes),
    )


def test_warns_about_demanding_sessions_without_recovery():
    baseline = (
        workout(10, "Tempo Run", "Hard"),
        workout(13, "Hill Reps", "Hard"),
    )
    revised = (
        baseline[0],
        replace(
            baseline[1],
            scheduled_at=datetime(2026, 9, 11, 8),
        ),
    )

    result = assess_plan_builder_change(
        baseline_workouts=baseline,
        revised_workouts=revised,
        reference_day=date(2026, 9, 9),
    )

    assert result.status == "warning"
    assert "48 hours" in result.messages[0]
    assert any(
        "Move one demanding session" in recommendation
        for recommendation in result.recommendations
    )


def test_blocks_demanding_session_immediately_before_race():
    revised = (
        workout(12, "Hill Reps", "Hard"),
        workout(13, "Race", "Race effort", 60),
    )

    result = assess_plan_builder_change(
        baseline_workouts=(),
        revised_workouts=revised,
        reference_day=date(2026, 9, 9),
    )

    assert result.blocked is True
    assert "compromise taper" in result.messages[0]
    assert any(
        "replace it with an easy session" in recommendation
        for recommendation in result.recommendations
    )


def test_reports_long_run_spacing_and_weekly_load_together():
    baseline = (
        workout(14, "Long Run", "Easy", 60),
        workout(16, "Tempo Run", "Hard", 30),
    )
    revised = (
        baseline[0],
        replace(
            baseline[1],
            scheduled_at=datetime(2026, 9, 15, 8),
            duration=timedelta(minutes=75),
        ),
    )

    result = assess_plan_builder_change(
        baseline_workouts=baseline,
        revised_workouts=revised,
        reference_day=date(2026, 9, 10),
    )

    assert any("Long Run" in message for message in result.messages)
    assert any("Weekly load" in message for message in result.messages)
    assert len(result.recommendations) >= 2
    assert result.blocked is True
