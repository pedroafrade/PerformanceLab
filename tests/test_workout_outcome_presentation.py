"""
PerformanceLab

Tests for workout outcome presentation.
"""

from datetime import date, datetime, timedelta

from performancelab import (
    History,
    create_workout,
)
from performancelab.presentation.planning_presenter import (
    PlanningPresenter,
)
from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
    WeeklyPlan,
)


def make_planned_workout():

    return PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            4,
            8,
            0,
        ),
        sport="Running",
        title="Easy Run",
        duration=timedelta(
            minutes=60,
        ),
        intensity="Easy",
    )


def make_presenter(
    *,
    history,
):

    workout = make_planned_workout()

    training_plan = TrainingPlan(
        workouts=[
            workout,
        ],
    )

    weekly_plan = WeeklyPlan(
        start_date=date(
            2026,
            8,
            4,
        ),
        end_date=date(
            2026,
            8,
            10,
        ),
        workouts=[
            workout,
        ],
    )

    return PlanningPresenter(
        plan=weekly_plan,
        history=history,
        reference=datetime(
            2026,
            8,
            5,
            12,
            0,
        ),
        training_plan=training_plan,
    )


def test_presenter_exposes_equivalent_outcome():

    completed = create_workout(
        sport="Running",
        workout_date=datetime(
            2026,
            8,
            4,
            8,
            5,
        ),
        distance=10.0,
        duration=timedelta(
            minutes=60,
        ),
        elevation_gain=0.0,
        rpe=3,
    )

    planning = make_presenter(
        history=History(
            workouts=[
                completed,
            ]
        ),
    ).build()

    assert (
        planning.weekly_plan.days[0]
        .outcome_status
        == "equivalent"
    )


def test_presenter_exposes_missed_outcome():

    planning = make_presenter(
        history=History(),
    ).build()

    assert (
        planning.weekly_plan.days[0]
        .outcome_status
        == "missed"
    )