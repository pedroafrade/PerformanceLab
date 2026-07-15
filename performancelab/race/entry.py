"""
PerformanceLab

EventEntry

Represents an athlete's participation in a sporting event.
"""

from dataclasses import dataclass
from datetime import timedelta

from .event import Event


@dataclass
class EventEntry:

    event: Event

    priority: str = "B"

    target_time: timedelta | None = None

    result_time: timedelta | None = None

    position: int | None = None

    finished: bool = False

    dnf: bool = False

    dns: bool = False

    notes: str = ""

    # ======================================================

    @property
    def completed(self):

        return self.finished or self.dnf

    # ======================================================

    @property
    def pending(self):

        return not self.completed and not self.dns

    # ======================================================

    @property
    def is_goal(self):

        return self.priority.upper() in {"A", "B", "C"}

    # ======================================================

    def __repr__(self):

        return (

            f"EventEntry("

            f"event='{self.event.name}', "

            f"priority='{self.priority}', "

            f"finished={self.finished})"

        )