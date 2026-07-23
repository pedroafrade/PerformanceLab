"""
PerformanceLab

Regeneration Strategy

Reduces training stress when accumulated fatigue is high,
allowing the athlete to restore readiness before resuming
normal progression.
"""

from performancelab.coaching.context import CoachContext
from performancelab.coaching.strategy import (
    CoachStrategy,
    StrategyPlan,
)


class RegenerationStrategy(CoachStrategy):

    name = "RegenerationStrategy"

    phase = "Regeneration"

    # ======================================================

    def build(
        self,
        context: CoachContext,
    ) -> StrategyPlan:

        objectives = [
            "Reduce accumulated fatigue.",
            "Restore readiness for future training.",
            "Maintain movement without creating new stress.",
        ]

        guidelines = [
            (
                "Use rest or short easy sessions during "
                "the first part of the week."
            ),
            (
                "Avoid threshold, interval and maximal "
                "strength sessions."
            ),
            (
                "Resume normal training only when recovery "
                "indicators improve."
            ),
            (
                "Prefer low-impact training when practical."
            ),
        ]

        warnings = [
            (
                "Regeneration takes priority over planned "
                "training progression."
            ),
        ]

        volume_factor = 0.60
        target_sessions = 4
        recovery_days = 3

        if context.tsb < -30:

            volume_factor = 0.40
            target_sessions = 3
            recovery_days = 4

            warnings.append(
                "Accumulated fatigue is very high."
            )

        if (
            context.average_rpe is not None
            and context.average_rpe >= 8
        ):

            volume_factor = min(
                volume_factor,
                0.50,
            )

            warnings.append(
                "Recent sessions have a high perceived effort."
            )

        if (
            context.days_until_event is not None
            and context.days_until_event <= 7
        ):

            warnings.append(
                "An event is approaching while fatigue "
                "remains elevated."
            )

        return StrategyPlan(

            strategy=self.name,

            phase=self.phase,

            volume_factor=volume_factor,

            target_sessions=target_sessions,

            intensity_sessions=0,

            long_sessions=0,

            recovery_days=recovery_days,

            objectives=tuple(objectives),

            guidelines=tuple(guidelines),

            warnings=tuple(warnings),
        )