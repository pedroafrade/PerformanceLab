"""
PerformanceLab

AthleteAnalytics

Descriptive analysis of an athlete's training history.
"""

from datetime import timedelta


class AthleteAnalytics:

    # ======================================================

    def __init__(self, history):

        self.history = history

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
    def total_duration(self):

        total = timedelta()

        for workout in self.history:

            duration = getattr(workout, "duration", None)

            if duration is not None:

                total += duration

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

    def summary(self):

        print()

        print("=" * 50)

        print("ATHLETE ANALYTICS")

        print("=" * 50)

        print(f"Workouts   : {self.number_of_workouts}")
        print(f"Sports     : {', '.join(self.sports)}")
        print(f"Duration   : {self.total_duration}")
        print(f"Average RPE: {self.average_rpe}")

        print("=" * 50)

    # ======================================================

    def __repr__(self):

        return (

            f"AthleteAnalytics("

            f"{self.number_of_workouts} workouts)"

        )