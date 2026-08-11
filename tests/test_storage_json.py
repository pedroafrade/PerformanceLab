"""
PerformanceLab

Tests for JSON storage.
"""

import json

from datetime import date, datetime, timedelta

import pytest

from performancelab import (
    Athlete,
    ActivityCoachInterpretation,
    ActivityCoachInterpretationBook,
    Event,
    EventEntry,
    Goal,
    Workout,
)
from performancelab.coaching import (
    ActivityCoachNarrative,
)
from performancelab.analysis import (
    HeartRateZone,
    NutritionProfile,
)

from performancelab.storage import (
    athlete_from_dict,
    athlete_to_dict,
    load_athlete,
    save_athlete,
)

import performancelab.storage.json as json_storage

from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
    TrainingPlanAdaptation,
    WorkoutOutcomeStatus,
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

        threshold_hr=180,

        manual_heart_rate_zones=(

            HeartRateZone(
                name="Z1",
                lower_bpm=120,
                upper_bpm=139,
            ),

            HeartRateZone(
                name="Z2",
                lower_bpm=140,
                upper_bpm=154,
            ),

            HeartRateZone(
                name="Z3",
                lower_bpm=155,
                upper_bpm=169,
            ),

            HeartRateZone(
                name="Z4",
                lower_bpm=170,
                upper_bpm=184,
            ),

            HeartRateZone(
                name="Z5",
                lower_bpm=185,
                upper_bpm=190,
            ),

        ),

        nutrition_profile=NutritionProfile(
            carbohydrate_per_hour=75,
            fluid_lower_ml_per_hour=500,
            fluid_upper_ml_per_hour=650,
            sodium_lower_mg_per_hour=450,
            sodium_upper_mg_per_hour=650,
            gel_carbohydrate_grams=25,
            pre_race_carbohydrate_lower=70,
            pre_race_carbohydrate_upper=90,
            source="athlete-tested",
        ),

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
    workout.feedback.estimated_rpe = 5.4
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

    assert data["version"] == 10

    assert "id" in data["athlete"]

    assert isinstance(data["athlete"]["id"], str)

    assert data["athlete"]["name"] == "Pedro"

    assert len(data["workouts"]) == 1

    assert (
        data["workouts"][0]["id"]
        == athlete.history[0].workout_id
    )

    assert len(data["goals"]) == 1

    assert len(data["events"]) == 1

    assert (
        data["events"][0]["event"]["id"]
        == athlete.events[0].event.event_id
    )

# ======================================================

def test_workout_without_id_receives_id():

    data = athlete_to_dict(
        create_athlete()
    )

    data["workouts"][0].pop("id")

    loaded = athlete_from_dict(data)

    workout_id = (
        loaded.history[0].workout_id
    )

    assert isinstance(
        workout_id,
        str,
    )

    assert workout_id

# ======================================================

