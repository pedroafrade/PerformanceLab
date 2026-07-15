"""
PerformanceLab

Weekly Summary

Represents one training week.
"""

from dataclasses import dataclass, field
from datetime import date

from performancelab.analysis import time
from performancelab.analysis import volume
from performancelab.history import History

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

        return time.training_days(self.history)

    # ======================================================

    @property
    def total_duration(self):

        """
        Total training time across all sports.

        This represents total time spent training, not
        sport-specific volume.
        """

        return volume.total_duration(self.history)

    # ======================================================

    @property
    def duration(self):

        return self.total_duration

    # ======================================================

    @property
    def by_sport(self):

        histories = {}

        for workout in self.history:

            sport = workout.sport or "Unknown"

            if sport not in histories:

                histories[sport] = History()

            histories[sport].add(workout)

        return histories

    # ======================================================

    def history_for(self, sport):

        return self.by_sport.get(

            sport,

            History(),

        )

    # ======================================================

    def distance_for(self, sport):

        return volume.total_distance(

            self.history_for(sport),

        )

    # ======================================================

    def duration_for(self, sport):

        return volume.total_duration(

            self.history_for(sport),

        )

    # ======================================================

    def elevation_for(self, sport):

        return volume.total_elevation(

            self.history_for(sport),

        )

    # ======================================================

    @property
    def load(self):

        return load.weekly_load(self)

    # ======================================================

    def __repr__(self):

        return (

            f"WeeklySummary("

            f"{self.start_date} -> {self.end_date}, "

            f"{self.workouts} workouts)"

        )