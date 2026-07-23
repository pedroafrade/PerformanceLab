"""
PerformanceLab

Coach

Main orchestration service for the coaching engine.
"""

from datetime import date

from performancelab.athlete import Athlete

from .analyzer import CoachAnalyzer
from .context import CoachContext
from .recommendation import CoachRecommendation
from .selector import StrategySelector


class Coach:
    """
    Builds a coaching recommendation for an athlete.

    Workflow:

    Athlete
        -> CoachContext
        -> CoachAnalyzer
        -> StrategySelector
        -> CoachStrategy
        -> StrategyPlan
        -> CoachRecommendation
    """

    # ======================================================

    def recommend(
        self,
        athlete: Athlete,
        today: date | None = None,
    ) -> CoachRecommendation:

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