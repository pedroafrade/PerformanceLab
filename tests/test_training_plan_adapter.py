"""
PerformanceLab

Tests for incremental training-plan adaptation.
"""

from datetime import date, datetime, timedelta

import pytest

from performancelab.analysis.training_state import (
    TrainingState,
)
from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
    TrainingPlanAdapter,
    WorkoutOutcome,
    WorkoutOutcomeStatus,
)


def make_training_state() -> TrainingState:

    return TrainingState(
        ctl=40.0,
        atl=35.0,
        tsb=5.0,
        acute_chronic_ratio=1.0,
        monotony=1.0,
        strain=350.0,
        consistency=0.8,
        weekly_frequency=4.0,
        days_since_last_workout=0,
        recent_training_load=300.0,
    )


def make_plan() -> TrainingPlan:

    return TrainingPlan(
        plan_id="persistent-plan",
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
            PlannedWorkout(
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
            ),
            PlannedWorkout(
                scheduled_at=datetime(
                    2026,
                    8,
                    6,
                    8,
                    0,
                ),
                sport="Running",
                title="Tempo Run",
                duration=timedelta(
                    minutes=50,
                ),
                intensity="Tempo",
            ),
        ],
    )


def test_equivalent_outcome_preserves_plan():

    plan = make_plan()

    outcome = WorkoutOutcome(
        planned_workout=plan.workouts[0],
        completed_workout=None,
        status=(
            WorkoutOutcomeStatus.EQUIVALENT
        ),
        planned_load=180.0,
        completed_load=180.0,
    )

    adapted = TrainingPlanAdapter().adapt(
        plan=plan,
        outcomes=(
            outcome,
        ),
        training_state=make_training_state(),
        reference_day=date(
            2026,
            8,
            5,
        ),
    )

    assert adapted is not plan
    assert adapted.plan_id == plan.plan_id
    assert adapted.start_date == plan.start_date
    assert adapted.end_date == plan.end_date
    assert adapted.workouts == plan.workouts


def test_pending_outcome_preserves_future_workout():

    plan = make_plan()

    outcome = WorkoutOutcome(
        planned_workout=plan.workouts[1],
        completed_workout=None,
        status=(
            WorkoutOutcomeStatus.PENDING
        ),
        planned_load=250.0,
        completed_load=None,
    )

    adapted = TrainingPlanAdapter().adapt(
        plan=plan,
        outcomes=(
            outcome,
        ),
        training_state=make_training_state(),
        reference_day=date(
            2026,
            8,
            5,
        ),
    )

    assert (
        adapted.workouts[1]
        == plan.workouts[1]
    )


def test_unimplemented_adaptation_fails_explicitly():

    plan = make_plan()

    outcome = WorkoutOutcome(
        planned_workout=plan.workouts[0],
        completed_workout=None,
        status=(
            WorkoutOutcomeStatus.MISSED
        ),
        planned_load=180.0,
        completed_load=None,
    )

    with pytest.raises(
        NotImplementedError,
        match="missed",
    ):
        TrainingPlanAdapter().adapt(
            plan=plan,
            outcomes=(
                outcome,
            ),
            training_state=(
                make_training_state()
            ),
            reference_day=date(
                2026,
                8,
                5,
            ),
        )