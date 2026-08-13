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
    DailyTrainingDecision,
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
        "The planned session supports the Peak phase."
        in result.reasons
    )

    assert (
        result.decision
        is DailyTrainingDecision.PROCEED
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
        result.decision
        is (
            DailyTrainingDecision
            .RECOVERY_ONLY
        )
    )

    assert (
        "Do not perform the planned intensity or volume today."
        in result.cautions
    )

    assert (
        "Use rest or very light recovery work according to subjective feedback."
        in result.cautions
    )

def test_ready_athlete_can_proceed():

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            4,
        ),
        sport="Running",
        title="Easy Run",
        duration=timedelta(
            minutes=45,
        ),
        intensity="Easy",
    )

    result = build_daily_training_guidance(
        training_state=(
            create_training_state()
        ),
        workout=workout,
    )

    assert (
        result.decision
        is DailyTrainingDecision.PROCEED
    )


def test_recovery_replaces_large_easy_session():

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            4,
        ),
        sport="Running",
        title="Easy Run",
        duration=timedelta(
            minutes=115,
        ),
        distance=19.0,
        intensity="Easy",
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
        result.decision
        is (
            DailyTrainingDecision
            .RECOVERY_ONLY
        )
    )

    assert (
        "Recovery should replace the planned "
        "training stimulus today."
        in result.reasons
    )


def test_easy_readiness_replaces_intensity():

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            4,
        ),
        sport="Running",
        title="LT2 Run",
        duration=timedelta(
            minutes=45,
        ),
        intensity="Hard",
    )

    result = build_daily_training_guidance(
        training_state=(
            create_training_state(
                tsb=-5.0,
                acute_chronic_ratio=1.0,
            )
        ),
        workout=workout,
    )

    assert (
        result.decision
        is DailyTrainingDecision.EASY_ONLY
    )


def test_race_requires_review_during_recovery():

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            4,
        ),
        sport="Trail Running",
        title="Race",
        duration=timedelta(
            hours=3,
        ),
        intensity="Race effort",
        phase="Race",
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
        result.decision
        is (
            DailyTrainingDecision
            .REVIEW_REQUIRED
        )
    )


def test_rest_day_returns_rest_decision():

    result = build_daily_training_guidance(
        training_state=(
            create_training_state()
        ),
        workout=None,
    )

    assert (
        result.decision
        is DailyTrainingDecision.REST
    )