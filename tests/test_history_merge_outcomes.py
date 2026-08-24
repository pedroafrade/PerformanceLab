"""
Tests for factual workout merge outcomes.
"""

from datetime import (
    datetime,
    timedelta,
)

from performancelab.history import (
    History,
)
from performancelab.workout import (
    Workout,
)


def workout(
    *,
    workout_id,
    title="Morning Run",
):

    result = Workout(
        workout_id=workout_id
    )

    result.info.title = title
    result.info.sport = "Running"
    result.info.date = datetime(
        2026,
        8,
        10,
        8,
        0,
    )
    result.info.duration = timedelta(
        minutes=60
    )
    result.info.distance = 10.0

    return result


def test_reports_new_workout_as_imported():

    history = History()

    result = history.merge_with_result(
        workout(
            workout_id="new"
        )
    )

    assert result.status == "imported"
    assert len(
        history
    ) == 1


def test_reports_unchanged_match_as_duplicate():

    history = History()

    history.add(
        workout(
            workout_id="existing"
        )
    )

    result = history.merge_with_result(
        workout(
            workout_id="duplicate"
        )
    )

    assert result.status == "duplicate"
    assert len(
        history
    ) == 1


def test_reports_enriched_title_as_updated():

    history = History()

    history.add(
        workout(
            workout_id="existing",
            title="10",
        )
    )

    result = history.merge_with_result(
        workout(
            workout_id="imported",
            title="Morning Run",
        )
    )

    assert result.status == "updated"

    assert (
        result.workout.info.title
        == "Morning Run"
    )


def test_reports_new_sensor_data_as_updated():

    history = History()

    existing = workout(
        workout_id="existing"
    )

    history.add(
        existing
    )

    imported = workout(
        workout_id="imported"
    )

    imported.sensors.add(
        "heart_rate",
        {
            "average": 150,
        },
    )

    result = history.merge_with_result(
        imported
    )

    assert result.status == "updated"

    assert (
        result
        .workout
        .sensors
        .get(
            "heart_rate"
        )
        == {
            "average": 150,
        }
    )