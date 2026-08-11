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
from performancelab.activity_coach_records import (
    ActivityCoachInterpretation,
    ActivityCoachInterpretationBook,
)
from performancelab.coaching.activity_coach_generation import (
    ActivityCoachNarrative,
)
from performancelab.analysis import (
    HeartRateZone,
    NutritionProfile,
)

from performancelab.training.planning.planned_workout import (
    PlannedWorkout,
)
from performancelab.training.planning.training_plan import (
    TrainingPlan,
)

from performancelab.training.planning.plan_adaptation import (
    TrainingPlanAdaptation,
)
from performancelab.training.planning.workout_outcome import (
    WorkoutOutcomeStatus,
)

from uuid import uuid4


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
# Text encoding repair
# ======================================================

def _repair_text_encoding(
    value,
):
    """
    Repairs text where UTF-8 was incorrectly interpreted
    as Latin-1, for example PÃ© instead of Pé.
    """

    if value is None:

        return None

    text = str(
        value
    )

    mojibake_markers = (
        "Ã",
        "Â",
        "â€",
        "â€“",
        "â€”",
    )

    if not any(
        marker in text
        for marker in mojibake_markers
    ):

        return text

    try:

        return (
            text
            .encode("latin-1")
            .decode("utf-8")
        )

    except (
        UnicodeEncodeError,
        UnicodeDecodeError,
    ):

        return text
    
# ======================================================
# Heart-rate zones
# ======================================================

def _heart_rate_zone_to_dict(
    zone,
):

    return {
        "name": zone.name,
        "lower_bpm": zone.lower_bpm,
        "upper_bpm": zone.upper_bpm,
    }


# ======================================================

def _heart_rate_zone_from_dict(
    data,
):

    return HeartRateZone(
        name=data.get(
            "name",
            "",
        ),
        lower_bpm=int(
            data.get("lower_bpm")
        ),
        upper_bpm=int(
            data.get("upper_bpm")
        ),
    )
# ======================================================
# Nutrition profile
# ======================================================

def _nutrition_profile_to_dict(
    profile,
):

    return {
        "carbohydrate_per_hour": (
            profile.carbohydrate_per_hour
        ),
        "fluid_lower_ml_per_hour": (
            profile.fluid_lower_ml_per_hour
        ),
        "fluid_upper_ml_per_hour": (
            profile.fluid_upper_ml_per_hour
        ),
        "sodium_lower_mg_per_hour": (
            profile.sodium_lower_mg_per_hour
        ),
        "sodium_upper_mg_per_hour": (
            profile.sodium_upper_mg_per_hour
        ),
        "gel_carbohydrate_grams": (
            profile.gel_carbohydrate_grams
        ),
        "pre_race_carbohydrate_lower": (
            profile.pre_race_carbohydrate_lower
        ),
        "pre_race_carbohydrate_upper": (
            profile.pre_race_carbohydrate_upper
        ),
        "source": profile.source,
    }


# ======================================================

def _nutrition_profile_from_dict(
    data,
):

    data = data or {}

    return NutritionProfile(
        carbohydrate_per_hour=data.get(
            "carbohydrate_per_hour",
            80,
        ),
        fluid_lower_ml_per_hour=data.get(
            "fluid_lower_ml_per_hour",
            450,
        ),
        fluid_upper_ml_per_hour=data.get(
            "fluid_upper_ml_per_hour",
            600,
        ),
        sodium_lower_mg_per_hour=data.get(
            "sodium_lower_mg_per_hour",
            400,
        ),
        sodium_upper_mg_per_hour=data.get(
            "sodium_upper_mg_per_hour",
            600,
        ),
        gel_carbohydrate_grams=data.get(
            "gel_carbohydrate_grams",
            25,
        ),
        pre_race_carbohydrate_lower=data.get(
            "pre_race_carbohydrate_lower",
            60,
        ),
        pre_race_carbohydrate_upper=data.get(
            "pre_race_carbohydrate_upper",
            80,
        ),
        source=data.get(
            "source",
            "default",
        ),
    )
# ======================================================
# Workout
# ======================================================

