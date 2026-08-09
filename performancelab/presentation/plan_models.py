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
    is_race: bool
    status: str
    prescription_summary: str | None
    structure: tuple[str, ...]

@dataclass(frozen=True)
class PlanChartPointData:
    """
    One session-level point prepared for the plan chart.
    """

    day: date
    title: str
    phase: str | None
    planned_load: float | None
    distance: float | None
    elevation_gain: float | None
    duration: timedelta | None
    intensity: str | None
    is_race: bool
    status: str


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
class PlanPhaseData:
    """
    One continuous phase in the complete plan timeline.
    """

    name: str
    start_date: date
    end_date: date
    is_current: bool


@dataclass(frozen=True)
class PlanCurrentPhaseData:
    """
    Current training phase prepared for presentation.
    """

    name: str
    objective: str
    start_date: date
    end_date: date
    weeks_remaining: int
    sessions_remaining: int
    planned_load_remaining: float
    longest_session_minutes: int

@dataclass(frozen=True)
class PlanAdaptationData:
    """
    Presentation-ready before/after plan adaptation.
    """

    reconciled_on: date
    workout_day: date
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
    chart_points: tuple[
        PlanChartPointData,
        ...,
    ]
    progression: tuple[
        PlanProgressionPointData,
        ...,
    ]
    phases: tuple[
        PlanPhaseData,
        ...,
    ]
    current_phase: (
        PlanCurrentPhaseData
        | None
    )

    target_event_title: str | None = None
    target_event_date: date | None = None

    latest_adaptation: (
        PlanAdaptationData
        | None
    ) = None