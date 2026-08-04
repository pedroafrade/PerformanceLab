"""
PerformanceLab

Complete training-plan presentation models.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta


@dataclass(frozen=True)
class PlanWorkoutData:
    """
    One presentation-ready planned workout.
    """

    scheduled_at: datetime
    sport: str | None
    title: str
    duration: timedelta | None
    distance: float | None
    elevation_gain: float | None
    intensity: str | None
    phase: str | None
    planned_load: float | None
    status: str
    prescription_summary: str | None
    structure: tuple[str, ...]

@dataclass(frozen=True)
class PlanProgressionPointData:
    """
    One weekly point in the plan progression overview.
    """

    week_start: date
    phase: str | None
    planned_load: float
    duration_minutes: float
    distance: float
    elevation_gain: float

@dataclass(frozen=True)
class PlanWeekData:
    """
    One presentation-ready training week.
    """

    start_date: date
    end_date: date
    phase: str | None
    planned_load: float
    workouts: tuple[
        PlanWorkoutData,
        ...,
    ]


@dataclass(frozen=True)
class CompletePlanData:
    """
    Complete persistent training plan for presentation.
    """

    plan_id: str
    start_date: date | None
    end_date: date | None
    reference_day: date

    weeks: tuple[
        PlanWeekData,
        ...,
    ]
    progression: tuple[
        PlanProgressionPointData,
        ...,
    ]