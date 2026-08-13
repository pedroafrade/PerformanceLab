"""
Tests for the Today presenter.
"""
import pytest

from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
from dataclasses import (
    FrozenInstanceError,
)

from performancelab import (
    Athlete,
    create_workout,
)

from performancelab.coaching import (
    DailyTrainingDecision,
    TemporaryWorkoutAdjustment,
)

from performancelab.presentation import (
    TodayData,
    TodayPresenter,
)
from performancelab.training.planning import (
    TrainingPlanAdaptation,
    WorkoutOutcomeStatus,
)


REFERENCE_DAY = date(
    2026,
    8,
    4,
)


def test_builds_empty_today_context():

    athlete = Athlete(
        name="Pedro"
    )

    result = TodayPresenter(
        athlete
    ).build(
        reference_day=(
            REFERENCE_DAY
        )
    )

    assert isinstance(
        result,
        TodayData,
    )

    assert (
        result.reference_day
        == REFERENCE_DAY
    )

    assert (
        result.today_session.day
        == REFERENCE_DAY
    )

    assert (
        result.today_session.title
        is None
    )

    assert (
        result.next_workout
        is None
    )

    assert (
        result.next_event
        is None
    )
    assert (
        result.guidance.decision
        == "rest"
    )

    assert (
        result.guidance.title
        == "Rest and recover today"
    )

    assert (
        result.guidance.action
        == (
            "No training stimulus is "
            "recommended today."
        )
    )

    assert (
        result.guidance.plan_is_modified
        is False
    )

    assert (
        result.guidance
        .temporary_adjustment
        is None
    )

    assert result.guidance.reasons == (
        "No training session is planned today.",
    )

    assert result.guidance.cautions == (
        "Use the day for recovery and preparation.",
    )


def test_exposes_today_and_next_workout():

    athlete = Athlete(
        name="Pedro"
    )

    athlete.training_plan.schedule(
        scheduled_at=datetime.combine(
            REFERENCE_DAY,
            time.min,
        ),
        sport="Running",
        title="Easy Run",
        duration=timedelta(
            minutes=45,
        ),
        intensity="Easy",
        phase="Build",
    )

    athlete.training_plan.schedule(
        scheduled_at=datetime.combine(
            REFERENCE_DAY
            + timedelta(days=2),
            time.min,
        ),
        sport="Running",
        title="Tempo Run",
        duration=timedelta(
            minutes=60,
        ),
        intensity="Hard",
    )

    result = TodayPresenter(
        athlete
    ).build(
        reference_day=(
            REFERENCE_DAY
        )
    )

    assert (
        result.today_session.title
        == "Easy Run"
    )

    assert (
        result.today_session.is_today
        is True
    )

    assert (
        result.next_workout.title
        == "Easy Run"
    )
    assert (
        "The planned session supports the Build phase."
        in result.guidance.reasons
    )

    assert (
        "The planned session can proceed."
        in result.guidance.reasons
    )
    assert (
        result.guidance.decision
        == "proceed"
    )

    assert (
        result.guidance.title
        == "Follow the planned session"
    )

    assert (
        result.guidance.action
        == (
            "Complete the planned session "
            "within its prescribed duration "
            "and intensity."
        )
    )

    assert (
        result.guidance.plan_is_modified
        is False
    )

    assert (
        result.guidance
        .temporary_adjustment
        is None
    )

    assert (
        "Stay within the planned duration and intensity."
        in result.guidance.cautions
    )


