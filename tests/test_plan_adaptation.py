"""
Tests for immutable training-plan adaptations.
"""

from dataclasses import FrozenInstanceError
from datetime import date, datetime, timedelta

import pytest

from performancelab.training.planning import (
    TrainingPlanAdaptation,
    WorkoutOutcomeStatus,
)

from performancelab.training.planning.planned_workout import (
    PlannedWorkout,
)
from performancelab.training.planning.training_plan_adapter import (
    TrainingPlanAdapter,
)


def create_adaptation() -> TrainingPlanAdaptation:

    return TrainingPlanAdaptation(
        reconciled_on=date(
            2026,
            8,
            2,
        ),
        workout_day=date(
            2026,
            8,
            4,
        ),
        workout_title="LT2 Run",
        previous_duration=timedelta(
            minutes=50,
        ),
        revised_duration=timedelta(
            minutes=38,
        ),
        trigger_status=(
            WorkoutOutcomeStatus.SUBSTITUTE
        ),
        load_difference=744.0,
    )


def test_models_reduced_future_session():

    result = create_adaptation()

    assert result.duration_change == timedelta(
        minutes=-12,
    )
    assert result.is_reduction is True


def test_adaptation_is_immutable():

    result = create_adaptation()

    with pytest.raises(
        FrozenInstanceError
    ):
        result.workout_title = "Tempo Run"


def test_rejects_unchanged_duration():

    with pytest.raises(
        ValueError,
        match="must change workout duration",
    ):
        TrainingPlanAdaptation(
            reconciled_on=date(
                2026,
                8,
                2,
            ),
            workout_day=date(
                2026,
                8,
                4,
            ),
            workout_title="LT2 Run",
            previous_duration=timedelta(
                minutes=50,
            ),
            revised_duration=timedelta(
                minutes=50,
            ),
            trigger_status=(
                WorkoutOutcomeStatus.MODIFIED
            ),
        )


def test_rejects_non_adaptive_outcome():

    with pytest.raises(
        ValueError,
        match="can adapt the future plan",
    ):
        TrainingPlanAdaptation(
            reconciled_on=date(
                2026,
                8,
                2,
            ),
            workout_day=date(
                2026,
                8,
                4,
            ),
            workout_title="LT2 Run",
            previous_duration=timedelta(
                minutes=50,
            ),
            revised_duration=timedelta(
                minutes=38,
            ),
            trigger_status=(
                WorkoutOutcomeStatus.EQUIVALENT
            ),
        )


def test_rejects_datetime_as_domain_date():

    with pytest.raises(
        TypeError,
        match="reconciled_on must be a date",
    ):
        TrainingPlanAdaptation(
            reconciled_on=datetime(
                2026,
                8,
                2,
            ),
            workout_day=date(
                2026,
                8,
                4,
            ),
            workout_title="LT2 Run",
            previous_duration=timedelta(
                minutes=50,
            ),
            revised_duration=timedelta(
                minutes=38,
            ),
            trigger_status=(
                WorkoutOutcomeStatus.SUBSTITUTE
            ),
        )
def test_adapted_hill_session_preserves_repetitions():

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            11,
            8,
            0,
        ),
        sport="Trail Running",
        title="Hill Run",
        duration=timedelta(
            minutes=45,
        ),
        intensity="Hard",
        objective=(
            "Develop strength and power on climbs."
        ),
        structure=(
            "Warm up 10 min",
            "5×3 min uphill",
            (
                "Recover 2 min easy downhill "
                "between repetitions"
            ),
            "Cool down 5 min",
            (
                "Heart rate target: "
                "Z4 · 177–186 bpm"
            ),
        ),
    )

    result = (
        TrainingPlanAdapter
        ._adapted_structure(
            workout=workout,
            duration=timedelta(
                minutes=36,
            ),
            main_label=(
                "Controlled quality work"
            ),
        )
    )

    assert any(
        (
            "×3 min uphill"
            in step
        )
        for step in result
    )

    assert any(
        (
            "Recover 2 min easy downhill"
            in step
        )
        for step in result
    )

    assert (
        "Controlled quality work 22 min"
        not in result
    )

    assert (
        "Heart rate target: Z4 · 177–186 bpm"
        in result
    )