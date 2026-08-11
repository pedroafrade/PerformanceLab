from dataclasses import (
    FrozenInstanceError,
    replace,
)
from datetime import (
    date,
    timedelta,
)

import pytest

from performancelab import (
    Athlete,
    Workout,
)
from performancelab.presentation import (
    ActivityCoachPresenter,
    ActivityListItemData,
)


def create_activity():
    return ActivityListItemData(
        workout_id="workout-1",
        workout_date=date(
            2026,
            8,
            9,
        ),
        sport="Running",
        title="Long Hill Run",
        distance=11.58,
        duration=timedelta(
            hours=1,
            minutes=42,
        ),
        elevation_gain=632.0,
        rpe=7.7,
        outcome_status="modified",
        planned_title="Long Run",
        planned_load=419.0,
        completed_load=789.0,
        load_difference=370.0,
    )


def create_workout():
    workout = Workout()

    workout.sensors.add(
        "heart_rate",
        [
            {
                "value": 160,
            },
            {
                "value": 168,
            },
            {
                "value": 185,
            },
        ],
    )

    workout.sensors.add(
        "power",
        [
            {
                "value": 190,
            },
            {
                "value": 214,
            },
        ],
    )

    workout.sensors.add(
        "cadence",
        [
            {
                "value": 138,
            },
            {
                "value": 144,
            },
        ],
    )

    workout.environment.temperature = 20.0
    workout.environment.humidity = 89.0
    workout.environment.terrain = "Trail"

    return workout


def test_builds_activity_coach_context():

    context = ActivityCoachPresenter(
        activity=create_activity(),
        workout=create_workout(),
    ).build()

    assert context.activity.title == (
        "Long Hill Run"
    )

    assert context.heart_rate.average == (
        pytest.approx(171.0)
    )
    assert context.heart_rate.maximum == 185.0

    assert context.power.average == (
        pytest.approx(202.0)
    )
    assert context.power.maximum == 214.0

    assert context.cadence.average == (
        pytest.approx(141.0)
    )
    assert context.cadence.maximum == 144.0

    assert context.temperature == 20.0
    assert context.humidity == 89.0
    assert context.terrain == "Trail"


def test_activity_coach_context_is_immutable():

    context = ActivityCoachPresenter(
        activity=create_activity(),
        workout=create_workout(),
    ).build()

    with pytest.raises(
        FrozenInstanceError
    ):
        context.temperature = 25.0

def test_builds_recent_training_context():

    athlete = Athlete(
        name="Pedro"
    )

    previous = Workout()
    previous.info.title = "Easy Run"
    previous.info.sport = "Running"
    previous.info.date = date(
        2026,
        8,
        6,
    )
    previous.info.duration = timedelta(
        minutes=60
    )
    previous.feedback.rpe = 5.0

    current = create_workout()
    current.info.title = (
        "Long Hill Run"
    )
    current.info.sport = "Running"
    current.info.date = date(
        2026,
        8,
        9,
    )
    current.info.duration = timedelta(
        minutes=102
    )
    current.feedback.rpe = 7.7

    athlete.history.add(
        previous
    )
    athlete.history.add(
        current
    )

    activity = replace(
        create_activity(),
        workout_id=str(
            current.workout_id
        ),
    )

    context = ActivityCoachPresenter(
        activity=activity,
        workout=current,
        athlete=athlete,
    ).build()

    recent = (
        context.recent_training
    )

    assert recent.window_days == 7
    assert recent.session_count == 2

    assert (
        recent.total_duration_minutes
        == pytest.approx(162.0)
    )

    assert recent.total_load > 0

    assert recent.previous_title == (
        "Easy Run"
    )
    assert (
        recent.previous_days_before
        == 3
    )
    assert (
        recent.previous_load
        == pytest.approx(300.0)
    )


def test_recent_training_context_is_immutable():

    athlete = Athlete(
        name="Pedro"
    )

    context = ActivityCoachPresenter(
        activity=create_activity(),
        workout=create_workout(),
        athlete=athlete,
    ).build()

    with pytest.raises(
        FrozenInstanceError
    ):
        (
            context
            .recent_training
            .session_count
        ) = 3