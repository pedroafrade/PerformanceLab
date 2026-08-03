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