"""
PerformanceLab

Monthly Builder

Builds MonthlySummary objects from WeeklySummary objects.
"""

from .monthly import MonthlySummary


class MonthlyBuilder:

    # ======================================================

    def __init__(self, weeks):

        self.weeks = weeks

    # ======================================================

    def build(self):

        if len(self.weeks) == 0:

            return []

        months = {}

        for week in self.weeks:

            key = (

                week.start_date.year,

                week.start_date.month,

            )

            if key not in months:

                months[key] = MonthlySummary(

                    year=key[0],

                    month=key[1],

                )

            months[key].add_week(week)

        return list(months.values())

    # ======================================================

    def month(self, year, month):

        for summary in self.build():

            if (

                summary.year == year

                and

                summary.month == month

            ):

                return summary

        return None

    # ======================================================

    def __repr__(self):

        return (

            f"MonthlyBuilder("

            f"{len(self.weeks)} weeks)"

        )