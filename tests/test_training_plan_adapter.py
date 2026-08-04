"""
PerformanceLab

Tests for incremental training-plan adaptation.
"""

from datetime import date, datetime, timedelta
from dataclasses import replace

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
        reconciled_workout_ids=(
            "completed-workout",
        ),
        reconciled_workout_signatures=(
            (
                "completed-workout",
                (
                    "2026-08-04",
                    "running",
                    3600.0,
                    6.0,
                ),
            ),
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
    assert (
        adapted.reconciled_workout_ids
        == plan.reconciled_workout_ids
    )
    assert (
        adapted.reconciled_workout_signatures
        == plan.reconciled_workout_signatures
    )
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
    plan.workouts[1] = replace(
        plan.workouts[1],
        prescription_summary=(
            "35 min tempo"
        ),
        structure=(
            "Warm up 10 min",
            "Tempo effort 35 min",
            "Cool down 5 min",
            (
                "Heart rate target: "
                "Z3–Z4 · 168–175 bpm"
            ),
        ),
    )
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
        == timedelta(
            minutes=43,
            seconds=45,
        )
    )
    assert (
        adapted.workouts[1]
        .prescription_summary
        == (
            "Reduced quality session · "
            "44 min total"
        )
    )

    assert (
        adapted.workouts[1].structure
        == (
            "Warm up 10 min",
            (
                "Controlled quality work "
                "29 min"
            ),
            "Cool down 5 min",
            (
                "Heart rate target: "
                "Z3–Z4 · 168–175 bpm"
            ),
        )
    )
    assert len(
        adapted.adaptations
    ) == 1

    adaptation = (
        adapted.adaptations[0]
    )

    assert (
        adaptation.workout_title
        == adapted.workouts[1].title
    )
    assert (
        adaptation.previous_duration
        == timedelta(minutes=50)
    )
    assert (
        adaptation.revised_duration
        == timedelta(
            minutes=43,
            seconds=45,
        )
    )
    assert (
        adaptation.trigger_status
        is WorkoutOutcomeStatus.MODIFIED
    )
    assert (
        adaptation.load_difference
        == 90.0
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
    assert (
        adapted.adaptations
        == ()
    )


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
    assert len(
        adapted.adaptations
    ) == 1

    adaptation = (
        adapted.adaptations[0]
    )

    assert (
        adaptation.previous_duration
        == timedelta(minutes=60)
    )
    assert (
        adaptation.revised_duration
        == timedelta(minutes=63)
    )
    assert (
        adaptation.trigger_status
        is WorkoutOutcomeStatus.MISSED
    )
    assert (
        adaptation.load_difference
        is None
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

def test_equivalent_substitute_load_preserves_future_plan():

    plan = make_plan()

    outcome = make_outcome(
        plan=plan,
        status=(
            WorkoutOutcomeStatus.SUBSTITUTE
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

    assert adapted.workouts == plan.workouts


def test_substitute_overload_reduces_demanding_session():

    plan = make_plan()

    outcome = make_outcome(
        plan=plan,
        status=(
            WorkoutOutcomeStatus.SUBSTITUTE
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
        == timedelta(
            minutes=43,
            seconds=45,
        )
    )


def test_substitute_underload_increases_easy_session():

    plan = make_plan()

    outcome = make_outcome(
        plan=plan,
        status=(
            WorkoutOutcomeStatus.SUBSTITUTE
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
def test_underload_prefers_planned_sport_family():

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
                sport="Cycling",
                title="Easy Ride",
                duration=timedelta(
                    minutes=60,
                ),
                intensity="Easy",
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

    outcome = WorkoutOutcome(
        planned_workout=(
            plan.workouts[0]
        ),
        completed_workout=None,
        status=(
            WorkoutOutcomeStatus.SUBSTITUTE
        ),
        planned_load=350.0,
        completed_load=120.0,
    )

    adapted = TrainingPlanAdapter().adapt(
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

    assert (
        adapted.workouts[1].duration
        == timedelta(minutes=60)
    )

    assert (
        adapted.workouts[2].duration
        == timedelta(minutes=63)
    )

def test_unknown_substitute_load_preserves_plan():

    plan = make_plan()

    outcome = make_outcome(
        plan=plan,
        status=(
            WorkoutOutcomeStatus.SUBSTITUTE
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
            make_training_state()
        ),
        reference_day=date(
            2026,
            8,
            5,
        ),
    )

    assert (
        adapted.workouts
        == plan.workouts
    )

def test_small_underload_uses_proportional_increase():

    plan = make_plan()

    outcome = make_outcome(
        plan=plan,
        status=(
            WorkoutOutcomeStatus.MODIFIED
        ),
        planned_load=180.0,
        completed_load=174.0,
    )

    adapted = TrainingPlanAdapter().adapt(
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

    assert (
        adapted.workouts[2].duration
        == timedelta(
            minutes=60,
            seconds=30,
        )
    )

def test_overload_reduction_is_capped_at_twenty_percent():

    plan = make_plan()

    outcome = make_outcome(
        plan=plan,
        status=(
            WorkoutOutcomeStatus.MODIFIED
        ),
        planned_load=180.0,
        completed_load=900.0,
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
        == timedelta(minutes=40)
    )

def test_underload_does_not_increase_recovery_session():

    plan = make_plan()

    plan.workouts[1] = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            6,
            8,
            0,
        ),
        sport="Running",
        title="Recovery Run",
        duration=timedelta(
            minutes=50,
        ),
        intensity="Recovery",
    )

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
        adapted.workouts[1].duration
        == timedelta(minutes=50)
    )

    assert (
        adapted.workouts[2].duration
        == timedelta(minutes=63)
    )

def test_underload_preserves_schedule_and_weekly_limit():

    plan = make_plan()

    original_days = tuple(
        workout.day
        for workout in plan.workouts
    )

    original_duration = sum(
        (
            workout.duration
            for workout in plan.workouts
            if workout.duration is not None
        ),
        timedelta(),
    )

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

    adapted_days = tuple(
        workout.day
        for workout in adapted.workouts
    )

    adapted_duration = sum(
        (
            workout.duration
            for workout in adapted.workouts
            if workout.duration is not None
        ),
        timedelta(),
    )

    assert (
        len(adapted.workouts)
        == len(plan.workouts)
    )

    assert (
        adapted_days
        == original_days
    )

    assert (
        adapted_duration
        <= original_duration * 1.05
    )

def test_adapted_lt2_structure_preserves_intervals():

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            4,
            8,
            0,
        ),
        sport="Trail Running",
        title="LT2 Run",
        duration=timedelta(
            minutes=60,
        ),
        intensity="Hard",
        structure=(
            "Warm up 16 min",
            (
                "3×10 min at LT2 "
                "(177 bpm)"
            ),
            (
                "Recover 2 min easy "
                "between repetitions"
            ),
            "Cool down 10 min",
            (
                "Heart rate target: "
                "Z4 · 177–181 bpm"
            ),
        ),
    )

    structure = (
        TrainingPlanAdapter
        ._adapted_structure(
            workout=workout,
            duration=timedelta(
                minutes=38,
            ),
            main_label=(
                "Controlled quality work"
            ),
        )
    )

    assert structure == (
        "Warm up 8 min",
        "3×7 min at LT2",
        (
            "Recover 2 min easy "
            "between repetitions"
        ),
        "Cool down 5 min",
        (
            "Heart rate target: "
            "Z4 · 177–181 bpm"
        ),
    )