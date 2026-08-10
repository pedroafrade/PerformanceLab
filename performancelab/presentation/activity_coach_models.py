"""
PerformanceLab

Immutable Training Coach presentation models.
"""

from dataclasses import dataclass

from .activity_models import (
    ActivityListItemData,
)


@dataclass(frozen=True)
class ActivityCoachSensorData:
    """
    Immutable average and maximum sensor values.
    """

    average: float | None = None
    maximum: float | None = None


@dataclass(frozen=True)
class ActivityCoachContextData:
    """
    Factual context for one completed activity.

    This object contains measured or already calculated
    values only. It does not contain coach conclusions.
    """

    activity: ActivityListItemData

    heart_rate: ActivityCoachSensorData
    power: ActivityCoachSensorData
    cadence: ActivityCoachSensorData

    temperature: float | None = None
    humidity: float | None = None
    terrain: str | None = None