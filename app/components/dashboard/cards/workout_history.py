"""
PerformanceLab

Workout history dashboard card.
"""

from ...workout_details import (
    show_workout_details,
)
from ...workout_table import (
    show_workout_table,
)


def show_workout_history_card(
    athlete,
):
    """
    Displays the workout history card.

    Parameters
    ----------
    athlete
        Athlete whose workouts are displayed.

    Returns
    -------
    Workout | None
        Workout selected in the history table.
    """

    selected_workout = show_workout_table(
        athlete
    )

    if selected_workout is not None:

        show_workout_details(
            selected_workout
        )

    return selected_workout