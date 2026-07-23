"""
PerformanceLab

Base Strategy

Develops general aerobic fitness, consistency and technical
quality without targeting a specific competition.
"""

from performancelab.coaching.context import CoachContext
from performancelab.coaching.strategy import (
    CoachStrategy,
    StrategyPlan,
)


class BaseStrategy(CoachStrategy):

    name = "BaseStrategy"

    phase = "Base"

    # ======================================================

    def build(
        self,
        context: CoachContext,
    ) -> StrategyPlan:

        objectives = [
            "Develop general aerobic fitness.",
            "Improve training consistency.",
            "Build tolerance for future training load.",
        ]

        guidelines = [
            (
                "Keep most sessions at an easy, "
                "conversational intensity."
            ),
            (
                "Include one longer aerobic session "
                "during the week."
            ),
            (
                "Avoid placing demanding sessions on "
                "consecutive days."
            ),
        ]

        warnings = []

        target_sessions = 5

        if not self._has_training_history(context):

            target_sessions = 3

            guidelines.append(
                "Use short introductory sessions while "
                "establishing training consistency."
            )

            warnings.append(
                "Limited training history available."
            )

        if (
            context.average_rpe is not None
            and context.average_rpe >= 8
        ):
            target_sessions = max(
                3,
                target_sessions - 1,
            )

            warnings.append(
                "Recent perceived effort is high."
            )

        return StrategyPlan(

            strategy=self.name,

            phase=self.phase,

            volume_factor=1.00,

            target_sessions=target_sessions,

            intensity_sessions=1,

            long_sessions=1,

            recovery_days=2,

            objectives=tuple(objectives),

            guidelines=tuple(guidelines),

            warnings=tuple(warnings),
        )