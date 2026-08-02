"""
PerformanceLab

Workout

Complete workout object.
"""

from dataclasses import dataclass, field
from uuid import uuid4

from .environment import Environment
from .feedback import AthleteFeedback
from .info import WorkoutInfo
from .sensors import SensorCollection


@dataclass
class Workout:

    workout_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    info: WorkoutInfo = field(default_factory=WorkoutInfo)

    environment: Environment = field(default_factory=Environment)

    feedback: AthleteFeedback = field(default_factory=AthleteFeedback)

    sensors: SensorCollection = field(default_factory=SensorCollection)

    # ======================================================

    @property
    def sport(self):

        return self.info.sport

    # ======================================================

    @property
    def date(self):

        return self.info.date

    # ======================================================

    @property
    def distance(self):

        return self.info.distance

    # ======================================================

    @property
    def duration(self):

        return self.info.duration

    # ======================================================

    @property
    def elevation_gain(self):

        return self.info.elevation_gain

    # ======================================================

    def __repr__(self):

        return (
            f"Workout("
            f"sport={self.info.sport}, "
            f"date={self.info.date})"
        )