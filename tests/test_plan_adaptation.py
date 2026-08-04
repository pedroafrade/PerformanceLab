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