def _workout_to_dict(workout):

    return {

        "id": workout.workout_id,

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

            "estimated_rpe": (
                workout.feedback.estimated_rpe
            ),

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

    workout = Workout(
        workout_id=(
            data.get("id")
            or str(uuid4())
        )
    )

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

    workout.feedback.estimated_rpe = feedback.get(
        "estimated_rpe"
    )

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

        "elevation_gain": (
            workout.elevation_gain
        ),

        "description": workout.description,

        "prescription_summary": (
            workout.prescription_summary
        ),

        "intensity": workout.intensity,

        "objective": workout.objective,

        "structure": list(
            workout.structure
        ),

        "equipment": list(
            workout.equipment
        ),
        "phase": workout.phase,
    }


# ======================================================
def _planned_workout_from_dict(data):

    return PlannedWorkout(

        scheduled_at=_deserialize_date(
            data.get("scheduled_at")
        ),

        sport=_repair_text_encoding(
            data.get("sport")
        ),

        title=_repair_text_encoding(
            data.get("title")
        ),

        duration=_deserialize_duration(
            data.get("duration")
        ),

        distance=data.get("distance"),

        elevation_gain=data.get(
            "elevation_gain"
        ),

        description=_repair_text_encoding(
            data.get("description")
        ),

        prescription_summary=(
            _repair_text_encoding(
                data.get(
                    "prescription_summary"
                )
            )
        ),

        intensity=_repair_text_encoding(
            data.get("intensity")
        ),

        objective=_repair_text_encoding(
            data.get("objective")
        ),

        structure=tuple(
            _repair_text_encoding(
                item
            )
            for item in data.get(
                "structure",
                [],
            )
        ),

        equipment=tuple(
            _repair_text_encoding(
                item
            )
            for item in data.get(
                "equipment",
                [],
            )
        ),

        phase=_repair_text_encoding(
            data.get("phase")
        ),

    )

# ======================================================
# Training plan adaptation
# ======================================================

def _training_plan_adaptation_to_dict(
    adaptation,
):

    return {
        "reconciled_on": _serialize_date(
            adaptation.reconciled_on
        ),
        "workout_day": _serialize_date(
            adaptation.workout_day
        ),
        "workout_title": (
            adaptation.workout_title
        ),
        "previous_duration": (
            _serialize_duration(
                adaptation.previous_duration
            )
        ),
        "revised_duration": (
            _serialize_duration(
                adaptation.revised_duration
            )
        ),
        "trigger_status": (
            adaptation.trigger_status.value
        ),
        "load_difference": (
            adaptation.load_difference
        ),
        "previous_distance": (
            adaptation.previous_distance
        ),
        "revised_distance": (
            adaptation.revised_distance
        ),
        "previous_elevation_gain": (
            adaptation.previous_elevation_gain
        ),
        "revised_elevation_gain": (
            adaptation.revised_elevation_gain
        ),
        "previous_prescription": (
            adaptation.previous_prescription
        ),
        "revised_prescription": (
            adaptation.revised_prescription
        ),
    }

# ======================================================

