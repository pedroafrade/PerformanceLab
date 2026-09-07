"""
Tests for workout stimulus classification.
"""

from datetime import datetime, timedelta

from performancelab.training.planning import (
    PlannedWorkout,
    WorkoutOutcome,
    WorkoutOutcomeStatus,
    WorkoutStimulus,
    completed_workout_stimulus,
    planned_workout_stimulus,
)
from performancelab.workout import (
    Workout,
    WorkoutInfo,
)


def planned(
    *,
    purpose=None,
    focus=None,
    title="Planned workout",
):
    return PlannedWorkout(
        scheduled_at=datetime(
            2026,
            9,
            2,
            8,
            0,
        ),
        sport="Trail Running",
        title=title,
        duration=timedelta(
            minutes=50,
        ),
        purpose=purpose,
        focus=focus,
    )


def completed(
    title: str,
):
    return Workout(
        info=WorkoutInfo(
            date=datetime(
                2026,
                9,
                2,
                8,
                0,
            ),
            sport="Trail Running",
            title=title,
            duration=timedelta(
                minutes=50,
            ),
        )
    )


def test_planned_focus_has_priority():

    workout = planned(
        purpose="intensity",
        focus="hills",
        title="Quality Run",
    )

    assert (
        planned_workout_stimulus(
            workout
        )
        is WorkoutStimulus.HILLS
    )


def test_legacy_planned_title_remains_supported():

    workout = planned(
        title="LT2 Run",
    )

    assert (
        planned_workout_stimulus(
            workout
        )
        is WorkoutStimulus.THRESHOLD
    )


def test_completed_explicit_easy_run_is_classified():

    workout = completed(
        "Easy Run"
    )

    assert (
        completed_workout_stimulus(
            workout
        )
        is WorkoutStimulus.EASY
    )


def test_hills_replaced_by_tempo_creates_gap():

    outcome = WorkoutOutcome(
        planned_workout=planned(
            purpose="intensity",
            focus="hills",
        ),
        completed_workout=completed(
            "Tempo Run"
        ),
        status=(
            WorkoutOutcomeStatus.MODIFIED
        ),
        planned_load=250.0,
        completed_load=250.0,
    )

    assert (
        outcome.planned_stimulus
        is WorkoutStimulus.HILLS
    )
    assert (
        outcome.completed_stimulus
        is WorkoutStimulus.TEMPO
    )
    assert outcome.stimulus_equivalent is False
    assert outcome.has_stimulus_gap is True


def test_lt2_replaced_by_easy_creates_gap():

    outcome = WorkoutOutcome(
        planned_workout=planned(
            purpose="intensity",
            focus="threshold",
        ),
        completed_workout=completed(
            "Easy Run"
        ),
        status=(
            WorkoutOutcomeStatus.MODIFIED
        ),
        planned_load=240.0,
        completed_load=180.0,
    )

    assert (
        outcome.planned_stimulus
        is WorkoutStimulus.THRESHOLD
    )
    assert (
        outcome.completed_stimulus
        is WorkoutStimulus.EASY
    )
    assert outcome.has_stimulus_gap is True


def test_unknown_completed_title_does_not_invent_gap():

    outcome = WorkoutOutcome(
        planned_workout=planned(
            purpose="intensity",
            focus="hills",
        ),
        completed_workout=completed(
            "Morning Activity"
        ),
        status=(
            WorkoutOutcomeStatus.MODIFIED
        ),
        planned_load=250.0,
        completed_load=250.0,
    )

    assert (
        outcome.completed_stimulus
        is WorkoutStimulus.UNKNOWN
    )
    assert outcome.stimulus_equivalent is None
    assert outcome.has_stimulus_gap is False


def test_missed_known_stimulus_creates_gap():

    outcome = WorkoutOutcome(
        planned_workout=planned(
            purpose="intensity",
            focus="threshold",
        ),
        completed_workout=None,
        status=(
            WorkoutOutcomeStatus.MISSED
        ),
        planned_load=240.0,
        completed_load=None,
    )

    assert outcome.has_stimulus_gap is True