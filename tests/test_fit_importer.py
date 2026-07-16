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
            },
        ],
        "sessions": [
            {
                "sport": "running",
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
                "total_ascent": 15.0,
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

    assert workout.date.isoformat() == (
        "2026-07-01"
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