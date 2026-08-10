from dataclasses import (
    FrozenInstanceError,
)
from datetime import (
    date,
    timedelta,
)

import pytest

from performancelab import Workout
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