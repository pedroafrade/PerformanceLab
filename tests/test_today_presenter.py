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
from performancelab.presentation import (
    TodayData,
    TodayPresenter,
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