"""
PerformanceLab

Tests for one-time training-plan reconciliation.
"""

from datetime import date, datetime, timedelta

from performancelab import History
from performancelab.analysis.training_state import (
    TrainingState,
)
from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
    TrainingPlanReconciler,
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
        days_since_last_workout=1,
        recent_training_load=300.0,
    )


def make_plan() -> TrainingPlan:

    return TrainingPlan(
        plan_id="reconciliation-plan",
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
                    6,
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


def test_reconciliation_adapts_missed_workout_once():

    plan = make_plan()

    reconciled = (
        TrainingPlanReconciler().reconcile(
            plan=plan,
            history=History(),
            training_state=(
                make_training_state()
            ),
            through_day=date(
                2026,
                8,
                4,
            ),
        )
    )

    assert (
        reconciled.reconciled_through
        == date(
            2026,
            8,
            4,
        )
    )

    assert (
        reconciled.workouts[0].duration
        == timedelta(minutes=50)
    )

    assert (
        reconciled.workouts[1].duration
        == timedelta(minutes=63)
    )


def test_same_period_is_not_adapted_twice():

    reconciler = (
        TrainingPlanReconciler()
    )

    first = reconciler.reconcile(
        plan=make_plan(),
        history=History(),
        training_state=(
            make_training_state()
        ),
        through_day=date(
            2026,
            8,
            4,
        ),
    )

    second = reconciler.reconcile(
        plan=first,
        history=History(),
        training_state=(
            make_training_state()
        ),
        through_day=date(
            2026,
            8,
            4,
        ),
    )

    assert second is first

    assert (
        second.workouts[1].duration
        == timedelta(minutes=63)
    )


def test_reconciliation_ignores_future_workouts():

    plan = make_plan()

    reconciled = (
        TrainingPlanReconciler().reconcile(
            plan=plan,
            history=History(),
            training_state=(
                make_training_state()
            ),
            through_day=date(
                2026,
                8,
                3,
            ),
        )
    )

    assert reconciled.workouts == plan.workouts

    assert (
        reconciled.reconciled_through
        == date(
            2026,
            8,
            3,
        )
    )


def test_reconciliation_processes_only_new_period():

    reconciler = (
        TrainingPlanReconciler()
    )

    first = reconciler.reconcile(
        plan=make_plan(),
        history=History(),
        training_state=(
            make_training_state()
        ),
        through_day=date(
            2026,
            8,
            3,
        ),
    )

    second = reconciler.reconcile(
        plan=first,
        history=History(),
        training_state=(
            make_training_state()
        ),
        through_day=date(
            2026,
            8,
            4,
        ),
    )

    assert (
        second.reconciled_through
        == date(
            2026,
            8,
            4,
        )
    )

    assert (
        second.workouts[1].duration
        == timedelta(minutes=63)
    )