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
# Planning
# ======================================================


@dataclass(frozen=True)
class DashboardPlanningData:
    """
    Presentation-ready planning data.
    """

    next_goal: str | None
    days_to_goal: int | None

    next_event: str | None
    days_to_event: int | None


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