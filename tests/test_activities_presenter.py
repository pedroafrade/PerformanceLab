"""
Tests for ActivitiesPresenter.
"""

from dataclasses import FrozenInstanceError
from datetime import date, datetime, timedelta

import pytest

from performancelab.history import (
    History,
)
from performancelab.presentation import (
    ActivitiesPresenter,
    ActivityFilters,
    ActivityListItemData,
)
from performancelab.workout import (
    Workout,
)

from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
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



def test_filters_activities_by_sport():

    run = create_activity(
        workout_date=date(
            2026,
            8,
            1,
        ),
        title="Morning run",
        sport="Running",
    )

    ride = create_activity(
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Evening ride",
        sport="Cycling",
    )

    result = ActivitiesPresenter(
        History(
            workouts=[
                run,
                ride,
            ]
        )
    ).build(
        filters=ActivityFilters(
            sport="Cycling"
        )
    )

    assert tuple(
        activity.title
        for activity in result
    ) == (
        "Evening ride",
    )


def test_filters_activities_by_title():

    run = create_activity(
        workout_date=date(
            2026,
            8,
            1,
        ),
        title="Morning Easy Run",
    )

    ride = create_activity(
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Long Ride",
        sport="Cycling",
    )

    result = ActivitiesPresenter(
        History(
            workouts=[
                run,
                ride,
            ]
        )
    ).build(
        filters=ActivityFilters(
            query="easy"
        )
    )

    assert tuple(
        activity.title
        for activity in result
    ) == (
        "Morning Easy Run",
    )


def test_filters_activities_by_date_range():

    older = create_activity(
        workout_date=date(
            2026,
            6,
            1,
        ),
        title="Older run",
    )

    recent = create_activity(
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Recent run",
    )

    result = ActivitiesPresenter(
        History(
            workouts=[
                older,
                recent,
            ]
        )
    ).build(
        filters=ActivityFilters(
            start_date=date(
                2026,
                7,
                5,
            ),
            end_date=date(
                2026,
                8,
                3,
            ),
        )
    )

    assert tuple(
        activity.title
        for activity in result
    ) == (
        "Recent run",
    )



def test_attaches_plan_outcome_to_activity():

    completed = create_activity(
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Volta da Ericeira",
        sport="Cycling",
        duration=timedelta(
            minutes=60,
        ),
        rpe=7,
    )

    planned = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            2,
            8,
            0,
        ),
        sport="Trail Running",
        title="Long Run",
        duration=timedelta(
            minutes=60,
        ),
        intensity="Hard",
    )

    history = History(
        workouts=[
            completed,
        ]
    )

    result = ActivitiesPresenter(
        history,
        training_plan=TrainingPlan(
            workouts=[
                planned,
            ]
        ),
        reference_day=date(
            2026,
            8,
            3,
        ),
    ).build()

    assert (
        result[0].outcome_status
        == "substitute"
    )
    assert (
        result[0].planned_title
        == "Long Run"
    )
    assert (
        result[0].planned_load
        == 420
    )
    assert (
        result[0].completed_load
        == 420
    )
    assert (
        result[0].load_difference
        == 0
    )


def test_activity_inside_plan_can_be_unplanned():

    completed = create_activity(
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Unplanned run",
    )

    result = ActivitiesPresenter(
        History(
            workouts=[
                completed,
            ]
        ),
        training_plan=TrainingPlan(
            start_date=date(
                2026,
                8,
                1,
            ),
            end_date=date(
                2026,
                8,
                31,
            ),
        ),
        reference_day=date(
            2026,
            8,
            3,
        ),
    ).build()

    assert (
        result[0].outcome_status
        == "unplanned"
    )
    assert (
        result[0].planned_title
        is None
    )
    assert (
        result[0].planned_load
        is None
    )
    assert (
        result[0].completed_load
        is None
    )
    assert (
        result[0].load_difference
        is None
    )


def test_activity_before_plan_is_outside_plan():

    completed = create_activity(
        workout_date=date(
            2026,
            7,
            20,
        ),
        title="Historical run",
    )

    result = ActivitiesPresenter(
        History(
            workouts=[
                completed,
            ]
        ),
        training_plan=TrainingPlan(
            start_date=date(
                2026,
                8,
                1,
            ),
            end_date=date(
                2026,
                8,
                31,
            ),
        ),
        reference_day=date(
            2026,
            8,
            3,
        ),
    ).build()

    assert (
        result[0].outcome_status
        == "outside_plan"
    )

def test_filters_activity_by_plan_result():

    activity = ActivityListItemData(
        workout_id="modified-activity",
        workout_date=date(
            2026,
            8,
            2,
        ),
        sport="Running",
        title="Shortened run",
        distance=5,
        duration=timedelta(
            minutes=30,
        ),
        elevation_gain=0,
        rpe=5,
        outcome_status="modified",
    )

    assert ActivitiesPresenter._matches_filters(
        activity,
        ActivityFilters(
            outcome_status="modified"
        ),
    )

    assert not (
        ActivitiesPresenter
        ._matches_filters(
            activity,
            ActivityFilters(
                outcome_status="equivalent"
            ),
        )
    )


def test_filters_unplanned_activity():

    activity = ActivityListItemData(
        workout_id="unplanned-activity",
        workout_date=date(
            2026,
            8,
            2,
        ),
        sport="Cycling",
        title="Unplanned ride",
        distance=40,
        duration=timedelta(
            hours=2,
        ),
        elevation_gain=500,
        rpe=5,
        outcome_status="unplanned",
    )

    assert ActivitiesPresenter._matches_filters(
        activity,
        ActivityFilters(
            outcome_status="unplanned"
        ),
    )

    assert not (
        ActivitiesPresenter
        ._matches_filters(
            activity,
            ActivityFilters(
                outcome_status="substitute"
            ),
        )
    )