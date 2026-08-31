"""
Tests for workout detail formatting.
"""

from types import (
    SimpleNamespace,
)

from app.components.workout_details import (
    format_elevation_source,
)


def workout_with_source(
    source: str,
):

    return SimpleNamespace(
        info=SimpleNamespace(
            source=source,
        ),
    )


def test_formats_fit_elevation_source():

    workout = workout_with_source(
        "fit"
    )

    assert (
        format_elevation_source(
            workout
        )
        == "Elevation source: FIT"
    )


def test_formats_gpx_elevation_source():

    workout = workout_with_source(
        "gpx"
    )

    assert (
        format_elevation_source(
            workout
        )
        == "Elevation source: GPX"
    )


def test_omits_missing_elevation_source():

    workout = workout_with_source(
        ""
    )

    assert (
        format_elevation_source(
            workout
        )
        == ""
    )