def test_athlete_round_trip():

    original = create_athlete()

    data = athlete_to_dict(original)

    loaded = athlete_from_dict(data)

    assert loaded.athlete_id == original.athlete_id

    assert loaded.name == original.name

    assert loaded.birth_date == (
        original.birth_date
    )

    assert loaded.weight == original.weight

    assert loaded.ftp == original.ftp

    assert loaded.threshold_hr == 180

    assert (
        loaded.manual_heart_rate_zones
        == original.manual_heart_rate_zones
    )

    assert (
        loaded.manual_heart_rate_zones[3].name
        == "Z4"
    )

    assert (
        loaded.manual_heart_rate_zones[3].lower_bpm
        == 170
    )

    assert (
        loaded.manual_heart_rate_zones[3].upper_bpm
        == 184
    )

    assert (
        loaded.nutrition_profile
        == original.nutrition_profile
    )

    assert (
        loaded.nutrition_profile
        .carbohydrate_per_hour
        == 75
    )

    assert (
        loaded.nutrition_profile
        .fluid_lower_ml_per_hour
        == 500
    )

    assert (
        loaded.nutrition_profile
        .source
        == "athlete-tested"
    )

    assert len(loaded.history) == 1

    assert len(loaded.goals) == 1

    assert len(loaded.events) == 1

    workout = loaded.history[0]

    assert (
        workout.workout_id
        == original.history[0].workout_id
    )

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

    assert workout.feedback.estimated_rpe == 5.4

    assert workout.feedback.effective_rpe == 6

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

    assert (
        loaded.events[0].event.event_id
        == original.events[0].event.event_id
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

    assert loaded.athlete_id == athlete.athlete_id
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

def test_saved_file_uses_compact_json(
    tmp_path,
):

    athlete = create_athlete()

    path = tmp_path / "athlete.json"

    save_athlete(
        athlete,
        path,
    )

    content = path.read_text(
        encoding="utf-8"
    )

    assert "\n" not in content

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

# ======================================================

def test_load_old_json_without_id():

    athlete = create_athlete()

    data = athlete_to_dict(athlete)

    del data["athlete"]["id"]

    loaded = athlete_from_dict(data)

    assert loaded.athlete_id is not None
    assert isinstance(loaded.athlete_id, str)

# ======================================================

def test_load_old_event_without_id():

    athlete = create_athlete()

    data = athlete_to_dict(
        athlete
    )

    del data["events"][0]["event"]["id"]

    loaded = athlete_from_dict(
        data
    )

    event_id = (
        loaded.events[0].event.event_id
    )

    assert isinstance(
        event_id,
        str,
    )

    assert event_id

# ======================================================

def test_load_old_json_without_estimated_rpe():

    athlete = create_athlete()

    data = athlete_to_dict(
        athlete
    )

    del data["workouts"][0]["feedback"][
        "estimated_rpe"
    ]

    loaded = athlete_from_dict(
        data
    )

    workout = loaded.history[0]

    assert workout.feedback.rpe == 6
    assert workout.feedback.estimated_rpe is None
    assert workout.feedback.effective_rpe == 6
# ======================================================

def test_load_old_json_without_nutrition_profile():

    athlete = create_athlete()

    data = athlete_to_dict(
        athlete
    )

    del data["athlete"][
        "nutrition_profile"
    ]

    loaded = athlete_from_dict(
        data
    )

    assert loaded.nutrition_profile == (
        NutritionProfile()
    )

# ======================================================

def test_failed_save_preserves_existing_file(
    tmp_path,
    monkeypatch,
):

    athlete = create_athlete()

    path = tmp_path / "athlete.json"

    path.write_text(
        "original content",
        encoding="utf-8",
    )

    def fail_dump(
        *args,
        **kwargs,
    ):

        raise RuntimeError(
            "Simulated write failure"
        )

    monkeypatch.setattr(
        json_storage.json_module,
        "dump",
        fail_dump,
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated write failure",
    ):

        save_athlete(
            athlete,
            path,
        )

    assert path.read_text(
        encoding="utf-8"
    ) == "original content"

    assert list(
        tmp_path.glob("*.tmp")
    ) == []

def test_training_plan_metadata_round_trip():

    athlete = create_athlete()

    athlete.training_plan = TrainingPlan(
        plan_id="plan-sealand-trail",
        start_date=date(2026, 7, 29),
        end_date=date(2026, 9, 27),
        primary_event_id="trail-pe-firme",
        competition_event_ids=(
            "sealand",
            "trail-pe-firme",
        ),
    )

    athlete.training_plan.add(
        PlannedWorkout(
            scheduled_at=datetime(
                2026,
                8,
                2,
            ),
            sport="Trail Running",
            title="Long Aerobic Run",
            duration=timedelta(
                hours=2,
            ),
            elevation_gain=450,
            prescription_summary=(
                "18 km · 450 D+"
            ),
            phase="Build",
        )
    )

    data = athlete_to_dict(
        athlete
    )

    assert data["training_plan"][
        "id"
    ] == "plan-sealand-trail"

    assert data["training_plan"][
        "start_date"
    ] == "2026-07-29"

    assert data["training_plan"][
        "end_date"
    ] == "2026-09-27"

    assert data["training_plan"][
        "primary_event_id"
    ] == "trail-pe-firme"

    assert data["training_plan"][
        "competition_event_ids"
    ] == [
        "sealand",
        "trail-pe-firme",
    ]

    assert len(
        data["training_plan"]["workouts"]
    ) == 1

    assert (
        data["training_plan"]["workouts"][0][
            "phase"
        ]
        == "Build"
    )
    assert (
        data["training_plan"]["workouts"][0][
            "elevation_gain"
        ]
        == 450
    )

    loaded = athlete_from_dict(
        data
    )

    assert (
        loaded.training_plan.plan_id
        == "plan-sealand-trail"
    )

    assert (
        loaded.training_plan.start_date
        == date(2026, 7, 29)
    )

    assert (
        loaded.training_plan.end_date
        == date(2026, 9, 27)
    )

    assert (
        loaded.training_plan.primary_event_id
        == "trail-pe-firme"
    )

    assert (
        loaded.training_plan.competition_event_ids
        == (
            "sealand",
            "trail-pe-firme",
        )
    )

    assert len(
        loaded.training_plan
    ) == 1

    assert (
        loaded.training_plan[0].title
        == "Long Aerobic Run"
    )

    assert (
        loaded.training_plan[0].phase
        == "Build"
    )

    assert (
        loaded.training_plan[0].elevation_gain
        == 450
    )

    assert (
        loaded.training_plan[0]
        .prescription_summary
        == "18 km · 450 D+"
    )


def test_loads_legacy_training_plan_list():

    athlete = create_athlete()

    athlete.training_plan.add(
        PlannedWorkout(
            scheduled_at=datetime(
                2026,
                8,
                2,
            ),
            sport="Running",
            title="Legacy Long Run",
        )
    )

    data = athlete_to_dict(
        athlete
    )

    legacy_workouts = data[
        "training_plan"
    ]["workouts"]

    data["version"] = 1
    data["training_plan"] = (
        legacy_workouts
    )

    loaded = athlete_from_dict(
        data
    )

    assert (
        loaded.training_plan.start_date
        is None
    )

    assert (
        loaded.training_plan.end_date
        is None
    )

    assert len(
        loaded.training_plan
    ) == 1

    assert (
        loaded.training_plan[0].title
        == "Legacy Long Run"
    )
    assert (
        loaded.training_plan[0].elevation_gain
        is None
    )
    
def test_loads_planned_workout_without_phase():

    athlete = create_athlete()

    athlete.training_plan.add(
        PlannedWorkout(
            scheduled_at=datetime(
                2026,
                8,
                2,
            ),
            sport="Running",
            title="Legacy Run",
        )
    )

    data = athlete_to_dict(
        athlete
    )

    del data["training_plan"]["workouts"][0][
        "phase"
    ]

    loaded = athlete_from_dict(
        data
    )

    assert (
        loaded.training_plan[0].phase
        is None
    )
    assert (
        loaded.training_plan[0]
        .prescription_summary
        is None
    )
# ======================================================

def test_load_old_json_without_heart_rate_profile():

    athlete = create_athlete()

    data = athlete_to_dict(
        athlete
    )

    del data["athlete"]["threshold_hr"]
    del data["athlete"]["heart_rate_zones"]

    loaded = athlete_from_dict(
        data
    )

    assert loaded.threshold_hr is None

    assert (
        loaded.manual_heart_rate_zones
        == ()
    )
def test_training_plan_reconciliation_date_round_trip():

    athlete = create_athlete()

    athlete.training_plan = TrainingPlan(
        reconciled_through=date(
            2026,
            8,
            5,
        ),
        reconciled_workout_ids=(
            "workout-a",
            "workout-b",
        ),
        reconciled_workout_signatures=(
            (
                "workout-a",
                (
                    "2026-08-04",
                    "running",
                    3600.0,
                    6.0,
                ),
            ),
            (
                "workout-b",
                (
                    "2026-08-05",
                    "cycling",
                    5400.0,
                    5.0,
                ),
            ),
        ),
    )

    data = athlete_to_dict(
        athlete
    )

    assert (
        data["version"]
        == 10
    )

    assert (
        data["training_plan"][
            "reconciled_through"
        ]
        == "2026-08-05"
    )

    assert (
        data["training_plan"][
            "reconciled_workout_ids"
        ]
        == [
            "workout-a",
            "workout-b",
        ]
    )
    assert (
        data["training_plan"][
            "reconciled_workout_signatures"
        ]
        == [
            {
                "workout_id": "workout-a",
                "signature": [
                    "2026-08-04",
                    "running",
                    3600.0,
                    6.0,
                ],
            },
            {
                "workout_id": "workout-b",
                "signature": [
                    "2026-08-05",
                    "cycling",
                    5400.0,
                    5.0,
                ],
            },
        ]
    )
    loaded = athlete_from_dict(
        data
    )

    assert (
        loaded.training_plan.reconciled_through
        == date(
            2026,
            8,
            5,
        )
    )

    assert (
        loaded.training_plan.reconciled_workout_ids
        == (
            "workout-a",
            "workout-b",
        )
    )
    assert (
        loaded.training_plan
        .reconciled_workout_signatures
        == (
            (
                "workout-a",
                (
                    "2026-08-04",
                    "running",
                    3600.0,
                    6.0,
                ),
            ),
            (
                "workout-b",
                (
                    "2026-08-05",
                    "cycling",
                    5400.0,
                    5.0,
                ),
            ),
        )
    )

def test_loads_plan_without_reconciliation_date():

    athlete = create_athlete()

    data = athlete_to_dict(
        athlete
    )

    del data["training_plan"][
        "reconciled_workout_signatures"
    ]

    loaded = athlete_from_dict(
        data
    )

    assert (
        loaded.training_plan.reconciled_through
        is None
    )
    assert (
        loaded.training_plan.reconciled_workout_ids
        == ()
    )
    assert (
        loaded.training_plan
        .reconciled_workout_signatures
        == ()
    )

def test_training_plan_adaptation_round_trip():

    adaptation = TrainingPlanAdaptation(
        reconciled_on=date(
            2026,
            8,
            2,
        ),
        workout_day=date(
            2026,
            8,
            4,
        ),
        workout_title="LT2 Run",
        previous_duration=timedelta(
            minutes=50,
        ),
        revised_duration=timedelta(
            minutes=38,
        ),
        trigger_status=(
            WorkoutOutcomeStatus.SUBSTITUTE
        ),
        load_difference=744.0,
    )

    athlete = create_athlete()
    athlete.training_plan = TrainingPlan(
        adaptations=(
            adaptation,
        ),
    )

    data = athlete_to_dict(
        athlete
    )

    assert data["version"] == 10

    assert data["training_plan"][
        "adaptations"
    ] == [
        {
            "reconciled_on": "2026-08-02",
            "workout_day": "2026-08-04",
            "workout_title": "LT2 Run",
            "previous_duration": 3000.0,
            "revised_duration": 2280.0,
            "trigger_status": "substitute",
            "load_difference": 744.0,
            "previous_distance": None,
            "revised_distance": None,
            "previous_elevation_gain": None,
            "revised_elevation_gain": None,
            "previous_prescription": None,
            "revised_prescription": None,
        }
    ]

    loaded = athlete_from_dict(
        data
    )

    assert (
        loaded.training_plan.adaptations
        == (
            adaptation,
        )
    )


def test_loads_plan_without_adaptation_history():

    data = athlete_to_dict(
        create_athlete()
    )

    data["training_plan"].pop(
        "adaptations"
    )

    loaded = athlete_from_dict(
        data
    )

    assert (
        loaded.training_plan.adaptations
        == ()
    )



def test_activity_coach_interpretation_round_trip():

    athlete = create_athlete()

    interpretation = (
        ActivityCoachInterpretation(
            workout_id="workout-1",
            contract_version=(
                "activity-coach-v1"
            ),
            context_hash="context-hash",
            generated_at=datetime(
                2026,
                8,
                11,
                14,
                30,
            ),
            narrative=ActivityCoachNarrative(
                measured_facts=(
                    "Measured facts."
                ),
                deterministic_signals=(
                    "Load was above plan."
                ),
                prudent_interpretation=(
                    "The session was demanding."
                ),
                recommendations=(
                    "Approach the next session "
                    "conservatively."
                ),
                data_limitations=(
                    "Sleep was not recorded."
                ),
                provider="google-gemini",
                model="gemini-3.5-flash",
            ),
        )
    )

    athlete.activity_coach_interpretations = (
        ActivityCoachInterpretationBook(
            records=(
                interpretation,
            )
        )
    )

    data = athlete_to_dict(
        athlete
    )

    assert data["version"] == 10
    assert data[
        "activity_coach_interpretations"
    ][0][
        "context_hash"
    ] == "context-hash"

    loaded = athlete_from_dict(
        data
    )

    stored = (
        loaded
        .activity_coach_interpretations
        .find(
            workout_id="workout-1",
            contract_version=(
                "activity-coach-v1"
            ),
            context_hash="context-hash",
        )
    )

    assert stored is not None
    assert stored.generated_at == datetime(
        2026,
        8,
        11,
        14,
        30,
    )
    assert (
        stored.narrative.provider
        == "google-gemini"
    )
    assert (
        stored.narrative.recommendations
        == (
            "Approach the next session "
            "conservatively."
        )
    )


def test_loads_legacy_data_without_coach_interpretations():

    data = athlete_to_dict(
        create_athlete()
    )

    data.pop(
        "activity_coach_interpretations"
    )

    loaded = athlete_from_dict(
        data
    )

    assert len(
        loaded.activity_coach_interpretations
    ) == 0