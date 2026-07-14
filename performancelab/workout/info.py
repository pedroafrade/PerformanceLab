"""
PerformanceLab

WorkoutInfo

Identity of a workout.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class WorkoutInfo:

    date: datetime | None = None

    sport: str | None = None

    title: str = ""

    description: str = ""

    source: str = ""

    timezone: str = ""

    distance: float | None = None

    duration: timedelta | None = None

    elevation_gain: float | None = None

    def __repr__(self):

        return (
            f"WorkoutInfo("
            f"sport={self.sport}, "
            f"date={self.date})"
        )