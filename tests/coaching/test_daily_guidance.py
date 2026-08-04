"""
Tests for daily training guidance.
"""

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta

import pytest

from performancelab.analysis.training_state import (
    TrainingState,
)
from performancelab.coaching import (
    DailyTrainingGuidance,
    build_daily_training_guidance,
)
from performancelab.training.planning import (
    PlannedWorkout,
)


def create_training_state(
    *,
    tsb: float = 5.0,
    acute_chronic_ratio: float | None = 1.0,
) -> TrainingState:

    return TrainingState(
        ctl=50.0,
        atl=45.0,
        tsb=tsb,
        acute_chronic_ratio=(
            acute_chronic_ratio
        ),
        monotony=None,
        strain=None,
        consistency=None,
        weekly_frequency=None,
        days_since_last_workout=2,
        recent_training_load=250.0,
    )


def test_builds_guidance_for_demanding_session():

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            4,
        ),
        sport="Trail Running",
        title="LT2 Run",
        duration=timedelta(
            minutes=38,
        ),
        intensity="Hard",
        phase="Peak",
    )

    result = build_daily_training_guidance(
        training_state=(
            create_training_state()
        ),
        workout=workout,
    )

    assert isinstance(
        result,
        DailyTrainingGuidance,
    )

    assert (
        "Current recovery supports the planned session."
        in result.reasons
    )

    assert (
        "The session supports the Peak phase."
        in result.reasons
    )

    assert (
        "Keep every quality effort controlled."
        in result.cautions
    )


def test_guidance_is_immutable():

    result = build_daily_training_guidance(
        training_state=(
            create_training_state()
        ),
        workout=None,
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        result.reasons = ()


def test_rest_day_prioritises_recovery():

    result = build_daily_training_guidance(
        training_state=(
            create_training_state()
        ),
        workout=None,
    )

    assert result.reasons == (
        "No training session is planned today.",
    )

    assert result.cautions == (
        "Use the day for recovery and preparation.",
    )


def test_recovery_state_limits_duration():

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            4,
        ),
        sport="Running",
        title="Tempo Run",
        duration=timedelta(
            minutes=50,
        ),
        intensity="Hard",
    )

    result = build_daily_training_guidance(
        training_state=(
            create_training_state(
                tsb=-25.0,
                acute_chronic_ratio=1.6,
            )
        ),
        workout=workout,
    )

    assert (
        "Current fatigue indicates that recovery should take priority."
        in result.reasons
    )

    assert (
        "Do not extend the planned duration."
        in result.cautions
    )