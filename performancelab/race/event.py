"""
PerformanceLab

Event

Represents a sporting event.
"""

from dataclasses import dataclass
from datetime import date

ELEVATION_METRES_PER_EFFORT_KILOMETRE = 100.0


@dataclass
class Event:

    name: str = ""

    location: str = ""

    country: str = ""

    date: date | None = None

    sport: str = ""

    distance: float | None = None

    elevation_gain: float | None = None

    terrain: str = ""

    surface: str = ""

    organizer: str = ""

    website: str = ""

    gpx_file: str = ""

    description: str = ""

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

    @property
    def is_future(self):

        if self.date is None:

            return False

        return self.date >= date.today()

    # ======================================================

    @property
    def is_past(self):

        if self.date is None:

            return False

        return self.date < date.today()

    # ======================================================

    @property
    def days_remaining(self):

        if self.date is None:

            return None

        return (self.date - date.today()).days

    # ======================================================

    def __repr__(self):

        return (

            f"Event("

            f"name='{self.name}', "

            f"sport='{self.sport}', "

            f"distance={self.distance}, "

            f"elevation_gain={self.elevation_gain})"

        )