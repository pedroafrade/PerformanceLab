"""
PerformanceLab

Goal

Represents a future objective of an athlete.
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class Goal:

    name: str = ""

    description: str = ""

    date: date | None = None

    priority: str = "B"

    completed: bool = False

    # ======================================================

    @property
    def is_future(self):

        if self.date is None:

            return False

        return self.date >= date.today()

    # ======================================================

    @property
    def is_active(self):

        return self.is_future and not self.completed

    # ======================================================

    @property
    def days_remaining(self):

        if self.date is None:

            return None

        return (self.date - date.today()).days

    # ======================================================

    def __repr__(self):

        return (

            f"Goal("

            f"name='{self.name}', "

            f"date={self.date}, "

            f"priority='{self.priority}')"

        )