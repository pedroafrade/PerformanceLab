"""
PerformanceLab

Activity presentation models.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta


@dataclass(frozen=True)
class ActivityListItemData:
    """
    Presentation-ready summary of one completed activity.
    """

    workout_id: str
    workout_date: date | datetime | None
    sport: str
    title: str
    distance: float | None
    duration: timedelta | None
    elevation_gain: float | None
    rpe: float | None

    outcome_status: str | None = None
    planned_title: str | None = None
    planned_load: float | None = None
    completed_load: float | None = None
    load_difference: float | None = None


@dataclass(frozen=True)
class ActivityFilters:
    """
    Immutable filters applied to completed activities.
    """

    query: str = ""
    sport: str | None = None
    start_date: date | None = None
    end_date: date | None = None