"""
Tests for Planner event integration.

Place this file at:
    tests/training/planning/test_planner_events.py
"""

from datetime import date, timedelta
from types import SimpleNamespace

from performancelab.coaching import (
    DraftTrainingSlot,
    SessionPurpose,
)
from performancelab.training.config import Weekday
from performancelab.training.planning.planner import Planner


WEEK_START = date(
    2026,
    7,
    20,
)


def make_event_entry(
    *,
    event_date: date,
    name: str = "Test Race",
    target_time: timedelta | None = None,
):
    """
    Creates the minimal event entry required by Planner.

    SimpleNamespace keeps these tests focused on Planner behaviour
    instead of Event and EventEntry validation.
    """

    event = SimpleNamespace(
        date=event_date,
        name=name,
    )

    return SimpleNamespace(
        event=event,
        target_time=target_time,
    )


def make_slot(
    *,
    weekday: Weekday,
    purpose: SessionPurpose,
    duration_minutes: int | None = None,
) -> DraftTrainingSlot:
    """
    Creates a draft training slot.
    """

    if purpose is SessionPurpose.REST:
        return DraftTrainingSlot.rest(
            weekday
        )

    return DraftTrainingSlot(
        weekday=weekday,
        purpose=purpose,
        duration_minutes=duration_minutes,
    )


def test_keeps_slots_when_next_event_is_none() -> None:
    slots = (
        make_slot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=45,
        ),
        make_slot(
            weekday=Weekday.SUNDAY,
            purpose=SessionPurpose.LONG,
            duration_minutes=90,
        ),
    )

    result = Planner._apply_event_to_week(
        slots=slots,
        week_start=WEEK_START,
        next_event=None,
    )

    assert result == slots


def test_keeps_slots_when_event_has_no_date() -> None:
    slots = (
        make_slot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=45,
        ),
    )

    next_event = SimpleNamespace(
        event=SimpleNamespace(
            date=None,
            name="Undated Race",
        ),
        target_time=None,
    )

    result = Planner._apply_event_to_week(
        slots=slots,
        week_start=WEEK_START,
        next_event=next_event,
    )

    assert result == slots


def test_keeps_slots_when_event_is_outside_week() -> None:
    slots = (
        make_slot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=45,
        ),
        make_slot(
            weekday=Weekday.SUNDAY,
            purpose=SessionPurpose.LONG,
            duration_minutes=90,
        ),
    )

    next_event = make_event_entry(
        event_date=date(
            2026,
            8,
            2,
        ),
    )

    result = Planner._apply_event_to_week(
        slots=slots,
        week_start=WEEK_START,
        next_event=next_event,
    )

    assert result == slots


def test_replaces_matching_training_slot_with_race() -> None:
    slots = (
        make_slot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=45,
        ),
        make_slot(
            weekday=Weekday.SUNDAY,
            purpose=SessionPurpose.LONG,
            duration_minutes=90,
        ),
    )

    next_event = make_event_entry(
        event_date=date(
            2026,
            7,
            26,
        ),
        name="City Half Marathon",
        target_time=timedelta(
            hours=1,
            minutes=35,
        ),
    )

    result = Planner._apply_event_to_week(
        slots=slots,
        week_start=WEEK_START,
        next_event=next_event,
    )

    sunday_slot = next(
        slot
        for slot in result
        if slot.weekday is Weekday.SUNDAY
    )

    assert sunday_slot.purpose is SessionPurpose.RACE
    assert sunday_slot.duration_minutes == 95
    assert (
        "City Half Marathon"
        in sunday_slot.notes
    )


def test_uses_original_slot_duration_without_target_time() -> None:
    slots = (
        make_slot(
            weekday=Weekday.SUNDAY,
            purpose=SessionPurpose.LONG,
            duration_minutes=120,
        ),
    )

    next_event = make_event_entry(
        event_date=date(
            2026,
            7,
            26,
        ),
        target_time=None,
    )

    result = Planner._apply_event_to_week(
        slots=slots,
        week_start=WEEK_START,
        next_event=next_event,
    )

    race_slot = result[0]

    assert race_slot.purpose is SessionPurpose.RACE
    assert race_slot.duration_minutes == 120


