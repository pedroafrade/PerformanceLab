"""
PerformanceLab

Workout

Complete workout object.
"""

from dataclasses import dataclass, field
from datetime import datetime
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
    @property
    def reconciliation_signature(
        self,
    ) -> tuple[
        str,
        str,
        float | None,
        float | None,
    ]:
        """
        Returns the immutable workout state that affects
        outcome assessment and completed training load.
        """

        workout_day = self.date

        if isinstance(
            workout_day,
            datetime,
        ):
            workout_day = (
                workout_day.date()
            )

        day_value = (
            workout_day.isoformat()
            if workout_day is not None
            else ""
        )

        sport_value = str(
            self.sport or ""
        ).strip().lower()

        duration_seconds = (
            float(
                self.duration.total_seconds()
            )
            if self.duration is not None
            else None
        )

        effective_rpe = (
            self.feedback.effective_rpe
        )

        rpe_value = (
            float(effective_rpe)
            if effective_rpe is not None
            else None
        )

        return (
            day_value,
            sport_value,
            duration_seconds,
            rpe_value,
        )

    # ======================================================
    
    def __repr__(self):

        return (
            f"Workout("
            f"sport={self.info.sport}, "
            f"date={self.info.date})"
        )