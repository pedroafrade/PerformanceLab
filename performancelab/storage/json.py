"""
PerformanceLab

JSON Storage

Utilities for saving and loading athlete data.
"""

import json as json_module

from datetime import date, datetime, timedelta
from pathlib import Path

from performancelab import (
    Athlete,
    Event,
    EventEntry,
    Goal,
    Workout,
)

from performancelab.training.planning.planned_workout import (
    PlannedWorkout,
)


# ======================================================
# Date serialization
# ======================================================

def _serialize_date(value):

    if value is None:

        return None

    return value.isoformat()


# ======================================================

def _deserialize_date(value):

    if value is None:

        return None

    if "T" in value:

        return datetime.fromisoformat(value)

    return date.fromisoformat(value)


# ======================================================
# Duration serialization
# ======================================================

def _serialize_duration(value):

    if value is None:

        return None

    return value.total_seconds()


# ======================================================

def _deserialize_duration(value):

    if value is None:

        return None

    return timedelta(seconds=value)


# ======================================================
# Workout
# ======================================================

def _workout_to_dict(workout):

    return {

        "info": {

            "date": _serialize_date(
                workout.info.date
            ),

            "sport": workout.info.sport,

            "title": workout.info.title,

            "description": (
                workout.info.description
            ),

            "source": workout.info.source,

            "timezone": workout.info.timezone,

            "distance": workout.info.distance,

            "duration": _serialize_duration(
                workout.info.duration
            ),

            "elevation_gain": (
                workout.info.elevation_gain
            ),

        },

        "environment": {

            "temperature": (
                workout.environment.temperature
            ),

            "humidity": (
                workout.environment.humidity
            ),

            "wind_speed": (
                workout.environment.wind_speed
            ),

            "terrain": (
                workout.environment.terrain
            ),

            "weather": (
                workout.environment.weather
            ),

        },

        "feedback": {

            "rpe": workout.feedback.rpe,

            "feeling": workout.feedback.feeling,

            "sleep_quality": (
                workout.feedback.sleep_quality
            ),

            "motivation": (
                workout.feedback.motivation
            ),

            "stress": workout.feedback.stress,

            "muscle_soreness": (
                workout.feedback.muscle_soreness
            ),

            "notes": workout.feedback.notes,

        },

        "sensors": workout.sensors.sensors,

    }


# ======================================================

def _workout_from_dict(data):

    workout = Workout()

    info = data.get("info", {})

    workout.info.date = _deserialize_date(
        info.get("date")
    )

    workout.info.sport = info.get("sport")

    workout.info.title = info.get(
        "title",
        "",
    )

    workout.info.description = info.get(
        "description",
        "",
    )

    workout.info.source = info.get(
        "source",
        "",
    )

    workout.info.timezone = info.get(
        "timezone",
        "",
    )

    workout.info.distance = info.get(
        "distance"
    )

    workout.info.duration = (
        _deserialize_duration(
            info.get("duration")
        )
    )

    workout.info.elevation_gain = info.get(
        "elevation_gain"
    )

    environment = data.get(
        "environment",
        {},
    )

    workout.environment.temperature = (
        environment.get("temperature")
    )

    workout.environment.humidity = (
        environment.get("humidity")
    )

    workout.environment.wind_speed = (
        environment.get("wind_speed")
    )

    workout.environment.terrain = (
        environment.get("terrain", "")
    )

    workout.environment.weather = (
        environment.get("weather", "")
    )

    feedback = data.get("feedback", {})

    workout.feedback.rpe = feedback.get("rpe")

    workout.feedback.feeling = feedback.get(
        "feeling"
    )

    workout.feedback.sleep_quality = (
        feedback.get("sleep_quality")
    )

    workout.feedback.motivation = feedback.get(
        "motivation"
    )

    workout.feedback.stress = feedback.get(
        "stress"
    )

    workout.feedback.muscle_soreness = (
        feedback.get("muscle_soreness")
    )

    workout.feedback.notes = feedback.get(
        "notes",
        "",
    )

    for name, sensor in data.get(
        "sensors",
        {},
    ).items():

        workout.sensors.add(
            name,
            sensor,
        )

    return workout


# ======================================================
# Planned Workout
# ======================================================

def _planned_workout_to_dict(workout):

    return {

        "scheduled_at": _serialize_date(
            workout.scheduled_at
        ),

        "sport": workout.sport,

        "title": workout.title,

        "duration": _serialize_duration(
            workout.duration
        ),

        "distance": workout.distance,

        "description": workout.description,

        "intensity": workout.intensity,

        "objective": workout.objective,

        "structure": list(
            workout.structure
        ),

        "equipment": list(
            workout.equipment
        ),

    }


# ======================================================

def _planned_workout_from_dict(data):

    return PlannedWorkout(

        scheduled_at=_deserialize_date(
            data.get("scheduled_at")
        ),

        sport=data.get("sport"),

        title=data.get("title"),

        duration=_deserialize_duration(
            data.get("duration")
        ),

        distance=data.get("distance"),

        description=data.get("description"),

        intensity=data.get("intensity"),

        objective=data.get("objective"),

        structure=tuple(
            data.get(
                "structure",
                [],
            )
        ),

        equipment=tuple(
            data.get(
                "equipment",
                [],
            )
        ),

    )


# ======================================================
# Goal
# ======================================================

def _goal_to_dict(goal):

    return {

        "name": goal.name,

        "description": goal.description,

        "date": _serialize_date(goal.date),

        "priority": goal.priority,

        "completed": goal.completed,

    }


# ======================================================

