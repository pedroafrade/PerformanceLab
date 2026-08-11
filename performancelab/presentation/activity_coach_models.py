"""
PerformanceLab

Immutable Training Coach presentation models.
"""

from dataclasses import (
    dataclass,
    field,
)

from performancelab.coaching.activity_signals import (
    ActivityCoachSignal,
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
class ActivityCoachPlanData:
    """
    Training-plan context on the activity day.
    """

    phase: str | None = None


@dataclass(frozen=True)
class ActivityCoachEventData:
    """
    Next competition relative to the activity day.
    """

    name: str | None = None
    sport: str | None = None
    distance: float | None = None
    elevation_gain: float | None = None
    terrain: str | None = None
    priority: str | None = None
    days_until_event: int | None = None


@dataclass(frozen=True)
class ActivityCoachPhysiologyData:
    """
    Physiological references available to the coach.

    Dynamic TrainingState values are exposed only when
    the selected activity is the latest recorded activity.
    """

    threshold_hr: int | None = None
    ftp: float | None = None

    state_is_current: bool = False
    readiness: str | None = None
    recovery_score: float | None = None
    load_state: str | None = None


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

    plan: ActivityCoachPlanData = field(
        default_factory=(
            ActivityCoachPlanData
        )
    )

    event: ActivityCoachEventData = field(
        default_factory=(
            ActivityCoachEventData
        )
    )

    physiology: (
        ActivityCoachPhysiologyData
    ) = field(
        default_factory=(
            ActivityCoachPhysiologyData
        )
    )


@dataclass(frozen=True)
class ActivityCoachAssessmentData:
    """
    Immutable assessment assembled for one completed activity.

    The factual context remains separate from deterministic
    domain signals. No generated coaching narrative belongs
    in this object.
    """

    context: ActivityCoachContextData
    signals: tuple[
        ActivityCoachSignal,
        ...,
    ] = ()