def test_completed_today_moves_to_next_workout():

    athlete = Athlete(
        name="Pedro"
    )

    athlete.training_plan.schedule(
        scheduled_at=datetime.combine(
            REFERENCE_DAY,
            time.min,
        ),
        sport="Running",
        title="Easy Run",
        duration=timedelta(
            minutes=45,
        ),
        intensity="Easy",
    )

    future_day = (
        REFERENCE_DAY
        + timedelta(days=2)
    )

    athlete.training_plan.schedule(
        scheduled_at=datetime.combine(
            future_day,
            time.min,
        ),
        sport="Running",
        title="Tempo Run",
        duration=timedelta(
            minutes=60,
        ),
        intensity="Hard",
    )

    athlete.history.add(
        create_workout(
            sport="Running",
            workout_date=(
                REFERENCE_DAY
            ),
            distance=8.0,
            duration=timedelta(
                minutes=45,
            ),
            elevation_gain=0.0,
            rpe=5.0,
            title="Easy Run",
        )
    )

    result = TodayPresenter(
        athlete
    ).build(
        reference_day=(
            REFERENCE_DAY
        )
    )

    assert (
        result.today_session.completed
        is True
    )

    assert (
        result.next_workout.title
        == "Tempo Run"
    )

    assert (
        result.next_workout
        .scheduled_at
        .date()
        == future_day
    )
    assert (
        result.guidance.decision
        == "completed"
    )

    assert (
        result.guidance.title
        == "Today's training is complete"
    )

    assert (
        result.guidance.action
        == (
            "The completed activity is today's "
            "training stimulus. Use the remaining "
            "day for recovery."
        )
    )

    assert (
        result.guidance
        .temporary_adjustment
        is None
    )

    assert (
        result.guidance.plan_is_modified
        is False
    )

    assert (
        result.latest_activity_summary
        is not None
    )

    assert (
        result.latest_activity_summary
        .title
        == "Easy Run"
    )

    assert (
        result.latest_activity_summary
        .planned_title
        == "Easy Run"
    )

