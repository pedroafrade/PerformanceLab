"""
PerformanceLab

Tests for one-time training-plan reconciliation.
"""

from datetime import date, datetime, timedelta

from performancelab import History, Workout
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
def test_closed_day_reconciliation_stops_at_yesterday():

    plan = make_plan()

    reconciled = (
        TrainingPlanReconciler()
        .reconcile_closed_days(
            plan=plan,
            history=History(),
            training_state=(
                make_training_state()
            ),
            today=date(
                2026,
                8,
                5,
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
        reconciled.workouts[1].duration
        == timedelta(minutes=63)
    )


def test_closed_day_reconciliation_keeps_today_open():

    today_workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            5,
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
            today_workout,
        ],
    )

    reconciled = (
        TrainingPlanReconciler()
        .reconcile_closed_days(
            plan=plan,
            history=History(),
            training_state=(
                make_training_state()
            ),
            today=date(
                2026,
                8,
                5,
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
        reconciled.workouts
        == [
            today_workout,
        ]
    )
def test_reconciliation_records_closed_workout_identity():

    history = History()

    completed = Workout(
        workout_id="completed-workout",
    )

    completed.info.date = datetime(
        2026,
        8,
        4,
        9,
        0,
    )

    completed.info.sport = "Running"

    completed.info.duration = timedelta(
        minutes=50,
    )

    completed.info.distance = 10.0

    future = Workout(
        workout_id="future-workout",
    )

    future.info.date = datetime(
        2026,
        8,
        6,
        9,
        0,
    )

    future.info.sport = "Running"

    future.info.duration = timedelta(
        minutes=60,
    )

    future.info.distance = 10.0

    history.add(completed)
    history.add(future)

    reconciled = (
        TrainingPlanReconciler().reconcile(
            plan=make_plan(),
            history=history,
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
        reconciled.reconciled_workout_ids
        == (
            "completed-workout",
        )
    )
def test_existing_reconciliation_bootstraps_workout_ids():

    plan = make_plan()

    plan.reconciled_through = date(
        2026,
        8,
        4,
    )

    history = History()

    completed = Workout(
        workout_id="existing-workout",
    )

    completed.info.date = datetime(
        2026,
        8,
        4,
        9,
        0,
    )

    completed.info.sport = "Running"

    completed.info.duration = timedelta(
        minutes=50,
    )

    completed.info.distance = 10.0

    history.add(completed)

    reconciler = TrainingPlanReconciler()

    bootstrapped = reconciler.reconcile(
        plan=plan,
        history=history,
        training_state=(
            make_training_state()
        ),
        through_day=date(
            2026,
            8,
            4,
        ),
    )

    assert bootstrapped is not plan

    assert (
        bootstrapped.reconciled_workout_ids
        == (
            "existing-workout",
        )
    )

    assert (
        bootstrapped
        .reconciled_workout_signatures
        == (
            (
                "existing-workout",
                (
                    "2026-08-04",
                    "running",
                    3000.0,
                    None,
                ),
            ),
        )
    )

    assert (
        bootstrapped.workouts
        == plan.workouts
    )

    assert (
        bootstrapped.workouts[1].duration
        == timedelta(minutes=60)
    )

    repeated = reconciler.reconcile(
        plan=bootstrapped,
        history=history,
        training_state=(
            make_training_state()
        ),
        through_day=date(
            2026,
            8,
            4,
        ),
    )

    assert repeated is bootstrapped

def test_late_workout_is_reconciled_once():

    plan = make_plan()

    plan.reconciled_through = date(
        2026,
        8,
        4,
    )

    plan.reconciled_workout_ids = (
        "previous-workout",
    )

    history = History()

    late_workout = Workout(
        workout_id="late-workout",
    )

    late_workout.info.date = datetime(
        2026,
        8,
        4,
        18,
        0,
    )

    late_workout.info.sport = "Cycling"

    late_workout.info.duration = timedelta(
        minutes=30,
    )

    late_workout.info.distance = 15.0

    late_workout.feedback.rpe = 4

    history.add(late_workout)

    reconciler = TrainingPlanReconciler()

    reconciled = reconciler.reconcile(
        plan=plan,
        history=history,
        training_state=(
            make_training_state()
        ),
        through_day=date(
            2026,
            8,
            4,
        ),
    )

    assert reconciled is not plan

    assert (
        reconciled.reconciled_through
        == date(
            2026,
            8,
            4,
        )
    )

    assert (
        reconciled.reconciled_workout_ids
        == (
            "previous-workout",
            "late-workout",
        )
    )

    assert (
        reconciled.workouts[1].duration
        == timedelta(minutes=63)
    )

    repeated = reconciler.reconcile(
        plan=reconciled,
        history=history,
        training_state=(
            make_training_state()
        ),
        through_day=date(
            2026,
            8,
            4,
        ),
    )

    assert repeated is reconciled

    assert (
        repeated.workouts[1].duration
        == timedelta(minutes=63)
    )
def test_late_workout_is_assessed_with_multiple_same_day():

    plan = make_plan()

    plan.reconciled_through = date(
        2026,
        8,
        4,
    )

    plan.reconciled_workout_ids = (
        "existing-workout",
    )

    history = History()

    late_workout = Workout(
        workout_id="late-workout",
    )

    late_workout.info.date = datetime(
        2026,
        8,
        4,
        7,
        0,
    )

    late_workout.info.sport = "Cycling"

    late_workout.info.duration = timedelta(
        minutes=30,
    )

    late_workout.info.distance = 15.0

    late_workout.feedback.rpe = 4

    existing_workout = Workout(
        workout_id="existing-workout",
    )

    existing_workout.info.date = datetime(
        2026,
        8,
        4,
        18,
        0,
    )

    existing_workout.info.sport = "Running"

    existing_workout.info.duration = timedelta(
        minutes=50,
    )

    existing_workout.info.distance = 10.0

    existing_workout.feedback.rpe = 7

    history.add(late_workout)
    history.add(existing_workout)

    reconciled = (
        TrainingPlanReconciler().reconcile(
            plan=plan,
            history=history,
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
        reconciled.reconciled_workout_ids
        == (
            "existing-workout",
            "late-workout",
        )
    )

    assert (
        reconciled.workouts[1].duration
        == timedelta(minutes=63)
    )
def test_existing_ids_bootstrap_signatures_once():

    plan = make_plan()

    plan.reconciled_through = date(
        2026,
        8,
        4,
    )

    plan.reconciled_workout_ids = (
        "existing-workout",
    )

    history = History()

    completed = Workout(
        workout_id="existing-workout",
    )

    completed.info.date = datetime(
        2026,
        8,
        4,
        9,
        0,
    )

    completed.info.sport = "Running"

    completed.info.duration = timedelta(
        minutes=50,
    )

    completed.feedback.rpe = 6

    history.add(completed)

    reconciler = TrainingPlanReconciler()

    bootstrapped = reconciler.reconcile(
        plan=plan,
        history=history,
        training_state=(
            make_training_state()
        ),
        through_day=date(
            2026,
            8,
            4,
        ),
    )

    assert bootstrapped is not plan

    assert (
        bootstrapped
        .reconciled_workout_signatures
        == (
            (
                "existing-workout",
                (
                    "2026-08-04",
                    "running",
                    3000.0,
                    6.0,
                ),
            ),
        )
    )

    assert (
        bootstrapped.workouts
        == plan.workouts
    )

    assert (
        bootstrapped.workouts[1].duration
        == timedelta(minutes=60)
    )

    repeated = reconciler.reconcile(
        plan=bootstrapped,
        history=history,
        training_state=(
            make_training_state()
        ),
        through_day=date(
            2026,
            8,
            4,
        ),
    )

    assert repeated is bootstrapped