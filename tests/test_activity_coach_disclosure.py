"""
Tests for the Training Coach data-use disclosure.
"""

from dataclasses import (
    FrozenInstanceError,
)

import pytest

from performancelab.presentation import (
    ActivityCoachDisclosureData,
    build_activity_coach_disclosure,
)


def test_describes_training_coach_data_flow():

    disclosure = (
        build_activity_coach_disclosure()
    )

    assert isinstance(
        disclosure,
        ActivityCoachDisclosureData,
    )

    assert (
        disclosure.heading
        == "Before you generate"
    )

    assert (
        disclosure.provider
        == "Google Gemini"
    )

    assert "Google Gemini" in (
        disclosure.purpose
    )

    assert "activity facts" in (
        disclosure.data_summary
    )

    assert "heart-rate" in (
        disclosure.data_summary
    )

    assert "Additional information" in (
        disclosure.data_summary
    )

    assert "recent training" in (
        disclosure.data_summary
    )

    assert "current recovery" in (
        disclosure.data_summary
    )


def test_states_original_file_is_not_sent():

    disclosure = (
        build_activity_coach_disclosure()
    )

    assert (
        disclosure.original_file_sent
        is False
    )


def test_states_interpretation_is_retained():

    disclosure = (
        build_activity_coach_disclosure()
    )

    assert (
        disclosure.interpretation_retained
        is True
    )


def test_marks_result_as_non_medical():

    disclosure = (
        build_activity_coach_disclosure()
    )

    assert (
        "not medical advice"
        in disclosure.limitation
    )


def test_disclosure_is_immutable():

    disclosure = (
        build_activity_coach_disclosure()
    )

    with pytest.raises(
        FrozenInstanceError
    ):

        disclosure.provider = (
            "Another provider"
        )