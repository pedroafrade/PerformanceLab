"""
PerformanceLab

Weekly Plan Builder

Builds WeeklyPlan objects from planned workouts.
"""

from datetime import date, datetime, timedelta

from .weekly_plan import WeeklyPlan


class WeeklyPlanBuilder:

    # ======================================================

    def __init__(self, workouts=None):

        self.workouts = list(workouts or [])

    # ======================================================

    @staticmethod
    def week_start(day):

        if isinstance(day, datetime):

            day = day.date()

        return day - timedelta(
            days=day.weekday(),
        )

    # ======================================================

    @staticmethod
    def week_end(day):

        return WeeklyPlanBuilder.week_start(
            day,
        ) + timedelta(days=6)

    # ======================================================

    def week(self, day=None):

        day = day or date.today()

        start = self.week_start(day)

        end = self.week_end(day)

        plan = WeeklyPlan(
            start_date=start,
            end_date=end,
        )

        for workout in self.workouts:

            if (
                start
                <= workout.day
                <= end
            ):

                plan.add(workout)

        return plan

    # ======================================================

    def next_workout(self):

        return self.week().next_workout()

    # ======================================================

    def __repr__(self):

        return (
            f"WeeklyPlanBuilder("
            f"{len(self.workouts)} planned workouts)"
        )