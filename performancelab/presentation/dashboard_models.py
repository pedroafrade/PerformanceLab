"""
PerformanceLab

Dashboard presentation models.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Sequence


# ======================================================
# Athlete
# ======================================================

@dataclass(frozen=True)
class AthleteOverviewData:
    """
    Presentation-ready athlete overview.
    """

    name: str
    sports: Sequence[str]


# ======================================================
# Latest activity
# ======================================================

@dataclass(frozen=True)
class LatestActivityCardData:
    """
    Presentation-ready latest activity data.
    """

    sport: str | None
    title: str | None
    workout_date: date | datetime | None
    distance: float | None
    duration: timedelta | None
    elevation_gain: float | None
    average_heart_rate: float | None
    maximum_heart_rate: float | None
    average_power: float | None
    active_calories: float | None


# ======================================================
# Physiology
# ======================================================

@dataclass(frozen=True)
class PhysiologyCardData:
    """
    Presentation-ready current physiology data.
    """

    vo2_max: float | None
    resting_hr_30d: float | None
    walking_hr_30d: float | None
    hrv_30d: float | None
    estimated_ftp: float | None
    threshold_hr: float | None


# ======================================================
# Monthly sport summary
# ======================================================

@dataclass(frozen=True)
class MonthlySportSummaryData:
    """
    Presentation-ready monthly summary for one sport.
    """

    sport: str
    sessions: int
    distance: float
    duration: timedelta
    elevation_gain: float
    target_progress: int | None = None


@dataclass(frozen=True)
class MonthlySummaryCardData:
    """
    Presentation-ready monthly multisport summary.
    """

    start_date: date
    end_date: date
    sports: Sequence[MonthlySportSummaryData]


# ======================================================
# Planning
# ======================================================


@dataclass(frozen=True)
class WeeklyPlanDayData:
    """
    Presentation-ready plan for one day.
    """

    # calendar
    day: date

    # planned workout
    status: str
    sport: str | None
    title: str | None
    duration: timedelta | None
    distance: float | None
    intensity: str | None = None

    # presentation state
    is_today: bool = False
    is_next_workout: bool = False

    # execution state
    completed: bool = False
    completed_sport: str | None = None
    completed_title: str | None = None


@dataclass(frozen=True)
class WeeklyPlanData:
    """
    Presentation-ready seven-day training plan.
    """

    start_date: date
    end_date: date
    days: Sequence[WeeklyPlanDayData]


@dataclass(frozen=True)
class NextWorkoutData:
    """
    Presentation-ready next planned workout.
    """

    scheduled_at: datetime | None
    sport: str | None
    title: str | None
    duration: timedelta | None
    distance: float | None
    description: str | None
    intensity: str | None
    objective: str | None
    structure: Sequence[str] = ()
    equipment: Sequence[str] = ()


@dataclass(frozen=True)
class CoachRecommendationData:
    """
    Presentation-ready virtual coach recommendation.
    """

    summary: str
    recommendation: str
    status: str
    warnings: Sequence[str] = ()
    source: str = "rules"


@dataclass(frozen=True)
class PlanningCardData:
    """
    Complete presentation model for the planning card.
    """

    weekly_plan: WeeklyPlanData
    next_workout: NextWorkoutData | None
    coach: CoachRecommendationData


# ======================================================
# Summary
# ======================================================

@dataclass(frozen=True)
class DashboardSummaryData:
    """
    Presentation-ready dashboard summary.
    """

    workouts: int
    sports: int
    training_days: int

    total_duration: timedelta

    average_rpe: float | None

    ctl: float
    atl: float
    tsb: float


# ======================================================
# Performance
# ======================================================

@dataclass(frozen=True)
class PerformanceChartData:
    """
    Presentation-ready performance chart data.
    """

    dates: Sequence[date | datetime]

    load: Sequence[float]

    ctl: Sequence[float]
    atl: Sequence[float]
    tsb: Sequence[float]


# ======================================================
# Recovery
# ======================================================

@dataclass(frozen=True)
class RecoveryCardData:
    """
    Presentation-ready recovery data.
    """

    score: int
    status: str
    recommendation: str
    trend: str | None = None


# ======================================================
# Training load
# ======================================================

@dataclass(frozen=True)
class TrainingLoadCardData:
    """
    Presentation-ready training load data.
    """

    acute_load: float
    chronic_load: float
    ramp_rate: float
    score: int
    status: str
    recommendation: str

# ======================================================
# Next event
# ======================================================

@dataclass(frozen=True)
class NextEventCardData:
    """
    Presentation-ready next sporting event.
    """

    name: str | None
    event_date: date | None
    days_remaining: int | None

    sport: str | None
    distance: float | None

    location: str | None
    country: str | None

    priority: str | None
    target_time: timedelta | None

    elevation_gain: float | None = None
    website: str | None = None
    description: str | None = None