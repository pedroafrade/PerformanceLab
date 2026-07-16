"""
PerformanceLab

Workout Factory.
"""

from datetime import date, timedelta

from performancelab import Workout


# ======================================================
# Workout creation
# ======================================================

def create_workout(
    sport: str,
    workout_date: date,
    distance: float | None,
    duration: timedelta,
    elevation_gain: float | None,
    rpe: float | None,
    title: str = "",
    description: str = "",
) -> Workout:

    """
    Creates a Workout from user input.
    """

    workout = Workout()

    workout.info.sport = sport
    workout.info.date = workout_date
    workout.info.distance = distance
    workout.info.duration = duration
    workout.info.elevation_gain = elevation_gain
    workout.info.title = title
    workout.info.description = description
    workout.info.source = "manual"

    workout.feedback.rpe = rpe

    return workout