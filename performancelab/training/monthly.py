"""
PerformanceLab

Monthly Summary

Represents one training month.
"""
from datetime import timedelta
from dataclasses import dataclass, field

from .weekly import WeeklySummary
from . import load


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

        return sum(

            week.training_days

            for week in self.weeks

        )

    # ======================================================

    @property
    def duration(self):

        return sum(

            (

                week.duration

                for week in self.weeks

            ),

            start=type(self.weeks[0].duration)() if self.weeks else __import__("datetime").timedelta(),

        )

    # ======================================================

    @property
    def sports(self):

        sports = set()

        for week in self.weeks:

            sports.update(week.sports)

        return sorted(sports)
    # ======================================================

    @property
    def load(self):

        return load.monthly_load(self)
    
    # ======================================================
    
    @property
    def duration(self):

     total = timedelta()

     for week in self.weeks:

        total += week.duration

     return total
    # ======================================================

    def add_week(self, week):

        self.weeks.append(week)

    # ======================================================

    def __repr__(self):

        return (

            f"MonthlySummary("

            f"{self.year}-{self.month:02d}, "

            f"{len(self.weeks)} weeks)"

        )