def test_exposes_immutable_daily_readiness():

    athlete = Athlete(
        name="Pedro"
    )

    result = TodayPresenter(
        athlete
    ).build(
        reference_day=(
            REFERENCE_DAY
        )
    )

    assert (
        result.readiness.recovery_score
        == result.recovery.score
    )

    assert (
        result.readiness.recovery_status
        == result.recovery.status
    )

    assert (
        result.readiness.form
        == athlete.analytics
        .training_state
        .form
    )

    assert (
        result.readiness.recent_load
        == result.training_load
        .acute_load
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        result.readiness.form = 1.0

    with pytest.raises(
        FrozenInstanceError
    ):
        result.guidance.reasons = ()
def test_exposes_time_aware_readiness():

    athlete = Athlete(
        name="Pedro"
    )

    workout = create_workout(
        sport="Running",
        workout_date=datetime(
            2026,
            8,
            11,
            7,
            0,
        ),
        distance=10.0,
        duration=timedelta(
            hours=1,
        ),
        elevation_gain=100.0,
        rpe=3.0,
        title="Easy Run",
    )

    athlete.history.add(
        workout
    )

    reference_time = datetime(
        2026,
        8,
        12,
        14,
        0,
    )

    result = TodayPresenter(
        athlete
    ).build(
        reference_time=reference_time,
    )

    assert (
        result.reference_day
        == reference_time.date()
    )
    assert (
        result.readiness.reference_time
        == reference_time
    )
    assert (
        result.readiness
        .hours_since_last_workout
        == 30.0
    )
    assert (
        result.readiness
        .recovery_is_time_aware
        is True
    )

    assert (
        result.readiness.recovery_score
        == athlete.analytics
        .training_state_at(
            reference_time=(
                reference_time
            )
        )
        .recovery_score
    )


def test_today_readiness_falls_back_to_daily_estimate():

    athlete = Athlete(
        name="Pedro"
    )

    workout = create_workout(
        sport="Running",
        workout_date=date(
            2026,
            8,
            12,
        ),
        distance=10.0,
        duration=timedelta(
            hours=1,
        ),
        elevation_gain=100.0,
        rpe=6.0,
        title="Run without time",
    )

    athlete.history.add(
        workout
    )

    reference_time = datetime(
        2026,
        8,
        12,
        18,
        0,
    )

    result = TodayPresenter(
        athlete
    ).build(
        reference_time=reference_time,
    )

    assert (
        result.readiness
        .recovery_is_time_aware
        is False
    )
    assert (
        result.readiness
        .hours_since_last_workout
        is None
    )
    assert (
        result.readiness.recovery_score
        == athlete.analytics
        .training_state
        .recovery_score
    )


def test_rejects_mismatched_reference_time():

    athlete = Athlete(
        name="Pedro"
    )

    with pytest.raises(
        ValueError,
        match=(
            "reference_time must belong "
            "to reference_day"
        ),
    ):
        TodayPresenter(
            athlete
        ).build(
            reference_day=date(
                2026,
                8,
                11,
            ),
            reference_time=datetime(
                2026,
                8,
                12,
                10,
                0,
            ),
        )
        
def test_exposes_latest_plan_adaptation():

    athlete = Athlete(
        name="Pedro"
    )

    adaptation = TrainingPlanAdaptation(
        reconciled_on=date(
            2026,
            8,
            4,
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

    athlete.training_plan.adaptations = (
        adaptation,
    )

    result = TodayPresenter(
        athlete
    ).build(
        reference_day=date(
            2026,
            8,
            4,
        )
    )

    assert (
        result.latest_adaptation
        is not None
    )
    assert (
        result.latest_adaptation
        .workout_title
        == "LT2 Run"
    )
    assert (
        result.latest_adaptation
        .previous_minutes
        == 50
    )
    assert (
        result.latest_adaptation
        .revised_minutes
        == 38
    )
    assert (
        result.latest_adaptation
        .reason
        == (
            "Completed load was higher "
            "than planned."
        )
    )
def test_presents_recovery_as_planned_decision():

    assert (
        TodayPresenter
        ._decision_title(
            DailyTrainingDecision
            .RECOVERY_AS_PLANNED
        )
        == "Follow the recovery session"
    )

    assert (
        TodayPresenter
        ._decision_action(
            DailyTrainingDecision
            .RECOVERY_AS_PLANNED
        )
        == (
            "Complete the planned recovery "
            "session only if it feels "
            "appropriate. Rest remains a "
            "valid option."
        )
    )

def test_presents_recovery_only_decision():

    assert (
        TodayPresenter
        ._decision_title(
            DailyTrainingDecision
            .RECOVERY_ONLY
        )
        == "Prioritise recovery today"
    )

    assert (
        TodayPresenter
        ._decision_action(
            DailyTrainingDecision
            .RECOVERY_ONLY
        )
        == (
            "Do not perform the planned "
            "training stimulus. Choose rest "
            "or very light recovery work "
            "according to how you feel."
        )
    )


def test_presents_easy_only_decision():

    assert (
        TodayPresenter
        ._decision_title(
            DailyTrainingDecision
            .EASY_ONLY
        )
        == "Train easy today"
    )

    assert (
        TodayPresenter
        ._decision_action(
            DailyTrainingDecision
            .EASY_ONLY
        )
        == (
            "Replace the planned intensity "
            "with a shorter easy session."
        )
    )

def test_presents_temporary_workout_adjustment():

    adjustment = TemporaryWorkoutAdjustment(
        title=(
            "Rest or very light recovery"
        ),
        intensity="Very easy",
        maximum_duration=timedelta(
            minutes=20,
        ),
        replaces_planned_session=True,
        explanation=(
            "Rest is valid. If choosing active "
            "recovery, keep it very light."
        ),
    )

    result = (
        TodayPresenter
        ._temporary_adjustment_data(
            adjustment
        )
    )

    assert result is not None

    assert (
        result.title
        == "Rest or very light recovery"
    )

    assert (
        result.intensity
        == "Very easy"
    )

    assert (
        result.maximum_minutes
        == 20
    )

    assert (
        result.replaces_planned_session
        is True
    )

    assert (
        result.explanation
        == (
            "Rest is valid. If choosing active "
            "recovery, keep it very light."
        )
    )

def test_omits_missing_temporary_adjustment():

    assert (
        TodayPresenter
        ._temporary_adjustment_data(
            None
        )
        is None
    )