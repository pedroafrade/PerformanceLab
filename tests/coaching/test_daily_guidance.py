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
    TemporaryWorkoutAdjustment,
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

def test_preserves_suitable_recovery_session():

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            13,
        ),
        sport="Trail Running",
        title="Recovery Run",
        duration=timedelta(
            minutes=20,
        ),
        intensity="Very easy",
        phase="Regeneration",
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
            .RECOVERY_AS_PLANNED
        )
    )

    assert (
        result.temporary_adjustment
        is None
    )

    assert (
        "The planned recovery session already "
        "matches today's recovery needs."
        in result.reasons
    )

    assert (
        "Keep the planned recovery session "
        "very easy and within its duration."
        in result.cautions
    )

    assert (
        "Rest instead if subjective feedback "
        "indicates that even light activity "
        "is inappropriate."
        in result.cautions
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

def test_proceed_has_no_temporary_adjustment():

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

    assert (
        result.temporary_adjustment
        is None
    )


def test_reduces_planned_duration_by_twenty_percent():

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            4,
        ),
        sport="Running",
        title="Easy Run",
        duration=timedelta(
            minutes=50,
        ),
        intensity="Easy",
    )

    result = build_daily_training_guidance(
        training_state=(
            create_training_state(
                tsb=-5.0,
                acute_chronic_ratio=1.6,
            )
        ),
        workout=workout,
    )

    assert (
        result.decision
        is DailyTrainingDecision.REDUCE_VOLUME
    )

    adjustment = (
        result.temporary_adjustment
    )

    assert isinstance(
        adjustment,
        TemporaryWorkoutAdjustment,
    )

    assert (
        adjustment.title
        == "Easy Run"
    )

    assert (
        adjustment.maximum_duration
        == timedelta(minutes=40)
    )

    assert (
        adjustment.replaces_planned_session
        is False
    )

    # The persistent planned workout was not mutated.
    assert (
        workout.duration
        == timedelta(minutes=50)
    )


def test_replaces_intensity_with_short_easy_session():

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            4,
        ),
        sport="Running",
        title="LT2 Run",
        duration=timedelta(
            minutes=60,
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

    adjustment = (
        result.temporary_adjustment
    )

    assert (
        result.decision
        is DailyTrainingDecision.EASY_ONLY
    )

    assert (
        adjustment.title
        == "Easy session"
    )

    assert (
        adjustment.intensity
        == "Easy"
    )

    assert (
        adjustment.maximum_duration
        == timedelta(minutes=35)
    )

    assert (
        adjustment.replaces_planned_session
        is True
    )


def test_recovery_allows_rest_or_twenty_minutes():

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            4,
        ),
        sport="Running",
        title="Long Run",
        duration=timedelta(
            minutes=115,
        ),
        intensity="Easy to moderate",
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

    adjustment = (
        result.temporary_adjustment
    )

    assert (
        result.decision
        is (
            DailyTrainingDecision
            .RECOVERY_ONLY
        )
    )

    assert (
        adjustment.title
        == "Rest or very light recovery"
    )

    assert (
        adjustment.intensity
        == "Very easy"
    )

    assert (
        adjustment.maximum_duration
        == timedelta(minutes=20)
    )

    assert (
        adjustment.replaces_planned_session
        is True
    )


def test_race_review_has_no_automatic_adjustment():

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

    assert (
        result.temporary_adjustment
        is None
    )


def test_temporary_adjustment_is_immutable():

    adjustment = TemporaryWorkoutAdjustment(
        title="Easy session",
        intensity="Easy",
        maximum_duration=timedelta(
            minutes=30,
        ),
        replaces_planned_session=True,
        explanation="Temporary adjustment.",
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        adjustment.title = "Tempo Run"

def test_completed_activity_is_not_recommended_again():

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
        workout_completed=True,
    )

    assert (
        result.decision
        is DailyTrainingDecision.COMPLETED
    )

    assert (
        result.temporary_adjustment
        is None
    )

    assert (
        "Today's activity has already been completed."
        in result.reasons
    )

    assert (
        "Do not repeat the planned session "
        "to compensate for differences from "
        "the prescription."
        in result.cautions
    )


def test_rejects_invalid_completed_flag():

    with pytest.raises(
        TypeError,
        match="workout_completed",
    ):

        build_daily_training_guidance(
            training_state=(
                create_training_state()
            ),
            workout=None,
            workout_completed="yes",
        )