"""
PerformanceLab

Weekly Builder

Builds WeeklySummary objects from a History.
"""

from datetime import timedelta

from .weekly import WeeklySummary


class WeeklyBuilder:

    # ======================================================

    def __init__(self, history):

        self.history = history

    # ======================================================

    @staticmethod
    def week_start(day):

        """
        Returns Monday of the week.
        """

        return day - timedelta(days=day.weekday())

    # ======================================================

    @staticmethod
    def week_end(day):

        """
        Returns Sunday of the week.
        """

        return WeeklyBuilder.week_start(day) + timedelta(days=6)

    # ======================================================

    def week(self, day):

        """
        Returns one WeeklySummary containing the workouts
        of the week where 'day' belongs.
        """

        start = self.week_start(day)
        end = self.week_end(day)

        summary = WeeklySummary(

            start_date=start,
            end_date=end,

        )

        for workout in self.history:

            workout_date = workout.info.date

            if workout_date is None:

                continue

            if start <= workout_date <= end:

                summary.history.add(workout)

        return summary

    # ======================================================

    def build(self):

        """
        Returns all weeks present in the history.
        """

        if len(self.history) == 0:

            return []

        starts = {

            self.week_start(workout.info.date)

            for workout in self.history

            if workout.info.date is not None

        }

        weeks = [

            self.week(start)

            for start in sorted(starts)

        ]

        return weeks

    # ======================================================

    def __repr__(self):

        return (

            f"WeeklyBuilder("

            f"{len(self.history)} workouts)"

        )