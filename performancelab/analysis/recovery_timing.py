"""
PerformanceLab

Recovery timing.

Represents the temporal context used by recovery
estimates.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(
    frozen=True,
    slots=True,
)
class RecoveryTiming:
    """
    Immutable recovery timing snapshot.

    A workout without an exact completion time does not
    produce an elapsed-hours estimate.
    """

    reference_time: datetime
    last_workout_ended_at: (
        datetime | None
    ) = None

    @property
    def hours_since_last_workout(
        self,
    ) -> float | None:
        """
        Returns complete and partial hours since the last
        workout ended.
        """

        if (
            self.last_workout_ended_at
            is None
        ):
            return None

        elapsed = (
            self.reference_time
            - self.last_workout_ended_at
        )

        return max(
            elapsed.total_seconds()
            / 3600,
            0.0,
        )