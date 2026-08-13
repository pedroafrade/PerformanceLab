"""
PerformanceLab

Today presentation models.
"""

from dataclasses import dataclass
from datetime import date, datetime

from .activity_models import (
    ActivityListItemData,
)
from .dashboard_models import (
    CoachRecommendationData,
    LatestActivityCardData,
    NextEventCardData,
    NextWorkoutData,
    RecoveryCardData,
    TrainingLoadCardData,
    WeeklyPlanDayData,
)


@dataclass(frozen=True)
class TodayReadinessData:
    """
    Presentation-ready physiological context for
    the daily training decision.
    """

    recovery_score: float
    recovery_balance: float
    recovery_status: str
    form: float
    recent_load: float
    reference_time: datetime | None = None
    hours_since_last_workout: (
        float | None
    ) = None
    recovery_is_time_aware: bool = False


@dataclass(frozen=True)
class TodayGuidanceData:
    """
    Presentation-ready daily training decision.

    The recommendation is temporary and does not imply
    that the persistent TrainingPlan was modified.
    """

    decision: str
    title: str
    action: str
    plan_is_modified: bool

    reasons: tuple[str, ...]
    cautions: tuple[str, ...]


@dataclass(frozen=True)
class TodayAdaptationData:
    """
    Presentation-ready before/after plan adaptation.
    """

    workout_title: str

    previous_minutes: int
    revised_minutes: int

    reason: str

    previous_distance: float | None = None
    revised_distance: float | None = None

    previous_elevation_gain: float | None = None
    revised_elevation_gain: float | None = None

    previous_prescription: str | None = None
    revised_prescription: str | None = None


@dataclass(frozen=True)
class TodayData:
    """
    Presentation-ready daily athlete context.
    """

    reference_day: date

    today_session: (
        WeeklyPlanDayData
        | None
    )

    next_workout: (
        NextWorkoutData
        | None
    )

    coach: CoachRecommendationData
    readiness: TodayReadinessData
    guidance: TodayGuidanceData
    latest_adaptation: (
        TodayAdaptationData
        | None
    )

    latest_activity: (
        LatestActivityCardData
    )
    latest_activity_summary: (
        ActivityListItemData
        | None
    )
    today_activity_summary: (
        ActivityListItemData
        | None
    )
    recovery: RecoveryCardData

    training_load: (
        TrainingLoadCardData
    )

    next_event: (
        NextEventCardData
        | None
    )
