"""
PerformanceLab

Immutable Training Coach presentation models.
"""

from dataclasses import (
    dataclass,
    field,
)

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
class ActivityCoachRecentTrainingData:
    """
    Immutable training context ending on the activity day.
    """

    window_days: int = 7
    session_count: int = 0
    total_duration_minutes: float = 0.0
    total_load: float = 0.0

    previous_title: str | None = None
    previous_days_before: int | None = None
    previous_load: float | None = None


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

    recent_training: (
        ActivityCoachRecentTrainingData
    ) = field(
        default_factory=(
            ActivityCoachRecentTrainingData
        )
    )