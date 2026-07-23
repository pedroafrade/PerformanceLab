"""
PerformanceLab

Coach

Public façade for coaching recommendations and weekly planning.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from performancelab.training.planning.planner import Planner
from performancelab.training.planning.weekly_plan import WeeklyPlan

from .analyzer import CoachAnalyzer
from ..training.config.availability import AthleteAvailability
from ..training.config.constraints import TrainingConstraints
from .context import CoachContext
from ..training.config.preferences import AthletePreferences
from .recommendation import CoachRecommendation
from .selector import StrategySelector

if TYPE_CHECKING:
    from performancelab.athlete import Athlete


class Coach:
    """
    Public façade for the coaching engine.

    ``recommend()`` builds a high-level recommendation.
    ``plan()`` delegates weekly-plan generation to ``Planner``.
    """

    def __init__(
        self,
        *,
        planner: Planner | None = None,
    ) -> None:
        self.planner = planner or Planner()

    def recommend(
        self,
        athlete: Athlete,
        today: date | None = None,
    ) -> CoachRecommendation:
        self._validate_optional_date(
            today,
            field="today",
        )

        context = CoachContext.from_athlete(
            athlete,
            today=today,
        )

        analysis = CoachAnalyzer(
            context,
        ).analyze()

        strategy = StrategySelector().select(
            analysis,
        )

        plan = strategy.build(
            context,
        )

        return CoachRecommendation(
            context=context,
            analysis=analysis,
            strategy=plan.strategy,
            summary=analysis.summary,
            warnings=analysis.warnings,
        )

    def plan(
        self,
        *,
        athlete: Athlete,
        week_start: date | None = None,
        today: date | None = None,
    ) -> WeeklyPlan:
        return self.planner.build(
            athlete=athlete,
            week_start=week_start,
            today=today,
        )
    
    @staticmethod
    def _validate_optional_date(
        value: date | None,
        *,
        field: str,
    ) -> None:
        if (
            value is not None
            and not isinstance(value, date)
        ):
            raise TypeError(
                f"{field} must be a date or None"
            )

    def __repr__(self) -> str:
        return (
            "Coach("
            f"planner={self.planner!r})"
        )