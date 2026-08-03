"""
Tests for ActivitiesPresenter.
"""

from dataclasses import FrozenInstanceError
from datetime import date, timedelta

import pytest

from performancelab.history import (
    History,
)
from performancelab.presentation import (
    ActivitiesPresenter,
)
from performancelab.workout import (
    Workout,
)


def create_activity(
    *,
    workout_date: date,
    title: str,
    sport: str = "Running",
    distance: float | None = None,
    duration: timedelta | None = None,
    elevation_gain: float | None = None,
    rpe: float | None = None,
) -> Workout:

    workout = Workout()

    workout.info.date = workout_date
    workout.info.title = title
    workout.info.sport = sport
    workout.info.distance = distance
    workout.info.duration = duration
    workout.info.elevation_gain = (
        elevation_gain
    )
    workout.feedback.rpe = rpe

    return workout


def test_builds_activity_list_item():

    workout = create_activity(
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Volta da Ericeira",
        sport="Cycling",
        distance=50.3,
        duration=timedelta(
            hours=2,
            minutes=32,
        ),
        elevation_gain=980,
        rpe=7.5,
    )

    history = History(
        workouts=[
            workout,
        ]
    )

    result = ActivitiesPresenter(
        history
    ).build()

    assert len(result) == 1

    activity = result[0]

    assert (
        activity.workout_id
        == workout.workout_id
    )
    assert (
        activity.workout_date
        == date(2026, 8, 2)
    )
    assert activity.title == (
        "Volta da Ericeira"
    )
    assert activity.sport == "Cycling"
    assert activity.distance == 50.3
    assert activity.duration == timedelta(
        hours=2,
        minutes=32,
    )
    assert activity.elevation_gain == 980
    assert activity.rpe == 7.5


def test_orders_activities_newest_first():

    older = create_activity(
        workout_date=date(
            2026,
            7,
            30,
        ),
        title="Older run",
    )

    newer = create_activity(
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Newer ride",
        sport="Cycling",
    )

    history = History(
        workouts=[
            older,
            newer,
        ]
    )

    result = ActivitiesPresenter(
        history
    ).build()

    assert tuple(
        activity.title
        for activity in result
    ) == (
        "Newer ride",
        "Older run",
    )


def test_places_activity_without_date_last():

    dated = create_activity(
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Dated activity",
    )

    undated = Workout()
    undated.info.title = (
        "Undated activity"
    )

    history = History(
        workouts=[
            dated,
            undated,
        ]
    )

    result = ActivitiesPresenter(
        history
    ).build()

    assert tuple(
        activity.title
        for activity in result
    ) == (
        "Dated activity",
        "Undated activity",
    )


def test_activity_list_item_is_immutable():

    workout = create_activity(
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Immutable activity",
    )

    activity = ActivitiesPresenter(
        History(
            workouts=[
                workout,
            ]
        )
    ).build()[0]

    with pytest.raises(
        FrozenInstanceError
    ):
        activity.title = "Changed"