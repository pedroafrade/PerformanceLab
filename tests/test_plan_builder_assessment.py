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
