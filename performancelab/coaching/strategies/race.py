"""
PerformanceLab

Race Strategy

Minimises training stress during race week while preserving
readiness and supporting competition performance.
"""

from performancelab.coaching.context import CoachContext
from performancelab.coaching.strategy import (
    CoachStrategy,
    StrategyPlan,
)


class RaceStrategy(CoachStrategy):

    name = "RaceStrategy"
    phase = "Race"

    # ======================================================

    def build(
        self,
        context: CoachContext,
    ) -> StrategyPlan:

        objectives = [
            "Arrive at competition rested and prepared.",
            "Preserve physical and mental readiness.",
            "Execute the planned race strategy.",
        ]

        guidelines = [
            "Keep all non-race training short and easy.",
            "Avoid introducing new training stress.",
            "Prioritise sleep, hydration, and nutrition.",
            "Treat the race as the primary weekly load.",
        ]

        warnings: list[str] = []

        volume_factor = 0.40
        target_sessions = 3
        intensity_sessions = 0
        long_sessions = 0
        recovery_days = 4
        focus = "competition"

        if context.tsb < -10:
            volume_factor = 0.30
            target_sessions = 2
            recovery_days = 5
            focus = "race recovery and readiness"

            warnings.append(
                "Fatigue is elevated during race week; "
                "remove all unnecessary training stress."
            )

        if (
            context.average_rpe is not None
            and context.average_rpe >= 8
        ):
            volume_factor = min(
                volume_factor,
                0.30,
            )
            target_sessions = min(
                target_sessions,
                2,
            )
            recovery_days = max(
                recovery_days,
                5,
            )
            focus = "race recovery and readiness"

            warnings.append(
                "Recent perceived effort is high."
            )

        event_name = self._event_name(context)

        if event_name is not None:
            objectives.append(
                f"Perform effectively at {event_name}."
            )

        return StrategyPlan(
            strategy=self.name,
            phase=self.phase,

            volume_factor=volume_factor,

            target_sessions=target_sessions,
            intensity_sessions=intensity_sessions,
            long_sessions=long_sessions,
            recovery_days=recovery_days,

            focus=focus,

            target_weekly_minutes=150,
            target_weekly_load=250.0 * volume_factor,
            long_session_minutes=None,

            objectives=tuple(objectives),
            guidelines=tuple(guidelines),
            warnings=tuple(warnings),
        )