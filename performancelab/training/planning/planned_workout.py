"""
PerformanceLab

Planned Workout

Represents one planned workout.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class PlannedWorkout:
    """
    Represents one planned workout.
    """

    scheduled_at: datetime

    sport: str | None = None
    title: str | None = None

    duration: timedelta | None = None
    distance: float | None = None

    description: str | None = None
    intensity: str | None = None
    objective: str | None = None

    structure: tuple[str, ...] = ()
    equipment: tuple[str, ...] = ()

    # ======================================================

    @property
    def day(self):

        return self.scheduled_at.date()

    # ======================================================

    @property
    def is_rest(self):

        return (
            self.sport is None
            and self.title is None
            and self.duration is None
            and self.distance is None
        )

    # ======================================================

    def __repr__(self):

        return (
            "PlannedWorkout("
            f"{self.scheduled_at.isoformat()}, "
            f"sport={self.sport!r}, "
            f"title={self.title!r})"
        )