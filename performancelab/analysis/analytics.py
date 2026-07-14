"""
PerformanceLab

AthleteAnalytics

Descriptive analysis of an athlete's training data.
"""

from datetime import timedelta


class AthleteAnalytics:

    # ======================================================

    def __init__(self, athlete):

        self.athlete = athlete

    # ======================================================

    @property
    def history(self):

        return self.athlete.history

    # ======================================================

    @property
    def number_of_workouts(self):

        return len(self.history)

    # ======================================================

    @property
    def sports(self):

        return self.history.sports

    # ======================================================

    @property
    def first_workout(self):

        if len(self.history) == 0:

            return None

        return self.history[0]

    # ======================================================

    @property
    def last_workout(self):

        if len(self.history) == 0:

            return None

        return self.history[-1]

    # ======================================================

    @property
    def total_distance(self):

        total = 0.0

        for workout in self.history:

            distance = getattr(workout.info, "distance", None)

            if distance is not None:

                total += distance

        return total

    # ======================================================

    @property
    def total_duration(self):

        total = timedelta()

        for workout in self.history:

            duration = getattr(workout.info, "duration", None)

            if duration is not None:

                total += duration

        return total

    # ======================================================

    @property
    def total_elevation(self):

        total = 0.0

        for workout in self.history:

            elevation = getattr(
                workout.environment,
                "elevation_gain",
                None
            )

            if elevation is not None:

                total += elevation

        return total

    # ======================================================

    @property
    def average_rpe(self):

        values = [

            workout.feedback.rpe

            for workout in self.history

            if workout.feedback.rpe is not None

        ]

        if not values:

            return None

        return sum(values) / len(values)

    # ======================================================

    @property
    def training_days(self):

        dates = {

            workout.info.date

            for workout in self.history

            if workout.info.date is not None

        }

        return len(dates)

    # ======================================================

    def summary(self):

        return {

            "workouts": self.number_of_workouts,

            "sports": self.sports,

            "distance": self.total_distance,

            "duration": self.total_duration,

            "elevation": self.total_elevation,

            "training_days": self.training_days,

            "average_rpe": self.average_rpe,

            "first_workout": self.first_workout,

            "last_workout": self.last_workout,

        }

    # ======================================================

    def __repr__(self):

        return (

            f"AthleteAnalytics("

            f"{self.number_of_workouts} workouts)"

        )