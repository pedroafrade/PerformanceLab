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
    assert result.weekly_load_changes


def test_long_run_spacing_is_caution_without_an_independent_blocker():
    baseline = (
        workout(14, "Long Run", "Easy", 60),
        workout(16, "Hill Reps", "Hard", 30),
    )
    revised = (
        baseline[0],
        replace(baseline[1], scheduled_at=datetime(2026, 9, 15, 8)),
    )

    result = assess_plan_builder_change(
        baseline_workouts=baseline,
        revised_workouts=revised,
        reference_day=date(2026, 9, 10),
    )

    assert result.status == "warning"
    assert result.blocked is False
    assert any("Long Run" in message for message in result.messages)


def test_reports_weekly_load_before_after_and_percentage():
    baseline = (workout(14, "Easy Run", "Easy", 40),)
    revised = (replace(baseline[0], duration=timedelta(minutes=50)),)

    result = assess_plan_builder_change(
        baseline_workouts=baseline,
        revised_workouts=revised,
        reference_day=date(2026, 9, 10),
    )

    week, old_load, new_load, growth = result.weekly_load_changes[0]
    assert week == date(2026, 9, 14)
    assert new_load > old_load
    assert growth == (new_load - old_load) / old_load


def test_high_percentage_with_small_absolute_change_is_information_only():
    baseline = (workout(14, "Easy Run", "Easy", 10),)
    revised = (replace(baseline[0], duration=timedelta(minutes=14)),)

    result = assess_plan_builder_change(
        baseline_workouts=baseline,
        revised_workouts=revised,
        reference_day=date(2026, 9, 10),
    )

    assert result.blocked is False
    assert any(issue.severity == "information" for issue in result.issues)


def test_weekly_load_blocks_only_when_percentage_and_absolute_growth_are_high():
    baseline = (workout(14, "Easy Run", "Easy", 100),)
    revised = (replace(baseline[0], duration=timedelta(minutes=240)),)

    result = assess_plan_builder_change(
        baseline_workouts=baseline,
        revised_workouts=revised,
        reference_day=date(2026, 9, 10),
    )

    weekly_issue = next(
        issue for issue in result.issues if issue.rule == "weekly_load"
    )
    assert weekly_issue.severity == "blocked"
    assert weekly_issue.week == date(2026, 9, 14)
    assert "AU" in weekly_issue.message


def test_blocked_move_proposes_a_deterministic_safe_date():
    baseline = (
        workout(16, "Hill Reps", "Hard", 45),
        workout(13, "Race", "Race effort", 60),
    )
    revised = (
        replace(
            baseline[0],
            scheduled_at=datetime(2026, 9, 12, 8),
        ),
        baseline[1],
    )

    result = assess_plan_builder_change(
        baseline_workouts=baseline,
        revised_workouts=revised,
        reference_day=date(2026, 9, 10),
    )

    assert result.blocked is True
    assert result.alternatives
    assert result.alternatives[0].workout_id == baseline[0].planned_workout_id
    assert result.alternatives[0].target_day != date(2026, 9, 12)


def test_board_can_apply_the_suggested_move_in_one_action():
    source = (
        __import__("pathlib").Path(
            "app/components/plan_builder_board/index.html"
        ).read_text(encoding="utf-8")
    )

    assert 'type==="plan-builder:apply-alternative"' in source
    assert 'action:"move"' in source
    assert "workout_id:event.data.workout_id" in source