def _goal_from_dict(data):

    return Goal(

        name=data.get("name", ""),

        description=data.get(
            "description",
            "",
        ),

        date=_deserialize_date(
            data.get("date")
        ),

        priority=data.get(
            "priority",
            "B",
        ),

        completed=data.get(
            "completed",
            False,
        ),

    )


# ======================================================
# Event
# ======================================================

def _event_to_dict(event):

    return {

        "name": event.name,

        "location": event.location,

        "country": event.country,

        "date": _serialize_date(event.date),

        "sport": event.sport,

        "distance": event.distance,

        "elevation_gain": (
            event.elevation_gain
        ),

        "terrain": event.terrain,

        "surface": event.surface,

        "organizer": event.organizer,

        "website": event.website,

        "gpx_file": event.gpx_file,

        "description": event.description,

    }


# ======================================================

def _event_from_dict(data):

    return Event(

        name=data.get("name", ""),

        location=data.get(
            "location",
            "",
        ),

        country=data.get(
            "country",
            "",
        ),

        date=_deserialize_date(
            data.get("date")
        ),

        sport=data.get("sport", ""),

        distance=data.get("distance"),

        elevation_gain=data.get(
            "elevation_gain"
        ),

        terrain=data.get(
            "terrain",
            "",
        ),

        surface=data.get(
            "surface",
            "",
        ),

        organizer=data.get(
            "organizer",
            "",
        ),

        website=data.get(
            "website",
            "",
        ),

        gpx_file=data.get(
            "gpx_file",
            "",
        ),

        description=data.get(
            "description",
            "",
        ),

    )


# ======================================================
# Event Entry
# ======================================================

def _event_entry_to_dict(entry):

    return {

        "event": _event_to_dict(
            entry.event
        ),

        "priority": entry.priority,

        "target_time": _serialize_duration(
            entry.target_time
        ),

        "result_time": _serialize_duration(
            entry.result_time
        ),

        "position": entry.position,

        "finished": entry.finished,

        "dnf": entry.dnf,

        "dns": entry.dns,

        "notes": entry.notes,

    }


# ======================================================

def _event_entry_from_dict(data):

    return EventEntry(

        event=_event_from_dict(
            data.get("event", {})
        ),

        priority=data.get(
            "priority",
            "B",
        ),

        target_time=_deserialize_duration(
            data.get("target_time")
        ),

        result_time=_deserialize_duration(
            data.get("result_time")
        ),

        position=data.get("position"),

        finished=data.get(
            "finished",
            False,
        ),

        dnf=data.get(
            "dnf",
            False,
        ),

        dns=data.get(
            "dns",
            False,
        ),

        notes=data.get(
            "notes",
            "",
        ),

    )


# ======================================================
# Athlete
# ======================================================

def athlete_to_dict(athlete):

    return {

        "format": "PerformanceLab",

        "version": 1,

        "athlete": {

            "name": athlete.name,

            "birth_date": _serialize_date(
                athlete.birth_date
            ),

            "gender": athlete.gender,

            "height": athlete.height,

            "weight": athlete.weight,

            "ftp": athlete.ftp,

            "max_hr": athlete.max_hr,

            "resting_hr": athlete.resting_hr,

        },

        "workouts": [

            _workout_to_dict(workout)

            for workout in athlete.history

        ],

        "goals": [

            _goal_to_dict(goal)

            for goal in athlete.goals

        ],

        "events": [

            _event_entry_to_dict(entry)

            for entry in athlete.events

        ],

        "training_plan": [

            _planned_workout_to_dict(workout)

            for workout in athlete.training_plan

        ],

    }


# ======================================================

def athlete_from_dict(data):

    if data.get("format") != "PerformanceLab":

        raise ValueError(
            "Invalid PerformanceLab file"
        )

    athlete_data = data.get(
        "athlete",
        {},
    )

    athlete = Athlete(

        name=athlete_data.get(
            "name",
            "",
        ),

        birth_date=_deserialize_date(
            athlete_data.get("birth_date")
        ),

        gender=athlete_data.get(
            "gender",
            "",
        ),

        height=athlete_data.get("height"),

        weight=athlete_data.get("weight"),

        ftp=athlete_data.get("ftp"),

        max_hr=athlete_data.get("max_hr"),

        resting_hr=athlete_data.get(
            "resting_hr"
        ),

    )

    for workout_data in data.get(
        "workouts",
        [],
    ):

        athlete.history.add(

            _workout_from_dict(
                workout_data
            )

        )

    for goal_data in data.get(
        "goals",
        [],
    ):

        athlete.goals.add(

            _goal_from_dict(
                goal_data
            )

        )

    for entry_data in data.get(
        "events",
        [],
    ):

        athlete.events.add(

            _event_entry_from_dict(
                entry_data
            )

        )

    for workout_data in data.get(
        "training_plan",
        [],
    ):

        athlete.training_plan.add(

            _planned_workout_from_dict(
                workout_data
            )

        )

    return athlete


# ======================================================
# Save Athlete
# ======================================================

def save_athlete(
    athlete,
    path,
):

    destination = Path(path)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = athlete_to_dict(athlete)

    with destination.open(
        "w",
        encoding="utf-8",
    ) as file:

        json_module.dump(

            data,

            file,

            ensure_ascii=False,

            indent=2,

        )

    return destination


# ======================================================
# Load Athlete
# ======================================================

def load_athlete(path):

    source = Path(path)

    if not source.exists():

        raise FileNotFoundError(
            f"Athlete file not found: {source}"
        )

    with source.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json_module.load(file)

    return athlete_from_dict(data)