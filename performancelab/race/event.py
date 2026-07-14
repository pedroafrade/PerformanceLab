"""
PerformanceLab

Event

Represents a sporting event.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:

    name: str = ""

    location: str = ""

    country: str = ""

    date: datetime | None = None

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
    def is_future(self):

        if self.date is None:

            return False

        return self.date > datetime.now()

    # ======================================================

    @property
    def days_remaining(self):

        if self.date is None:

            return None

        return (self.date - datetime.now()).days

    # ======================================================

    def __repr__(self):

        return (

            f"Event("

            f"name='{self.name}', "

            f"sport='{self.sport}', "

            f"distance={self.distance}, "

            f"elevation_gain={self.elevation_gain})"

        )