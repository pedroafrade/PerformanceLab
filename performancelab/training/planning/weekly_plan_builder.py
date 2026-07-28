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

    def window(
        self,
        center_day=None,
    ):
        """
        Builds a seven-day window centred on the supplied day.

        The returned range contains:

        - three days before the centre day;
        - the centre day;
        - three days after the centre day.
        """

        center_day = center_day or date.today()

        if isinstance(
            center_day,
            datetime,
        ):
            center_day = center_day.date()

        start = center_day - timedelta(
            days=3,
        )

        end = center_day + timedelta(
            days=3,
        )

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