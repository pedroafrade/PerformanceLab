"""
Tests for the complete PlanPresenter.
"""

from dataclasses import FrozenInstanceError
from datetime import date, datetime, timedelta

import pytest

from performancelab.history import (
    History,
)
from performancelab.presentation import (
    PlanPresenter,
)
from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
)
from performancelab.workout import (
    Workout,
)


def planned_workout(
    *,
    day: int,
    title: str,
    intensity: str,
    duration_minutes: int,
    phase: str,
) -> PlannedWorkout:

    return PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            day,
            8,
            0,
        ),
        sport="Running",
        title=title,
        duration=timedelta(
            minutes=duration_minutes,
        ),
        intensity=intensity,
        phase=phase,
    )


def test_groups_complete_plan_by_week():

    first = planned_workout(
        day=4,
        title="Easy Run",
        intensity="Easy",
        duration_minutes=60,
        phase="Build",
    )

    second = planned_workout(
        day=6,
        title="LT2 Run",
        intensity="Hard",
        duration_minutes=45,
        phase="Build",
    )

    third = planned_workout(
        day=11,
        title="Hill Run",
        intensity="Hard",
        duration_minutes=60,
        phase="Peak",
    )

    plan = TrainingPlan(
        start_date=date(
            2026,
            8,
            1,
        ),
        end_date=date(
            2026,
            8,
            31,
        ),
        workouts=[
            first,
            second,
            third,
        ],
    )

    result = PlanPresenter(
        plan=plan,
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            3,
        )
    )

    assert len(result.weeks) == 2

    assert (
        result.weeks[0].start_date
        == date(2026, 8, 3)
    )

    assert tuple(
        workout.title
        for workout in (
            result.weeks[0].workouts
        )
    ) == (
        "Easy Run",
        "LT2 Run",
    )

    assert (
        result.weeks[0].planned_load
        == pytest.approx(495)
    )

    assert (
        result.weeks[1].phase
        == "Peak"
    )


def test_attaches_workout_outcomes():

    completed = Workout(
        workout_id="completed-easy"
    )
    completed.info.date = date(
        2026,
        8,
        4,
    )
    completed.info.sport = "Running"
    completed.info.duration = timedelta(
        minutes=60,
    )
    completed.feedback.rpe = 3

    equivalent = planned_workout(
        day=4,
        title="Easy Run",
        intensity="Easy",
        duration_minutes=60,
        phase="Build",
    )

    pending = planned_workout(
        day=6,
        title="LT2 Run",
        intensity="Hard",
        duration_minutes=45,
        phase="Build",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                equivalent,
                pending,
            ]
        ),
        history=History(
            workouts=[
                completed,
            ]
        ),
    ).build(
        reference_day=date(
            2026,
            8,
            5,
        )
    )

    assert tuple(
        workout.status
        for workout in (
            result.weeks[0].workouts
        )
    ) == (
        "equivalent",
        "pending",
    )


def test_marks_past_session_as_missed():

    missed = planned_workout(
        day=4,
        title="Easy Run",
        intensity="Easy",
        duration_minutes=60,
        phase="Build",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                missed,
            ]
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            5,
        )
    )

    assert (
        result.weeks[0]
        .workouts[0]
        .status
        == "missed"
    )


def test_empty_plan_has_no_weeks():

    result = PlanPresenter(
        plan=TrainingPlan(),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            3,
        )
    )

    assert result.weeks == ()


def test_complete_plan_data_is_immutable():

    result = PlanPresenter(
        plan=TrainingPlan(),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            3,
        )
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        result.weeks = ()