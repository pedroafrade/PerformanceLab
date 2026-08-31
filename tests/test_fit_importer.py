"""
PerformanceLab

Tests for FIT Importer.
"""

from datetime import datetime, timedelta, timezone

import pytest

from performancelab.importers import (
    FITImporter,
    InvalidActivityError,
)


# ======================================================
# Helpers
# ======================================================

def sample_messages():

    return {
        "records": [
            {
                "timestamp": datetime(
                    2026,
                    7,
                    1,
                    8,
                    0,
                    tzinfo=timezone.utc,
                ),
                "position_lat": 461000000,
                "position_long": -109000000,
                "enhanced_altitude": 20.0,
                "distance": 0.0,
                "heart_rate": 140,
                "cadence": 82,
                "power": 210,
                "temperature": 18.0,
                "humidity": 62.0,
            },
            {
                "timestamp": datetime(
                    2026,
                    7,
                    1,
                    8,
                    10,
                    tzinfo=timezone.utc,
                ),
                "position_lat": 461100000,
                "position_long": -108900000,
                "enhanced_altitude": 35.0,
                "distance": 5000.0,
                "heart_rate": 155,
                "cadence": 86,
                "power": 240,
                "temperature": 20.0,
                "humidity": 58.0,
            },
        ],
        "sessions": [
            {
                "sport": "running",
                "sub_sport": "trail",
                "start_time": datetime(
                    2026,
                    7,
                    1,
                    8,
                    0,
                    tzinfo=timezone.utc,
                ),
                "total_distance": 5000.0,
                "total_elapsed_time": 600.0,
                "total_calories": 420,
            }
        ],
        "activities": [],
    }


# ======================================================

def test_fit_workout_creation(monkeypatch):

    importer = FITImporter()

    monkeypatch.setattr(
        importer,
        "_read_source",
        lambda source: b"fake-fit",
    )

    monkeypatch.setattr(
        importer,
        "_read_messages",
        lambda content: sample_messages(),
    )

    workout = importer.read(b"ignored")

    assert workout.info.source == "fit"

    assert workout.sport == "Running"

    assert (
        workout.info.sub_sport
        == "trail"
    )

    assert workout.date == datetime(
        2026,
        7,
        1,
        8,
        0,
        tzinfo=timezone.utc,
    )

    assert workout.distance == 5.0

    assert workout.duration == timedelta(
        minutes=10
    )

    assert workout.elevation_gain == 15.0


# ======================================================

def test_fit_route(monkeypatch):

    importer = FITImporter()

    monkeypatch.setattr(
        importer,
        "_read_source",
        lambda source: b"fake-fit",
    )

    monkeypatch.setattr(
        importer,
        "_read_messages",
        lambda content: sample_messages(),
    )

    workout = importer.read(b"ignored")

    route = workout.sensors.get("gps")

    assert route is not None

    assert len(route) == 2

    assert route[0]["latitude"] is not None

    assert route[0]["longitude"] is not None


# ======================================================

def test_fit_sensor_series(monkeypatch):

    importer = FITImporter()

    monkeypatch.setattr(
        importer,
        "_read_source",
        lambda source: b"fake-fit",
    )

    monkeypatch.setattr(
        importer,
        "_read_messages",
        lambda content: sample_messages(),
    )

    workout = importer.read(b"ignored")

    assert len(
        workout.sensors.get(
            "heart_rate"
        )
    ) == 2

    assert len(
        workout.sensors.get("power")
    ) == 2

    assert len(
        workout.sensors.get("cadence")
    ) == 2

    cadence = workout.sensors.get(
        "cadence"
    )

    assert cadence[0]["value"] == 164
    assert cadence[1]["value"] == 172

    assert workout.sensors.get(
        "active_calories"
    ) == [
        {
            "value": 420.0,
        },
    ]
def test_fit_imports_environment(
    monkeypatch,
):

    importer = FITImporter()

    monkeypatch.setattr(
        importer,
        "_read_source",
        lambda source: b"fake-fit",
    )

    monkeypatch.setattr(
        importer,
        "_read_messages",
        lambda content: sample_messages(),
    )

    workout = importer.read(
        b"ignored"
    )

    assert (
        workout.environment.temperature
        == 19.0
    )

    assert (
        workout.environment.humidity
        == 60.0
    )
    assert (
        workout.environment.terrain
        == ""
    )

    assert (
        workout.info.sub_sport
        == "trail"
    )

def test_fit_prefers_session_environment(
    monkeypatch,
):

    importer = FITImporter()

    messages = sample_messages()

    messages["sessions"][0][
        "avg_temperature"
    ] = 21.0

    messages["sessions"][0][
        "avg_humidity"
    ] = 55.0

    monkeypatch.setattr(
        importer,
        "_read_source",
        lambda source: b"fake-fit",
    )

    monkeypatch.setattr(
        importer,
        "_read_messages",
        lambda content: messages,
    )

    workout = importer.read(
        b"ignored"
    )

    assert (
        workout.environment.temperature
        == 21.0
    )

    assert (
        workout.environment.humidity
        == 55.0
    )
