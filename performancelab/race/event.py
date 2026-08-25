"""
PerformanceLab

Event

Represents a sporting event.
"""

from dataclasses import dataclass, field
from uuid import uuid4
from datetime import (
    date as CalendarDate,
    timedelta,
)

ELEVATION_METRES_PER_EFFORT_KILOMETRE = 100.0

ROLLING_ELEVATION_METRES_PER_KILOMETRE = 10.0
HILLY_ELEVATION_METRES_PER_KILOMETRE = 25.0
MOUNTAINOUS_ELEVATION_METRES_PER_KILOMETRE = 40.0


@dataclass
class Event:

    name: str = ""

    location: str = ""

    country: str = ""

    date: CalendarDate | None = None

    sport: str = ""

    distance: float | None = None

    elevation_gain: float | None = None

    terrain: str = ""

    surface: str = ""

    organizer: str = ""

    website: str = ""

    gpx_file: str = ""

    description: str = ""

    event_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    
    # ======================================================

    @property
    def is_running_event(self) -> bool:
        """
        Returns whether the event belongs to the running family.
        """

        normalized_sport = self.sport.strip().lower()

        return any(
            token in normalized_sport
            for token in (
                "run",
                "running",
                "trail",
                "jog",
            )
        )

    # ======================================================

    @property
    def effort_distance(self) -> float | None:
        """
        Returns running effort distance in equivalent kilometres.

        Each 100 metres of elevation gain represents one
        additional kilometre of effort.
        """

        if (
            not self.is_running_event
            or self.distance is None
        ):
            return None

        elevation_gain = max(
            self.elevation_gain or 0.0,
            0.0,
        )

        return (
            max(self.distance, 0.0)
            + (
                elevation_gain
                / ELEVATION_METRES_PER_EFFORT_KILOMETRE
            )
        )

    # ======================================================

    def estimated_duration_at_pace(
        self,
        pace_minutes_per_kilometre: float | None,
    ) -> timedelta | None:
        """
        Estimates the event duration from an athlete's
        running pace and the event effort distance.

        Pace is expressed in minutes per kilometre.
        """

        effort_distance = self.effort_distance

        if (
            effort_distance is None
            or pace_minutes_per_kilometre is None
            or pace_minutes_per_kilometre <= 0
        ):
            return None

        return timedelta(
            minutes=(
                effort_distance
                * pace_minutes_per_kilometre
            )
        )
    
    # ======================================================

    @property
    def elevation_metres_per_kilometre(
        self,
    ) -> float | None:
        """
        Returns average elevation gain per kilometre.

        The value is only defined for running events with
        a positive distance.
        """

        if (
            not self.is_running_event
            or self.distance is None
            or self.distance <= 0
        ):
            return None

        elevation_gain = max(
            self.elevation_gain or 0.0,
            0.0,
        )

        return (
            elevation_gain
            / self.distance
        )

    # ======================================================

    @property
    def elevation_demand(
        self,
    ) -> str | None:
        """
        Classifies the climbing demand of a running event.
        """

        metres_per_kilometre = (
            self.elevation_metres_per_kilometre
        )

        if metres_per_kilometre is None:
            return None

        if (
            metres_per_kilometre
            >= MOUNTAINOUS_ELEVATION_METRES_PER_KILOMETRE
        ):
            return "mountainous"

        if (
            metres_per_kilometre
            >= HILLY_ELEVATION_METRES_PER_KILOMETRE
        ):
            return "hilly"

        if (
            metres_per_kilometre
            >= ROLLING_ELEVATION_METRES_PER_KILOMETRE
        ):
            return "rolling"

        return "flat"

    # ======================================================

    @property
    def is_future(self):

        if self.date is None:

            return False

        return self.date >= CalendarDate.today()

    # ======================================================

    @property
    def is_past(self):

        if self.date is None:

            return False

        return self.date < CalendarDate.today()

    # ======================================================

    @property
    def days_remaining(self):

        if self.date is None:

            return None

        return (self.date - CalendarDate.today()).days

    # ======================================================

    def __repr__(self):

        return (

            f"Event("

            f"name='{self.name}', "

            f"sport='{self.sport}', "

            f"distance={self.distance}, "

            f"elevation_gain={self.elevation_gain})"

        )