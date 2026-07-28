from performancelab.workout import (
    Workout,
    estimate_workout_rpe,
)


def workout_with_heart_rate() -> Workout:

    workout = Workout()

    workout.sensors.add(
        "heart_rate",
        [
            {
                "time": "2026-07-28T10:00:00",
                "value": 120,
            },
            {
                "time": "2026-07-28T10:01:00",
                "value": 162,
            },
        ],
    )

    return workout


def test_estimates_and_stores_workout_rpe():

    workout = workout_with_heart_rate()

    estimate = estimate_workout_rpe(
        workout,
        max_hr=190,
        resting_hr=50,
    )

    assert estimate == 5.0
    assert workout.feedback.estimated_rpe == 5.0
    assert workout.feedback.effective_rpe == 5.0


def test_manual_rpe_keeps_priority():

    workout = workout_with_heart_rate()

    workout.feedback.rpe = 8

    estimate_workout_rpe(
        workout,
        max_hr=190,
        resting_hr=50,
    )

    assert workout.feedback.estimated_rpe == 5.0
    assert workout.feedback.effective_rpe == 8


def test_missing_heart_rate_keeps_estimate_empty():

    workout = Workout()

    estimate = estimate_workout_rpe(
        workout,
        max_hr=190,
        resting_hr=50,
    )

    assert estimate is None
    assert workout.feedback.estimated_rpe is None


def test_missing_athlete_profile_keeps_estimate_empty():

    workout = workout_with_heart_rate()

    estimate = estimate_workout_rpe(
        workout,
        max_hr=None,
        resting_hr=50,
    )

    assert estimate is None
    assert workout.feedback.estimated_rpe is None