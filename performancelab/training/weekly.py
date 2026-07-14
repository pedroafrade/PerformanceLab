"""
PerformanceLab

Weekly Summary

Represents one training week.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta

from performancelab.history import History
from performancelab.analysis import volume

from . import load


@dataclass
class WeeklySummary:

    start_date: date
    end_date: date

    history: History = field(default_factory=History)

    # ======================================================

    @property
    def workouts(self):

        return len(self.history)

    # ======================================================

    @property
    def sports(self):

        return self.history.sports

    # ======================================================

    @property
    def training_days(self):

        return len({

            workout.info.date

            for workout in self.history

            if workout.info.date is not None

        })

    # ======================================================

    @property
    def total_distance(self):

        return volume.total_distance(self.history)

    # ======================================================

    @property
    def total_duration(self):

        return volume.total_duration(self.history)

    # ======================================================

    @property
    def total_elevation(self):

        return volume.total_elevation(self.history)

    # ======================================================

    @property
    def duration(self):

        return self.total_duration

    # ======================================================

    @property
    def by_sport(self):

        """
        Returns one History object for each sport.

        Example

        {
            "Running": History(...),
            "Cycling": History(...),
            "Swimming": History(...)
        }
        """

        sports = {}

        for workout in self.history:

            sport = workout.info.sport or "Unknown"

            if sport not in sports:

                sports[sport] = History()

            sports[sport].add(workout)

        return sports

    # ======================================================

    @property
    def load(self):

        return load.weekly_load(self)

    # ======================================================

    def history_for(self, sport):

        return self.by_sport.get(sport, History())

    # ======================================================

    def __repr__(self):

        return (

            f"WeeklySummary("

            f"{self.start_date} -> {self.end_date}, "

            f"{self.workouts} workouts)"

        )