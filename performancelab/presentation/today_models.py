"""
PerformanceLab

Today presentation models.
"""

from dataclasses import dataclass
from datetime import date

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

    recovery_score: int
    recovery_status: str
    form: float
    recent_load: float


@dataclass(frozen=True)
class TodayGuidanceData:
    """
    Presentation-ready reasons and cautions for today.
    """

    reasons: tuple[str, ...]
    cautions: tuple[str, ...]


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

    latest_activity: (
        LatestActivityCardData
    )
    latest_activity_summary: (
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