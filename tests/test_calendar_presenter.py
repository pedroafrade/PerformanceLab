"""
Tests for the monthly CalendarPresenter.
"""

from dataclasses import FrozenInstanceError
from datetime import date, datetime, timedelta

import pytest

from performancelab.history import (
    History,
)
from performancelab.presentation import (
    CalendarPresenter,
)
from performancelab.race import (
    Event,
    EventBook,
    EventEntry,
)
from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
)
from performancelab.workout import (
    Workout,
)


def calendar_day(
    calendar,
    target_day: date,
):

    return next(
        day
        for week in calendar.weeks
        for day in week
        if day.day == target_day
    )


def test_builds_monday_first_calendar_month():

    result = CalendarPresenter(
        history=History(),
        training_plan=TrainingPlan(),
        events=EventBook(),
    ).build(
        year=2026,
        month=8,
        reference_day=date(
            2026,
            8,
            3,
        ),
    )

    assert result.year == 2026
    assert result.month == 8

    assert (
        result.weeks[0][0].day
        == date(2026, 7, 27)
    )

    assert (
        result.weeks[0][-1].day
        == date(2026, 8, 2)
    )

    assert all(
        len(week) == 7
        for week in result.weeks
    )


def test_combines_plan_history_and_event():

    completed = Workout(
        workout_id="completed-ride"
    )
    completed.info.date = date(
        2026,
        8,
        2,
    )
    completed.info.title = (
        "Volta da Ericeira"
    )
    completed.info.sport = "Cycling"
    completed.info.duration = timedelta(
        hours=2,
    )
    completed.feedback.rpe = 7

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
        phase="Peak",
    )

    event = Event(
        event_id="event-1",
        name="Sealand",
        date=date(
            2026,
            8,
            9,
        ),
        sport="Road Running",
        distance=10,
    )

    entry = EventEntry(
        event=event,
        priority="A",
    )

    result = CalendarPresenter(
        history=History(
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
            workouts=[
                planned,
            ],
        ),
        events=EventBook(
            entries=[
                entry,
            ]
        ),
    ).build(
        year=2026,
        month=8,
        reference_day=date(
            2026,
            8,
            3,
        ),
    )

    second_august = calendar_day(
        result,
        date(
            2026,
            8,
            2,
        ),
    )

    assert {
        item.kind
        for item in second_august.items
    } == {
        "planned",
        "completed",
    }

    completed_item = next(
        item
        for item in second_august.items
        if item.kind == "completed"
    )

    assert (
        completed_item.status
        == "substitute"
    )

    ninth_august = calendar_day(
        result,
        date(
            2026,
            8,
            9,
        ),
    )

    assert (
        ninth_august.items[0].kind
        == "event"
    )
    assert (
        ninth_august.items[0].title
        == "Sealand"
    )
    assert (
        ninth_august.items[0].priority
        == "A"
    )


def test_marks_today_and_current_month():

    result = CalendarPresenter(
        history=History(),
        training_plan=TrainingPlan(),
        events=EventBook(),
    ).build(
        year=2026,
        month=8,
        reference_day=date(
            2026,
            8,
            3,
        ),
    )

    today = calendar_day(
        result,
        date(
            2026,
            8,
            3,
        ),
    )

    previous_month = calendar_day(
        result,
        date(
            2026,
            7,
            27,
        ),
    )

    assert today.is_today is True
    assert today.is_current_month is True

    assert (
        previous_month.is_current_month
        is False
    )


def test_calendar_models_are_immutable():

    result = CalendarPresenter(
        history=History(),
        training_plan=TrainingPlan(),
        events=EventBook(),
    ).build(
        year=2026,
        month=8,
        reference_day=date(
            2026,
            8,
            3,
        ),
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        result.month = 9


def test_rejects_invalid_month():

    presenter = CalendarPresenter(
        history=History(),
        training_plan=TrainingPlan(),
        events=EventBook(),
    )

    with pytest.raises(
        ValueError
    ):
        presenter.build(
            year=2026,
            month=13,
            reference_day=date(
                2026,
                8,
                3,
            ),
        )