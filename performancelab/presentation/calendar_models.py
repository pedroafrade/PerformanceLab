"""
PerformanceLab

Calendar presentation models.
"""

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class CalendarItemData:
    """
    One presentation-ready calendar item.
    """

    kind: str
    title: str
    sport: str | None

    entity_id: str | None = None
    status: str | None = None
    priority: str | None = None
    duration: timedelta | None = None
    summary: str | None = None


@dataclass(frozen=True)
class CalendarDayData:
    """
    Presentation-ready calendar day.
    """

    day: date
    is_current_month: bool
    is_today: bool
    phase: str | None

    items: tuple[
        CalendarItemData,
        ...,
    ] = ()

    phase_day_number: int | None = None
    phase_total_days: int | None = None
    is_rest_day: bool = False


@dataclass(frozen=True)
class CalendarUpcomingEventData:
    """
    One factual event within the upcoming event window.
    """

    event_id: str
    name: str
    event_date: date

    sport: str | None
    priority: str | None

    distance: float | None = None
    elevation_gain: float | None = None


@dataclass(frozen=True)
class CalendarMonthData:
    """
    Complete presentation-ready calendar month.
    """

    year: int
    month: int

    weeks: tuple[
        tuple[
            CalendarDayData,
            ...,
        ],
        ...,
    ]

    selected_day: (
        CalendarDayData
        | None
    ) = None

    upcoming_events: tuple[
        CalendarUpcomingEventData,
        ...,
    ] = ()