def _training_plan_adaptation_from_dict(
    data,
):

    return TrainingPlanAdaptation(
        reconciled_on=_deserialize_date(
            data.get("reconciled_on")
        ),
        workout_day=_deserialize_date(
            data.get("workout_day")
        ),
        workout_title=data.get(
            "workout_title"
        ),
        previous_duration=(
            _deserialize_duration(
                data.get(
                    "previous_duration"
                )
            )
        ),
        revised_duration=(
            _deserialize_duration(
                data.get(
                    "revised_duration"
                )
            )
        ),
        trigger_status=(
            WorkoutOutcomeStatus(
                data.get(
                    "trigger_status"
                )
            )
        ),
        load_difference=data.get(
            "load_difference"
        ),
        previous_distance=data.get(
            "previous_distance"
        ),
        revised_distance=data.get(
            "revised_distance"
        ),
        previous_elevation_gain=data.get(
            "previous_elevation_gain"
        ),
        revised_elevation_gain=data.get(
            "revised_elevation_gain"
        ),
        previous_prescription=(
            _repair_text_encoding(
                data.get(
                    "previous_prescription"
                )
            )
        ),
        revised_prescription=(
            _repair_text_encoding(
                data.get(
                    "revised_prescription"
                )
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

        "id": event.event_id,

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

        event_id=data.get(
            "id",
            str(uuid4()),
        ),

        name=_repair_text_encoding(
            data.get(
                "name",
                "",
            )
        ),

        location=_repair_text_encoding(
            data.get(
                "location",
                "",
            )
        ),

        country=_repair_text_encoding(
            data.get(
                "country",
                "",
            )
        ),

        date=_deserialize_date(
            data.get("date")
        ),

        sport=_repair_text_encoding(
            data.get(
                "sport",
                "",
            )
        ),

        distance=data.get("distance"),

        elevation_gain=data.get(
            "elevation_gain"
        ),

        terrain=_repair_text_encoding(
            data.get(
                "terrain",
                "",
            )
        ),

        surface=_repair_text_encoding(
            data.get(
                "surface",
                "",
            )
        ),

        organizer=_repair_text_encoding(
            data.get(
                "organizer",
                "",
            )
        ),

        website=data.get(
            "website",
            "",
        ),

        gpx_file=data.get(
            "gpx_file",
            "",
        ),

        description=_repair_text_encoding(
            data.get(
                "description",
                "",
            )
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
# Activity Coach interpretation
# ======================================================

def _activity_coach_interpretation_to_dict(
    interpretation,
):

    narrative = (
        interpretation.narrative
    )

    return {
        "workout_id": (
            interpretation.workout_id
        ),
        "contract_version": (
            interpretation.contract_version
        ),
        "context_hash": (
            interpretation.context_hash
        ),
        "generated_at": (
            _serialize_date(
                interpretation.generated_at
            )
        ),
        "narrative": {
            "measured_facts": (
                narrative.measured_facts
            ),
            "deterministic_signals": (
                narrative.deterministic_signals
            ),
            "prudent_interpretation": (
                narrative.prudent_interpretation
            ),
            "recommendations": (
                narrative.recommendations
            ),
            "data_limitations": (
                narrative.data_limitations
            ),
            "provider": narrative.provider,
            "model": narrative.model,
        },
    }


def _activity_coach_interpretation_from_dict(
    data,
):

    narrative_data = data.get(
        "narrative",
        {},
    )

    return ActivityCoachInterpretation(
        workout_id=data.get(
            "workout_id",
            "",
        ),
        contract_version=data.get(
            "contract_version",
            "",
        ),
        context_hash=data.get(
            "context_hash",
            "",
        ),
        generated_at=(
            _deserialize_date(
                data.get(
                    "generated_at"
                )
            )
        ),
        narrative=ActivityCoachNarrative(
            measured_facts=(
                narrative_data.get(
                    "measured_facts",
                    "",
                )
            ),
            deterministic_signals=(
                narrative_data.get(
                    "deterministic_signals",
                    "",
                )
            ),
            prudent_interpretation=(
                narrative_data.get(
                    "prudent_interpretation",
                    "",
                )
            ),
            recommendations=(
                narrative_data.get(
                    "recommendations",
                    "",
                )
            ),
            data_limitations=(
                narrative_data.get(
                    "data_limitations",
                    "",
                )
            ),
            provider=narrative_data.get(
                "provider",
                "",
            ),
            model=narrative_data.get(
                "model",
                "",
            ),
        ),
    )
# ======================================================
# Athlete
# ======================================================

def athlete_to_dict(athlete):

    return {

        "format": "PerformanceLab",

        "version": 10,

        "athlete": {

            "id": athlete.athlete_id,

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

            "threshold_hr": (
                athlete.threshold_hr
            ),

            "heart_rate_zones": [

                _heart_rate_zone_to_dict(
                    zone
                )

                for zone in (
                    athlete
                    .manual_heart_rate_zones
                )

            ],

            "nutrition_profile": (
                _nutrition_profile_to_dict(
                    athlete.nutrition_profile
                )
            ),

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
        "activity_coach_interpretations": [

            _activity_coach_interpretation_to_dict(
                interpretation
            )

            for interpretation in (
                athlete
                .activity_coach_interpretations
            )

        ],

        "training_plan": {

            "id": athlete.training_plan.plan_id,

            "start_date": _serialize_date(
                athlete.training_plan.start_date
            ),

            "end_date": _serialize_date(
                athlete.training_plan.end_date
            ),

            "reconciled_through": _serialize_date(
                athlete.training_plan.reconciled_through
            ),

            "reconciled_workout_ids": list(
                athlete.training_plan.reconciled_workout_ids
            ),

            "reconciled_workout_signatures": [
                {
                    "workout_id": workout_id,
                    "signature": list(
                        signature
                    ),
                }
                for workout_id, signature
                in (
                    athlete.training_plan
                    .reconciled_workout_signatures
                )
            ],
            
            "adaptations": [
                _training_plan_adaptation_to_dict(
                    adaptation
                )
                for adaptation in (
                    athlete.training_plan
                    .adaptations
                )
            ],

            "primary_event_id": (
                athlete.training_plan.primary_event_id
            ),

            "competition_event_ids": list(
                athlete.training_plan.competition_event_ids
            ),

            "workouts": [

                _planned_workout_to_dict(workout)

                for workout in athlete.training_plan

            ],

        },

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

        athlete_id=athlete_data.get(
            "id",
            str(uuid4()),
        ),

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

        threshold_hr=athlete_data.get(
            "threshold_hr"
        ),

        manual_heart_rate_zones=tuple(

            _heart_rate_zone_from_dict(
                zone_data
            )

            for zone_data in athlete_data.get(
                "heart_rate_zones",
                [],
            )

        ),

        nutrition_profile=(
            _nutrition_profile_from_dict(
                athlete_data.get(
                    "nutrition_profile"
                )
            )
        ),

    )

    athlete.activity_coach_interpretations = (
        ActivityCoachInterpretationBook(
            records=tuple(
                _activity_coach_interpretation_from_dict(
                    interpretation_data
                )
                for interpretation_data in data.get(
                    "activity_coach_interpretations",
                    [],
                )
            )
        )
    )
    
    training_plan_data = data.get(
        "training_plan",
        [],
    )

    if isinstance(
        training_plan_data,
        list,
    ):

        plan_workouts = (
            training_plan_data
        )

        athlete.training_plan = (
            TrainingPlan()
        )

    elif isinstance(
        training_plan_data,
        dict,
    ):

        plan_workouts = (
            training_plan_data.get(
                "workouts",
                [],
            )
        )

        athlete.training_plan = TrainingPlan(

            plan_id=training_plan_data.get(
                "id",
                str(uuid4()),
            ),

            start_date=_deserialize_date(
                training_plan_data.get(
                    "start_date"
                )
            ),

            end_date=_deserialize_date(
                training_plan_data.get(
                    "end_date"
                )
            ),

            reconciled_through=_deserialize_date(
                training_plan_data.get(
                    "reconciled_through"
                )
            ),

            reconciled_workout_ids=tuple(
                training_plan_data.get(
                    "reconciled_workout_ids",
                    [],
                )
            ),

            reconciled_workout_signatures=tuple(
                (
                    record.get(
                        "workout_id",
                        "",
                    ),
                    tuple(
                        record.get(
                            "signature",
                            [],
                        )
                    ),
                )
                for record in (
                    training_plan_data.get(
                        "reconciled_workout_signatures",
                        [],
                    )
                )
            ),

            adaptations=tuple(
                _training_plan_adaptation_from_dict(
                    adaptation_data
                )
                for adaptation_data in (
                    training_plan_data.get(
                        "adaptations",
                        [],
                    )
                )
            ),

            primary_event_id=(
                training_plan_data.get(
                    "primary_event_id"
                )
            ),

            competition_event_ids=tuple(
                training_plan_data.get(
                    "competition_event_ids",
                    [],
                )
            ),

        )

    else:

        raise ValueError(
            "Invalid training_plan data"
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

    for workout_data in plan_workouts:

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

    temporary = destination.with_name(
        f".{destination.name}."
        f"{uuid4().hex}.tmp"
    )

    data = athlete_to_dict(athlete)

    try:

        with temporary.open(
            "w",
            encoding="utf-8",
        ) as file:

            json_module.dump(

                data,

                file,

                ensure_ascii=False,

                separators=(",", ":"),

            )

        temporary.replace(
            destination
        )

    finally:

        if temporary.exists():

            temporary.unlink()

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