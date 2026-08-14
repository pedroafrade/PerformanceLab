from datetime import date

import pytest

from performancelab import (
    VO2MaxObservation,
    VO2MaxObservationBook,
    parse_vo2max_observation,
    synchronize_vo2max_observation_from_notes,
)


def test_observation_preserves_factual_context():

    observation = VO2MaxObservation(
        observed_at=date(
            2026,
            8,
            14,
        ),
        value=52.4,
        source="manual",
        method="apple-watch-estimate",
        workout_id="workout-1",
    )

    assert observation.value == 52.4
    assert observation.source == "manual"
    assert (
        observation.method
        == "apple-watch-estimate"
    )
    assert (
        observation.workout_id
        == "workout-1"
    )


def test_book_orders_observations_by_date():

    observations = VO2MaxObservationBook()

    observations.add(
        VO2MaxObservation(
            observed_at=date(
                2026,
                8,
                14,
            ),
            value=52.4,
            source="manual",
            method="device-estimate",
        )
    )
    observations.add(
        VO2MaxObservation(
            observed_at=date(
                2026,
                7,
                10,
            ),
            value=50.1,
            source="manual",
            method="device-estimate",
        )
    )

    assert [
        observation.value
        for observation in observations
    ] == [
        50.1,
        52.4,
    ]


def test_same_identity_is_replaced():

    observations = VO2MaxObservationBook()

    observations.add(
        VO2MaxObservation(
            observed_at=date(
                2026,
                8,
                14,
            ),
            value=51.0,
            source="manual",
            method="device-estimate",
        )
    )
    observations.add(
        VO2MaxObservation(
            observed_at=date(
                2026,
                8,
                14,
            ),
            value=52.4,
            source="manual",
            method="device-estimate",
        )
    )

    stored = tuple(
        observations
    )

    assert len(stored) == 1
    assert stored[0].value == 52.4


def test_different_sources_are_preserved():

    observations = VO2MaxObservationBook()

    observations.add(
        VO2MaxObservation(
            observed_at=date(
                2026,
                8,
                14,
            ),
            value=52.4,
            source="apple-health",
            method="device-estimate",
        )
    )
    observations.add(
        VO2MaxObservation(
            observed_at=date(
                2026,
                8,
                14,
            ),
            value=54.1,
            source="laboratory",
            method="cardiopulmonary-test",
        )
    )

    assert len(
        observations
    ) == 2


def test_rejects_non_positive_value():

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        VO2MaxObservation(
            observed_at=date(
                2026,
                8,
                14,
            ),
            value=0,
            source="manual",
            method="device-estimate",
        )


def test_rejects_empty_source():

    with pytest.raises(
        ValueError,
        match="source",
    ):
        VO2MaxObservation(
            observed_at=date(
                2026,
                8,
                14,
            ),
            value=52.4,
            source="",
            method="device-estimate",
        )

def test_parses_apple_watch_observation():

    observation = (
        parse_vo2max_observation(
            notes=(
                "Felt good. "
                "VO2max: 52.4 Apple Watch."
            ),
            observed_at=date(
                2026,
                8,
                14,
            ),
            workout_id="workout-1",
        )
    )

    assert observation is not None
    assert observation.value == 52.4
    assert (
        observation.source
        == "manual"
    )
    assert (
        observation.method
        == "apple-watch-estimate"
    )
    assert (
        observation.workout_id
        == "workout-1"
    )


def test_parses_decimal_comma():

    observation = (
        parse_vo2max_observation(
            notes="VO₂max = 51,7",
            observed_at=date(
                2026,
                8,
                14,
            ),
            workout_id="workout-1",
        )
    )

    assert observation is not None
    assert observation.value == 51.7
    assert (
        observation.method
        == "unspecified-estimate"
    )


def test_does_not_infer_from_unstructured_text():

    observation = (
        parse_vo2max_observation(
            notes=(
                "The watch showed better "
                "cardio fitness today."
            ),
            observed_at=date(
                2026,
                8,
                14,
            ),
            workout_id="workout-1",
        )
    )

    assert observation is None


def test_does_not_create_observation_without_date():

    observation = (
        parse_vo2max_observation(
            notes="VO2max: 52.4 Apple Watch",
            observed_at=None,
            workout_id="workout-1",
        )
    )

    assert observation is None


def test_synchronizes_edited_observation():

    observations = (
        VO2MaxObservationBook()
    )

    synchronize_vo2max_observation_from_notes(
        observations=observations,
        notes="VO2max: 51.2 Apple Watch",
        observed_at=date(
            2026,
            8,
            14,
        ),
        workout_id="workout-1",
    )

    changed = (
        synchronize_vo2max_observation_from_notes(
            observations=observations,
            notes="VO2max: 52.4 Apple Watch",
            observed_at=date(
                2026,
                8,
                14,
            ),
            workout_id="workout-1",
        )
    )

    stored = tuple(
        observations
    )

    assert changed is True
    assert len(stored) == 1
    assert stored[0].value == 52.4


def test_removes_observation_when_note_is_removed():

    observations = (
        VO2MaxObservationBook(
            observations=(
                VO2MaxObservation(
                    observed_at=date(
                        2026,
                        8,
                        14,
                    ),
                    value=52.4,
                    source="manual",
                    method=(
                        "apple-watch-estimate"
                    ),
                    workout_id="workout-1",
                ),
            )
        )
    )

    changed = (
        synchronize_vo2max_observation_from_notes(
            observations=observations,
            notes="Felt good.",
            observed_at=date(
                2026,
                8,
                14,
            ),
            workout_id="workout-1",
        )
    )

    assert changed is True
    assert len(observations) == 0


def test_synchronization_is_idempotent():

    observations = (
        VO2MaxObservationBook()
    )

    synchronize_vo2max_observation_from_notes(
        observations=observations,
        notes="VO2max: 52.4 Apple Watch",
        observed_at=date(
            2026,
            8,
            14,
        ),
        workout_id="workout-1",
    )

    changed = (
        synchronize_vo2max_observation_from_notes(
            observations=observations,
            notes="VO2max: 52.4 Apple Watch",
            observed_at=date(
                2026,
                8,
                14,
            ),
            workout_id="workout-1",
        )
    )

    assert changed is False
    assert len(observations) == 1