"""
PerformanceLab

Tests for planned workout outcomes.
"""

from datetime import date, datetime, timedelta

from performancelab import (
    History,
    create_workout,
)
from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
    WorkoutOutcomeStatus,
    assess_workout_outcome,
)


def make_planned_workout(
    *,
    sport="Trail Running",
    duration_minutes=60,
    intensity="Easy",
):

    return PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            4,
            8,
            0,
        ),
        sport=sport,
        duration=timedelta(
            minutes=duration_minutes,
        ),
        intensity=intensity,
    )


def make_completed_workout(
    *,
    sport="Running",
    duration_minutes=60,
    rpe=3,
):

    return create_workout(
        sport=sport,
        workout_date=datetime(
            2026,
            8,
            4,
            8,
            5,
        ),
        distance=10.0,
        duration=timedelta(
            minutes=duration_minutes,
        ),
        elevation_gain=0.0,
        rpe=rpe,
    )


def test_future_workout_is_pending():

    outcome = assess_workout_outcome(
        planned_workout=(
            make_planned_workout()
        ),
        completed_workout=None,
        reference_day=date(
            2026,
            8,
            3,
        ),
    )

    assert (
        outcome.status
        is WorkoutOutcomeStatus.PENDING
    )


def test_past_workout_without_activity_is_missed():

    outcome = assess_workout_outcome(
        planned_workout=(
            make_planned_workout()
        ),
        completed_workout=None,
        reference_day=date(
            2026,
            8,
            5,
        ),
    )

    assert (
        outcome.status
        is WorkoutOutcomeStatus.MISSED
    )


def test_similar_running_load_is_equivalent():

    outcome = assess_workout_outcome(
        planned_workout=(
            make_planned_workout()
        ),
        completed_workout=(
            make_completed_workout()
        ),
        reference_day=date(
            2026,
            8,
            4,
        ),
    )

    assert (
        outcome.status
        is WorkoutOutcomeStatus.EQUIVALENT
    )

    assert outcome.load_difference == 0


def test_different_running_load_is_modified():

    outcome = assess_workout_outcome(
        planned_workout=(
            make_planned_workout()
        ),
        completed_workout=(
            make_completed_workout(
                duration_minutes=30,
            )
        ),
        reference_day=date(
            2026,
            8,
            4,
        ),
    )

    assert (
        outcome.status
        is WorkoutOutcomeStatus.MODIFIED
    )

    assert outcome.load_difference == -90


def test_different_sport_is_substitute():

    outcome = assess_workout_outcome(
        planned_workout=(
            make_planned_workout()
        ),
        completed_workout=(
            make_completed_workout(
                sport="Cycling",
            )
        ),
        reference_day=date(
            2026,
            8,
            4,
        ),
    )

    assert (
        outcome.status
        is WorkoutOutcomeStatus.SUBSTITUTE
    )

def test_training_plan_assesses_complete_history():

    completed = (
        make_completed_workout()
    )

    future = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            6,
            8,
            0,
        ),
        sport="Trail Running",
        duration=timedelta(
            minutes=60,
        ),
        intensity="Easy",
    )

    history = History(
        workouts=[
            completed,
        ]
    )

    plan = TrainingPlan(
        workouts=[
            make_planned_workout(),
            future,
        ]
    )

    outcomes = plan.assess_outcomes(
        history=history,
        reference_day=date(
            2026,
            8,
            5,
        ),
    )

    assert len(outcomes) == 2

    assert (
        outcomes[0].status
        is WorkoutOutcomeStatus.EQUIVALENT
    )

    assert (
        outcomes[1].status
        is WorkoutOutcomeStatus.PENDING
    )


def test_training_plan_detects_missed_workout():

    plan = TrainingPlan(
        workouts=[
            make_planned_workout(),
        ]
    )

    outcomes = plan.assess_outcomes(
        history=History(),
        reference_day=date(
            2026,
            8,
            5,
        ),
    )

    assert len(outcomes) == 1

    assert (
        outcomes[0].status
        is WorkoutOutcomeStatus.MISSED
    )


def test_training_plan_matches_workout_by_calendar_day():

    completed = (
        make_completed_workout()
    )

    history = History(
        workouts=[
            completed,
        ]
    )

    plan = TrainingPlan(
        workouts=[
            make_planned_workout(),
        ]
    )

    outcomes = plan.assess_outcomes(
        history=history,
        reference_day=date(
            2026,
            8,
            4,
        ),
    )

    assert (
        outcomes[0].completed_workout
        is completed
    )