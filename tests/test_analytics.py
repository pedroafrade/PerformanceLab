"""
PerformanceLab

Tests for AthleteAnalytics.
"""

from datetime import date
from datetime import timedelta

from performancelab import Athlete
from performancelab.workout import Workout

import performancelab.analysis.time as t

print(t.__file__)
print(hasattr(t, "training_days"))
print(dir(t))

# ======================================================

def create_workout(
    sport,
    workout_date,
    distance,
    duration,
    elevation,
    rpe,
):

    workout = Workout()

    workout.info.sport = sport
    workout.info.date = workout_date
    workout.info.distance = distance
    workout.info.duration = duration

    workout.info.elevation_gain = elevation

    workout.feedback.rpe = rpe

    return workout


# ======================================================

def test_empty_analytics():

    athlete = Athlete(name="Pedro")

    analytics = athlete.analytics

    assert analytics.number_of_workouts == 0

    assert analytics.total_distance == 0

    assert analytics.total_duration == timedelta()

    assert analytics.total_elevation == 0

    assert analytics.average_rpe is None

    assert analytics.training_days == 0

    assert analytics.first_workout is None

    assert analytics.last_workout is None


# ======================================================

def test_number_of_workouts():

    athlete = Athlete()

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            10,

            timedelta(hours=1),

            250,

            6,

        )

    )

    athlete.history.add(

        create_workout(

            "Cycling",

            date(2026, 7, 2),

            50,

            timedelta(hours=2),

            600,

            5,

        )

    )

    assert athlete.analytics.number_of_workouts == 2


# ======================================================

def test_total_distance():

    athlete = Athlete()

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            10,

            timedelta(hours=1),

            100,

            6,

        )

    )

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 2),

            15,

            timedelta(hours=1, minutes=30),

            300,

            7,

        )

    )

    assert athlete.analytics.total_distance == 25


# ======================================================

def test_total_duration():

    athlete = Athlete()

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            10,

            timedelta(hours=1),

            100,

            6,

        )

    )

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 2),

            15,

            timedelta(hours=2),

            300,

            7,

        )

    )

    assert athlete.analytics.total_duration == timedelta(hours=3)


# ======================================================

def test_total_elevation():

    athlete = Athlete()

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            10,

            timedelta(hours=1),

            350,

            6,

        )

    )

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 2),

            20,

            timedelta(hours=2),

            650,

            7,

        )

    )

    assert athlete.analytics.total_elevation == 1000


# ======================================================

def test_average_rpe():

    athlete = Athlete()

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            10,

            timedelta(hours=1),

            100,

            6,

        )

    )

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 2),

            10,

            timedelta(hours=1),

            100,

            8,

        )

    )

    assert athlete.analytics.average_rpe == 7


# ======================================================

def test_training_days():

    athlete = Athlete()

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            5,

            timedelta(minutes=30),

            50,

            5,

        )

    )

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            5,

            timedelta(minutes=30),

            50,

            5,

        )

    )

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 2),

            10,

            timedelta(hours=1),

            100,

            6,

        )

    )

    assert athlete.analytics.training_days == 2


# ======================================================

def test_first_and_last_workout():

    athlete = Athlete()

    first = create_workout(

        "Running",

        date(2026, 7, 1),

        10,

        timedelta(hours=1),

        100,

        6,

    )

    last = create_workout(

        "Running",

        date(2026, 7, 10),

        20,

        timedelta(hours=2),

        500,

        8,

    )

    athlete.history.add(last)

    athlete.history.add(first)

    assert athlete.analytics.first_workout == first

    assert athlete.analytics.last_workout == last


# ======================================================

def test_summary():

    athlete = Athlete()

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            10,

            timedelta(hours=1),

            200,

            7,

        )

    )

    summary = athlete.analytics.summary()

    assert summary["workouts"] == 1

    assert summary["total_distance"] == 10

    assert summary["total_elevation"] == 200

    assert summary["average_rpe"] == 7