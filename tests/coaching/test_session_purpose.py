"""
Tests for SessionPurpose.
"""

from performancelab.coaching.session_purpose import (
    SessionPurpose,
)


def test_rest_is_not_training() -> None:

    assert SessionPurpose.REST.is_training is False


def test_training_purposes_are_training() -> None:

    training_purposes = {
        SessionPurpose.RECOVERY,
        SessionPurpose.EASY,
        SessionPurpose.INTENSITY,
        SessionPurpose.LONG,
        SessionPurpose.RACE,
        SessionPurpose.CROSS_TRAINING,
    }

    assert all(
        purpose.is_training
        for purpose in training_purposes
    )


def test_quality_purposes() -> None:

    assert SessionPurpose.INTENSITY.is_quality is True
    assert SessionPurpose.LONG.is_quality is True
    assert SessionPurpose.RACE.is_quality is True

    assert SessionPurpose.EASY.is_quality is False
    assert SessionPurpose.RECOVERY.is_quality is False
    assert SessionPurpose.REST.is_quality is False
    assert (
        SessionPurpose.CROSS_TRAINING.is_quality
        is False
    )


def test_low_intensity_purposes() -> None:

    assert (
        SessionPurpose.RECOVERY.is_low_intensity
        is True
    )

    assert SessionPurpose.EASY.is_low_intensity is True

    assert (
        SessionPurpose.INTENSITY.is_low_intensity
        is False
    )

    assert SessionPurpose.LONG.is_low_intensity is False
    assert SessionPurpose.RACE.is_low_intensity is False
    assert SessionPurpose.REST.is_low_intensity is False


def test_session_purpose_is_string_enum() -> None:

    assert SessionPurpose.EASY == "easy"
    assert SessionPurpose.LONG.value == "long"


def test_session_purpose_can_be_created_from_string() -> None:

    assert (
        SessionPurpose("intensity")
        is SessionPurpose.INTENSITY
    )