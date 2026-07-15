"""
PerformanceLab

Weekly Builder

Builds WeeklySummary objects from a History.
"""

from datetime import date, datetime, timedelta

from performancelab.history import History

from .weekly import WeeklySummary


class WeeklyBuilder:

    # ======================================================

    def __init__(self, history: History):

        self.history = history

    # ======================================================

    @staticmethod
    def _calendar_date(value):

        if isinstance(value, datetime):

            return value.date()

        return value

    # ======================================================

    @staticmethod
    def week_start(day):

        """
        Returns Monday of the week.
        """

        day = WeeklyBuilder._calendar_date(day)

        return day - timedelta(

            days=day.weekday(),

        )

    # ======================================================

    @staticmethod
    def week_end(day):

        """
        Returns Sunday of the week.
        """

        return WeeklyBuilder.week_start(

            day,

        ) + timedelta(days=6)

    # ======================================================

    def week(self, day):

        """
        Returns the WeeklySummary containing the given day.
        """

        start = self.week_start(day)
        end = self.week_end(day)

        summary = WeeklySummary(

            start_date=start,

            end_date=end,

        )

        for workout in self.history:

            if workout.date is None:

                continue

            workout_date = self._calendar_date(

                workout.date,

            )

            if start <= workout_date <= end:

                summary.history.add(workout)

        return summary

    # ======================================================

    def build(self):

        """
        Returns all weeks represented in the history.
        """

        starts = {

            self.week_start(workout.date)

            for workout in self.history

            if workout.date is not None

        }

        return [

            self.week(start)

            for start in sorted(starts)

        ]

    # ======================================================

    def __repr__(self):

        return (

            f"WeeklyBuilder("

            f"{len(self.history)} workouts)"

        )