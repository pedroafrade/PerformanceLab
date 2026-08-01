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


def make_training_state(
    *,
    tsb=5.0,
) -> TrainingState:

    return TrainingState(
        ctl=40.0,
        atl=35.0,
        tsb=tsb,
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
            PlannedWorkout(
                scheduled_at=datetime(
                    2026,
                    8,
                    8,
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
        ],
    )


def make_outcome(
    *,
    plan,
    status,
    planned_load,
    completed_load,
) -> WorkoutOutcome:

    return WorkoutOutcome(
        planned_workout=plan.workouts[0],
        completed_workout=None,
        status=status,
        planned_load=planned_load,
        completed_load=completed_load,
    )


def test_equivalent_outcome_preserves_plan():

    plan = make_plan()

    outcome = make_outcome(
        plan=plan,
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


def test_overload_reduces_next_demanding_workout():

    plan = make_plan()

    outcome = make_outcome(
        plan=plan,
        status=(
            WorkoutOutcomeStatus.MODIFIED
        ),
        planned_load=180.0,
        completed_load=270.0,
    )

    adapted = TrainingPlanAdapter().adapt(
        plan=plan,
        outcomes=(
            outcome,
        ),
        training_state=(
            make_training_state(
                tsb=-25.0,
            )
        ),
        reference_day=date(
            2026,
            8,
            5,
        ),
    )

    assert (
        plan.workouts[1].duration
        == timedelta(minutes=50)
    )

    assert (
        adapted.workouts[1].duration
        == timedelta(minutes=40)
    )


def test_overload_preserves_plan_when_recovery_is_good():

    plan = make_plan()

    outcome = make_outcome(
        plan=plan,
        status=(
            WorkoutOutcomeStatus.MODIFIED
        ),
        planned_load=180.0,
        completed_load=270.0,
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

    assert adapted.workouts == plan.workouts


def test_overload_does_not_change_past_workout():

    plan = make_plan()

    outcome = make_outcome(
        plan=plan,
        status=(
            WorkoutOutcomeStatus.MODIFIED
        ),
        planned_load=180.0,
        completed_load=270.0,
    )

    adapted = TrainingPlanAdapter().adapt(
        plan=plan,
        outcomes=(
            outcome,
        ),
        training_state=(
            make_training_state(
                tsb=-25.0,
            )
        ),
        reference_day=date(
            2026,
            8,
            5,
        ),
    )

    assert (
        adapted.workouts[0]
        == plan.workouts[0]
    )


def test_overload_preserves_taper_workout():

    plan = make_plan()

    taper_workout = PlannedWorkout(
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
        phase="Taper",
    )

    plan.workouts = [
        plan.workouts[0],
        taper_workout,
    ]

    outcome = make_outcome(
        plan=plan,
        status=(
            WorkoutOutcomeStatus.MODIFIED
        ),
        planned_load=180.0,
        completed_load=270.0,
    )

    adapted = TrainingPlanAdapter().adapt(
        plan=plan,
        outcomes=(
            outcome,
        ),
        training_state=(
            make_training_state(
                tsb=-25.0,
            )
        ),
        reference_day=date(
            2026,
            8,
            5,
        ),
    )

    assert (
        adapted.workouts[1].duration
        == timedelta(minutes=50)
    )

def test_missed_workout_increases_next_easy_session():

    plan = make_plan()

    outcome = make_outcome(
        plan=plan,
        status=(
            WorkoutOutcomeStatus.MISSED
        ),
        planned_load=180.0,
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
        plan.workouts[2].duration
        == timedelta(minutes=60)
    )

    assert (
        adapted.workouts[2].duration
        == timedelta(minutes=63)
    )


def test_lower_load_increases_next_easy_session():

    plan = make_plan()

    outcome = make_outcome(
        plan=plan,
        status=(
            WorkoutOutcomeStatus.MODIFIED
        ),
        planned_load=180.0,
        completed_load=90.0,
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
        adapted.workouts[1].duration
        == timedelta(minutes=50)
    )

    assert (
        adapted.workouts[2].duration
        == timedelta(minutes=63)
    )


def test_underload_preserves_plan_during_fatigue():

    plan = make_plan()

    outcome = make_outcome(
        plan=plan,
        status=(
            WorkoutOutcomeStatus.MISSED
        ),
        planned_load=180.0,
        completed_load=None,
    )

    adapted = TrainingPlanAdapter().adapt(
        plan=plan,
        outcomes=(
            outcome,
        ),
        training_state=(
            make_training_state(
                tsb=-25.0,
            )
        ),
        reference_day=date(
            2026,
            8,
            5,
        ),
    )

    assert adapted.workouts == plan.workouts


def test_underload_does_not_move_missed_workout():

    plan = make_plan()

    outcome = make_outcome(
        plan=plan,
        status=(
            WorkoutOutcomeStatus.MISSED
        ),
        planned_load=180.0,
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
        adapted.workouts[0]
        == plan.workouts[0]
    )

    assert (
        adapted.workouts[0].day
        == date(
            2026,
            8,
            4,
        )
    )