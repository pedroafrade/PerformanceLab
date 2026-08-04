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
    PlanProgressionPointData,
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
        result.weeks[0]
        .workouts[0]
        .planned_load
        == pytest.approx(180)
    )

    assert (
        result.weeks[0]
        .workouts[1]
        .planned_load
        == pytest.approx(315)
    )

    assert not (
        result.weeks[0]
        .workouts[0]
        .is_race
    )

    assert not (
        result.weeks[0]
        .workouts[1]
        .is_race
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
    assert result.progression == ()


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

def test_builds_immutable_plan_progression():

    first = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            4,
            8,
            0,
        ),
        sport="Trail Running",
        title="Easy Run",
        duration=timedelta(
            minutes=60,
        ),
        distance=10.0,
        elevation_gain=200.0,
        intensity="Easy",
        phase="Build",
    )

    second = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            6,
            8,
            0,
        ),
        sport="Trail Running",
        title="Long Run",
        duration=timedelta(
            minutes=90,
        ),
        distance=15.0,
        elevation_gain=400.0,
        intensity="Easy to moderate",
        phase="Build",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                first,
                second,
            ]
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            3,
        )
    )

    assert len(
        result.progression
    ) == 1

    point = result.progression[0]

    assert isinstance(
        point,
        PlanProgressionPointData,
    )
    assert (
        point.week_start
        == date(2026, 8, 3)
    )
    assert point.phase == "Build"
    assert (
        point.duration_minutes
        == pytest.approx(150.0)
    )
    assert (
        point.distance
        == pytest.approx(25.0)
    )
    assert (
        point.elevation_gain
        == pytest.approx(600.0)
    )
    assert (
        point.planned_load
        > 0
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        point.distance = 30.0

def test_marks_race_session_for_presentation():

    race = planned_workout(
        day=13,
        title="Race",
        intensity="Race effort",
        duration_minutes=120,
        phase="Race",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                race,
            ]
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            3,
        )
    )

    assert (
        result.weeks[0]
        .workouts[0]
        .is_race
    )