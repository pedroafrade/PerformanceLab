"""
PerformanceLab

Tests for JSON storage.
"""

import json

from datetime import date, datetime, timedelta

import pytest

from performancelab import (
    Athlete,
    Event,
    EventEntry,
    Goal,
    Workout,
)

from performancelab.storage import (
    athlete_from_dict,
    athlete_to_dict,
    load_athlete,
    save_athlete,
)


# ======================================================
# Helpers
# ======================================================

def create_athlete():

    athlete = Athlete(

        name="Pedro",

        birth_date=date(1990, 5, 10),

        gender="Male",

        height=178,

        weight=70,

        ftp=280,

        max_hr=190,

        resting_hr=50,

    )

    workout = Workout()

    workout.info.date = datetime(
        2026,
        7,
        1,
        8,
        30,
    )

    workout.info.sport = "Running"
    workout.info.title = "Morning Run"
    workout.info.description = "Easy session"
    workout.info.source = "manual"
    workout.info.timezone = "Europe/Lisbon"
    workout.info.distance = 10
    workout.info.duration = timedelta(
        minutes=50
    )
    workout.info.elevation_gain = 200

    workout.environment.temperature = 20
    workout.environment.humidity = 60
    workout.environment.wind_speed = 8
    workout.environment.terrain = "Road"
    workout.environment.weather = "Sunny"

    workout.feedback.rpe = 6
    workout.feedback.feeling = 8
    workout.feedback.sleep_quality = 7
    workout.feedback.motivation = 9
    workout.feedback.stress = 3
    workout.feedback.muscle_soreness = 2
    workout.feedback.notes = "Felt good"

    workout.sensors.add(
        "heart_rate",
        {
            "average": 150,
            "maximum": 175,
        },
    )

    athlete.history.add(workout)

    athlete.goals.add(

        Goal(

            name="Run a marathon",

            description="Finish comfortably",

            date=date(2026, 10, 1),

            priority="A",

        )

    )

    event = Event(

        name="Lisbon Marathon",

        location="Lisbon",

        country="Portugal",

        date=date(2026, 10, 18),

        sport="Running",

        distance=42.195,

        elevation_gain=350,

        terrain="Urban",

        surface="Road",

    )

    athlete.events.add(

        EventEntry(

            event=event,

            priority="A",

            target_time=timedelta(
                hours=3,
                minutes=30,
            ),

            notes="Primary race",

        )

    )

    return athlete


# ======================================================

def test_athlete_to_dict():

    athlete = create_athlete()

    data = athlete_to_dict(athlete)

    assert data["format"] == "PerformanceLab"

    assert data["version"] == 1

    assert data["athlete"]["name"] == "Pedro"

    assert len(data["workouts"]) == 1

    assert len(data["goals"]) == 1

    assert len(data["events"]) == 1


# ======================================================

def test_athlete_round_trip():

    original = create_athlete()

    data = athlete_to_dict(original)

    loaded = athlete_from_dict(data)

    assert loaded.name == original.name

    assert loaded.birth_date == (
        original.birth_date
    )

    assert loaded.weight == original.weight

    assert loaded.ftp == original.ftp

    assert len(loaded.history) == 1

    assert len(loaded.goals) == 1

    assert len(loaded.events) == 1

    workout = loaded.history[0]

    assert workout.date == datetime(
        2026,
        7,
        1,
        8,
        30,
    )

    assert workout.sport == "Running"

    assert workout.distance == 10

    assert workout.duration == timedelta(
        minutes=50
    )

    assert workout.elevation_gain == 200

    assert workout.feedback.rpe == 6

    assert workout.environment.terrain == (
        "Road"
    )

    assert workout.sensors.get(
        "heart_rate"
    ) == {

        "average": 150,

        "maximum": 175,

    }

    assert loaded.goals[0].name == (
        "Run a marathon"
    )

    assert loaded.events[0].event.name == (
        "Lisbon Marathon"
    )

    assert loaded.events[0].target_time == (
        timedelta(
            hours=3,
            minutes=30,
        )
    )


# ======================================================

def test_save_and_load_athlete(tmp_path):

    athlete = create_athlete()

    path = tmp_path / "pedro.plab.json"

    result = save_athlete(
        athlete,
        path,
    )

    assert result == path

    assert path.exists()

    loaded = load_athlete(path)

    assert loaded.name == "Pedro"

    assert len(loaded.history) == 1

    assert len(loaded.goals) == 1

    assert len(loaded.events) == 1


# ======================================================

def test_saved_file_is_valid_json(tmp_path):

    athlete = create_athlete()

    path = tmp_path / "athlete.json"

    save_athlete(
        athlete,
        path,
    )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    assert data["athlete"]["name"] == (
        "Pedro"
    )


# ======================================================

def test_save_creates_parent_directories(
    tmp_path,
):

    athlete = create_athlete()

    path = (

        tmp_path

        / "athletes"

        / "pedro"

        / "profile.json"

    )

    save_athlete(
        athlete,
        path,
    )

    assert path.exists()


# ======================================================

def test_load_missing_file(tmp_path):

    path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):

        load_athlete(path)


# ======================================================

def test_invalid_file_format():

    with pytest.raises(ValueError):

        athlete_from_dict(

            {
                "format": "OtherApplication",
            }

        )