"""
Tests for adaptation history in TrainingPlan.
"""

from datetime import date, timedelta

import pytest

from performancelab.training.planning import (
    TrainingPlan,
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


def test_training_plan_keeps_immutable_adaptation_history():

    adaptation = create_adaptation()

    plan = TrainingPlan(
        adaptations=(
            adaptation,
        ),
    )

    assert plan.adaptations == (
        adaptation,
    )


def test_training_plan_requires_adaptation_tuple():

    with pytest.raises(
        TypeError,
        match="adaptations must be a tuple",
    ):
        TrainingPlan(
            adaptations=[
                create_adaptation(),
            ],
        )


def test_training_plan_rejects_invalid_adaptation_entry():

    with pytest.raises(
        TypeError,
        match="TrainingPlanAdaptation",
    ):
        TrainingPlan(
            adaptations=(
                "invalid",
            ),
        )