def test_allows_race_without_duration_when_replacing_rest() -> None:
    slots = (
        make_slot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=45,
        ),
        make_slot(
            weekday=Weekday.WEDNESDAY,
            purpose=SessionPurpose.INTENSITY,
            duration_minutes=60,
        ),
        make_slot(
            weekday=Weekday.SUNDAY,
            purpose=SessionPurpose.REST,
        ),
    )

    next_event = make_event_entry(
        event_date=date(
            2026,
            7,
            26,
        ),
        target_time=None,
    )

    result = Planner._apply_event_to_week(
        slots=slots,
        week_start=WEEK_START,
        next_event=next_event,
    )

    race_slot = next(
        slot
        for slot in result
        if slot.weekday is Weekday.SUNDAY
    )

    assert race_slot.purpose is SessionPurpose.RACE
    assert race_slot.duration_minutes is None


def test_replaces_easy_session_with_rest_when_race_uses_rest_day() -> None:
    slots = (
        make_slot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=45,
        ),
        make_slot(
            weekday=Weekday.WEDNESDAY,
            purpose=SessionPurpose.INTENSITY,
            duration_minutes=60,
        ),
        make_slot(
            weekday=Weekday.SATURDAY,
            purpose=SessionPurpose.LONG,
            duration_minutes=100,
        ),
        make_slot(
            weekday=Weekday.SUNDAY,
            purpose=SessionPurpose.REST,
        ),
    )

    original_training_count = sum(
        slot.is_training
        for slot in slots
    )

    next_event = make_event_entry(
        event_date=date(
            2026,
            7,
            26,
        ),
        target_time=timedelta(
            hours=1,
            minutes=30,
        ),
    )

    result = Planner._apply_event_to_week(
        slots=slots,
        week_start=WEEK_START,
        next_event=next_event,
    )

    monday_slot = next(
        slot
        for slot in result
        if slot.weekday is Weekday.MONDAY
    )

    sunday_slot = next(
        slot
        for slot in result
        if slot.weekday is Weekday.SUNDAY
    )

    resulting_training_count = sum(
        slot.is_training
        for slot in result
    )

    assert monday_slot.purpose is SessionPurpose.REST
    assert sunday_slot.purpose is SessionPurpose.RACE

    assert (
        resulting_training_count
        == original_training_count
    )


def test_removes_shortest_easy_session_first() -> None:
    slots = (
        make_slot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=50,
        ),
        make_slot(
            weekday=Weekday.TUESDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=30,
        ),
        make_slot(
            weekday=Weekday.THURSDAY,
            purpose=SessionPurpose.RECOVERY,
            duration_minutes=20,
        ),
        make_slot(
            weekday=Weekday.SUNDAY,
            purpose=SessionPurpose.REST,
        ),
    )

    next_event = make_event_entry(
        event_date=date(
            2026,
            7,
            26,
        ),
        target_time=timedelta(
            minutes=45,
        ),
    )

    result = Planner._apply_event_to_week(
        slots=slots,
        week_start=WEEK_START,
        next_event=next_event,
    )

    monday_slot = next(
        slot
        for slot in result
        if slot.weekday is Weekday.MONDAY
    )

    tuesday_slot = next(
        slot
        for slot in result
        if slot.weekday is Weekday.TUESDAY
    )

    thursday_slot = next(
        slot
        for slot in result
        if slot.weekday is Weekday.THURSDAY
    )

    assert monday_slot.purpose is SessionPurpose.EASY
    assert tuesday_slot.purpose is SessionPurpose.REST
    assert thursday_slot.purpose is SessionPurpose.RECOVERY


def test_converts_target_time_to_complete_minutes() -> None:
    next_event = make_event_entry(
        event_date=date(
            2026,
            7,
            26,
        ),
        target_time=timedelta(
            hours=1,
            minutes=42,
            seconds=59,
        ),
    )

    result = Planner._event_duration_minutes(
        next_event
    )

    assert result == 102


def test_returns_none_for_missing_target_time() -> None:
    next_event = make_event_entry(
        event_date=date(
            2026,
            7,
            26,
        ),
        target_time=None,
    )

    result = Planner._event_duration_minutes(
        next_event
    )

    assert result is None


def test_returns_none_for_non_positive_target_time() -> None:
    zero_duration_event = make_event_entry(
        event_date=date(
            2026,
            7,
            26,
        ),
        target_time=timedelta(0),
    )

    negative_duration_event = make_event_entry(
        event_date=date(
            2026,
            7,
            26,
        ),
        target_time=timedelta(
            minutes=-10,
        ),
    )

    assert (
        Planner._event_duration_minutes(
            zero_duration_event
        )
        is None
    )

    assert (
        Planner._event_duration_minutes(
            negative_duration_event
        )
        is None
    )