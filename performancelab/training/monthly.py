"""
PerformanceLab

Monthly Summary

Represents a collection of training weeks assigned to one month.
"""

from dataclasses import dataclass, field
from datetime import timedelta

from . import load
from .weekly import WeeklySummary


@dataclass
class MonthlySummary:

    year: int
    month: int

    weeks: list[WeeklySummary] = field(default_factory=list)

    # ======================================================

    @property
    def workouts(self):

        return sum(

            week.workouts

            for week in self.weeks

        )

    # ======================================================

    @property
    def training_days(self):

        dates = {

            workout.date

            for week in self.weeks

            for workout in week.history

            if workout.date is not None

        }

        return len(dates)

    # ======================================================

    @property
    def total_duration(self):

        return sum(

            (

                week.total_duration

                for week in self.weeks

            ),

            timedelta(),

        )

    # ======================================================

    @property
    def duration(self):

        return self.total_duration

    # ======================================================

    @property
    def sports(self):

        sports = set()

        for week in self.weeks:

            sports.update(week.sports)

        return sorted(sports)

    # ======================================================

    def distance_for(self, sport):

        return sum(

            week.distance_for(sport)

            for week in self.weeks

        )

    # ======================================================

    def duration_for(self, sport):

        return sum(

            (

                week.duration_for(sport)

                for week in self.weeks

            ),

            timedelta(),

        )

    # ======================================================

    def elevation_for(self, sport):

        return sum(

            week.elevation_for(sport)

            for week in self.weeks

        )

    # ======================================================

    @property
    def load(self):

        return load.monthly_load(self)

    # ======================================================

    def add_week(self, week: WeeklySummary):

        self.weeks.append(week)

        self.weeks.sort(

            key=lambda item: item.start_date,

        )

    # ======================================================

    def __repr__(self):

        return (

            f"MonthlySummary("

            f"{self.year}-{self.month:02d}, "

            f"{len(self.weeks)} weeks)"

        )