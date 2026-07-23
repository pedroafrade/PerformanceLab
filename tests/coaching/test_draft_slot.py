"""
Tests for DraftTrainingSlot.
"""

import pytest

from performancelab.training.config.availability import Weekday
from performancelab.coaching.draft_slot import (
    DraftTrainingSlot,
)
from performancelab.coaching.session_purpose import (
    SessionPurpose,
)


def test_creates_training_slot() -> None:

    slot = DraftTrainingSlot(
        weekday=Weekday.MONDAY,
        purpose=SessionPurpose.EASY,
        duration_minutes=45,
    )

    assert slot.weekday is Weekday.MONDAY
    assert slot.purpose is SessionPurpose.EASY
    assert slot.duration_minutes == 45
    assert slot.notes is None


def test_accepts_enum_values_as_strings() -> None:

    slot = DraftTrainingSlot(
        weekday=Weekday.MONDAY.value,
        purpose="easy",
        duration_minutes=45,
    )

    assert slot.weekday is Weekday.MONDAY
    assert slot.purpose is SessionPurpose.EASY


def test_rest_factory_creates_rest_slot() -> None:

    slot = DraftTrainingSlot.rest(
        Weekday.FRIDAY,
        notes="Recovery before the weekend.",
    )

    assert slot.weekday is Weekday.FRIDAY
    assert slot.purpose is SessionPurpose.REST
    assert slot.duration_minutes is None
    assert slot.is_rest is True
    assert slot.is_training is False


def test_training_slot_properties() -> None:

    slot = DraftTrainingSlot(
        weekday=Weekday.TUESDAY,
        purpose=SessionPurpose.INTENSITY,
        duration_minutes=60,
    )

    assert slot.is_rest is False
    assert slot.is_training is True
    assert slot.is_intensity is True
    assert slot.is_long is False
    assert slot.is_quality is True
    assert slot.has_duration is True


def test_long_slot_properties() -> None:

    slot = DraftTrainingSlot(
        weekday=Weekday.SUNDAY,
        purpose=SessionPurpose.LONG,
        duration_minutes=90,
    )

    assert slot.is_long is True
    assert slot.is_intensity is False
    assert slot.is_quality is True


def test_training_slot_may_temporarily_have_no_duration() -> None:

    slot = DraftTrainingSlot(
        weekday=Weekday.WEDNESDAY,
        purpose=SessionPurpose.EASY,
    )

    assert slot.duration_minutes is None
    assert slot.has_duration is False
    assert slot.is_training is True


def test_rejects_negative_duration() -> None:

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):

        DraftTrainingSlot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=-1,
        )


def test_rejects_boolean_duration() -> None:

    with pytest.raises(
        TypeError,
        match="must be an integer",
    ):

        DraftTrainingSlot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=True,
        )


def test_rest_slot_cannot_have_duration() -> None:

    with pytest.raises(
        ValueError,
        match="rest slot cannot have a duration",
    ):

        DraftTrainingSlot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.REST,
            duration_minutes=30,
        )


def test_rejects_invalid_weekday() -> None:

    with pytest.raises(
        ValueError,
        match="Invalid weekday",
    ):

        DraftTrainingSlot(
            weekday="not-a-weekday",
            purpose=SessionPurpose.EASY,
        )


def test_rejects_invalid_session_purpose() -> None:

    with pytest.raises(
        ValueError,
        match="Invalid session purpose",
    ):

        DraftTrainingSlot(
            weekday=Weekday.MONDAY,
            purpose="not-a-purpose",
        )


def test_notes_are_stripped() -> None:

    slot = DraftTrainingSlot(
        weekday=Weekday.MONDAY,
        purpose=SessionPurpose.EASY,
        notes="  Easy aerobic session.  ",
    )

    assert slot.notes == "Easy aerobic session."


def test_empty_notes_become_none() -> None:

    slot = DraftTrainingSlot(
        weekday=Weekday.MONDAY,
        purpose=SessionPurpose.EASY,
        notes="",
    )

    assert slot.notes is None


def test_with_purpose_returns_new_slot() -> None:

    original = DraftTrainingSlot(
        weekday=Weekday.MONDAY,
        purpose=SessionPurpose.EASY,
        duration_minutes=45,
    )

    changed = original.with_purpose(
        SessionPurpose.INTENSITY,
    )

    assert changed is not original

    assert original.purpose is SessionPurpose.EASY
    assert changed.purpose is SessionPurpose.INTENSITY

    assert changed.weekday is Weekday.MONDAY
    assert changed.duration_minutes == 45


def test_changing_purpose_to_rest_removes_duration() -> None:

    original = DraftTrainingSlot(
        weekday=Weekday.MONDAY,
        purpose=SessionPurpose.EASY,
        duration_minutes=45,
    )

    changed = original.with_purpose(
        SessionPurpose.REST,
    )

    assert changed.is_rest is True
    assert changed.duration_minutes is None


def test_with_duration_returns_new_slot() -> None:

    original = DraftTrainingSlot(
        weekday=Weekday.MONDAY,
        purpose=SessionPurpose.EASY,
        duration_minutes=45,
    )

    changed = original.with_duration(60)

    assert original.duration_minutes == 45
    assert changed.duration_minutes == 60
    assert changed is not original


def test_rest_slot_cannot_receive_duration() -> None:

    slot = DraftTrainingSlot.rest(
        Weekday.MONDAY,
    )

    with pytest.raises(
        ValueError,
        match="rest slot cannot have a duration",
    ):

        slot.with_duration(30)


def test_move_to_returns_slot_on_another_weekday() -> None:

    original = DraftTrainingSlot(
        weekday=Weekday.MONDAY,
        purpose=SessionPurpose.EASY,
        duration_minutes=45,
    )

    moved = original.move_to(
        Weekday.THURSDAY,
    )

    assert original.weekday is Weekday.MONDAY
    assert moved.weekday is Weekday.THURSDAY

    assert moved.purpose is SessionPurpose.EASY
    assert moved.duration_minutes == 45


def test_slot_is_immutable() -> None:

    slot = DraftTrainingSlot(
        weekday=Weekday.MONDAY,
        purpose=SessionPurpose.EASY,
        duration_minutes=45,
    )

    with pytest.raises(
        AttributeError,
    ):

        slot.duration_minutes = 60