# ======================================================

def test_fit_without_activity(monkeypatch):

    importer = FITImporter()

    monkeypatch.setattr(
        importer,
        "_read_source",
        lambda source: b"fake-fit",
    )

    monkeypatch.setattr(
        importer,
        "_read_messages",
        lambda content: {
            "records": [],
            "sessions": [],
            "activities": [],
        },
    )

    with pytest.raises(
        InvalidActivityError
    ):

        importer.read(b"ignored")


# ======================================================

def test_fit_default_sport(monkeypatch):

    importer = FITImporter(
        default_sport="Cycling"
    )

    messages = sample_messages()

    messages["sessions"][0].pop("sport")

    monkeypatch.setattr(
        importer,
        "_read_source",
        lambda source: b"fake-fit",
    )

    monkeypatch.setattr(
        importer,
        "_read_messages",
        lambda content: messages,
    )

    workout = importer.read(b"ignored")

    assert workout.sport == "Cycling"

def test_fit_derives_running_cadence_from_total_strides(
    monkeypatch,
):

    importer = FITImporter()

    messages = sample_messages()

    for record in messages["records"]:
        record.pop(
            "cadence",
            None,
        )

    messages["sessions"][0][
        "total_strides"
    ] = 810

    messages["sessions"][0][
        "total_timer_time"
    ] = 600

    monkeypatch.setattr(
        importer,
        "_read_source",
        lambda source: b"fake-fit",
    )

    monkeypatch.setattr(
        importer,
        "_read_messages",
        lambda content: messages,
    )

    workout = importer.read(
        b"ignored"
    )

    cadence = workout.sensors.get(
        "cadence"
    )

    assert cadence is not None
    assert len(cadence) == 1
    assert cadence[0]["value"] == 162

def test_fit_imports_street_running_sub_sport(
    monkeypatch,
):

    importer = FITImporter()

    messages = sample_messages()

    messages["sessions"][0][
        "sub_sport"
    ] = "street"

    monkeypatch.setattr(
        importer,
        "_read_source",
        lambda source: b"fake-fit",
    )

    monkeypatch.setattr(
        importer,
        "_read_messages",
        lambda content: messages,
    )

    workout = importer.read(
        b"ignored"
    )

    assert workout.sport == "Running"

    assert (
        workout.info.sub_sport
        == "street"
    )

    assert (
        workout.environment.terrain
        == ""
    )

def test_fit_without_sub_sport_keeps_it_empty(
    monkeypatch,
):

    importer = FITImporter()

    messages = sample_messages()

    messages["sessions"][0].pop(
        "sub_sport"
    )

    monkeypatch.setattr(
        importer,
        "_read_source",
        lambda source: b"fake-fit",
    )

    monkeypatch.setattr(
        importer,
        "_read_messages",
        lambda content: messages,
    )

    workout = importer.read(
        b"ignored"
    )

    assert (
        workout.info.sub_sport
        == ""
    )

    assert (
        workout.environment.terrain
        == ""
    )

def test_fit_normalizes_sub_sport_name(
    monkeypatch,
):

    importer = FITImporter()

    messages = sample_messages()

    messages["sessions"][0][
        "sub_sport"
    ] = "Indoor Running"

    monkeypatch.setattr(
        importer,
        "_read_source",
        lambda source: b"fake-fit",
    )

    monkeypatch.setattr(
        importer,
        "_read_messages",
        lambda content: messages,
    )

    workout = importer.read(
        b"ignored"
    )

    assert (
        workout.info.sub_sport
        == "indoor_running"
    )

def test_fit_filters_record_elevation_noise():

    elevations = (
        100.0,
        102.0,
        100.0,
        102.0,
        100.0,
        102.0,
        100.0,
    )

    records = [
        {
            "enhanced_altitude": value,
        }
        for value in elevations
    ]

    result = FITImporter._elevation_gain(
        records,
        {},
    )

    raw_gain = sum(
        max(
            0.0,
            current - previous,
        )
        for previous, current
        in zip(
            elevations,
            elevations[1:],
        )
    )

    assert result == pytest.approx(
        1.7333333333
    )
    assert result < raw_gain


def test_fit_prefers_session_total_ascent():

    result = FITImporter._elevation_gain(
        [
            {
                "enhanced_altitude": 100.0,
            },
            {
                "enhanced_altitude": 900.0,
            },
        ],
        {
            "total_ascent": 319.0,
        },
    )

    assert result == 319.0

def test_fit_prefers_active_timer_duration():

    result = FITImporter._duration(
        [],
        {
            "total_timer_time": 540.0,
            "total_elapsed_time": 600.0,
        },
    )

    assert result == timedelta(
        minutes=9
    )


def test_fit_uses_elapsed_duration_without_timer():

    result = FITImporter._duration(
        [],
        {
            "total_elapsed_time": 600.0,
        },
    )

    assert result == timedelta(
        minutes=10
    )

