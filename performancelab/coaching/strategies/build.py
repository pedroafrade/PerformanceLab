"""
PerformanceLab

Build Strategy

Progressively develops fitness and training load while
maintaining sufficient recovery.
"""

from performancelab.coaching.context import CoachContext
from performancelab.coaching.strategy import (
    CoachStrategy,
    StrategyPlan,
)


class BuildStrategy(CoachStrategy):

    name = "BuildStrategy"
    phase = "Build"

    # ======================================================

    def build(
        self,
        context: CoachContext,
    ) -> StrategyPlan:

        objectives = [
            "Increase sustainable training load.",
            "Develop aerobic endurance.",
            "Introduce controlled intensity.",
        ]

        guidelines = [
            (
                "Increase weekly volume gradually rather "
                "than through a single large session."
            ),
            (
                "Separate demanding sessions with easy "
                "training or recovery."
            ),
            "Maintain one longer endurance session.",
            "Keep easy sessions genuinely easy.",
        ]

        warnings: list[str] = []

        volume_factor = 1.08
        target_sessions = 6
        intensity_sessions = 2
        focus = "threshold"

        if context.tsb < -10:
            volume_factor = 1.00
            intensity_sessions = 1
            focus = "aerobic endurance"

            warnings.append(
                "Fatigue is elevated; avoid increasing "
                "both volume and intensity."
            )

        if (
            context.average_rpe is not None
            and context.average_rpe >= 8
        ):
            volume_factor = min(
                volume_factor,
                1.00,
            )
            intensity_sessions = 1
            focus = "aerobic endurance"

            warnings.append(
                "Recent perceived effort is high."
            )

        event_name = self._event_name(context)

        if event_name is not None:
            objectives.append(
                f"Prepare progressively for {event_name}."
            )

        return StrategyPlan(
            strategy=self.name,
            phase=self.phase,

            volume_factor=volume_factor,

            target_sessions=target_sessions,
            intensity_sessions=intensity_sessions,
            long_sessions=1,
            recovery_days=1,

            focus=focus,

            target_weekly_minutes=420,
            target_weekly_load=500.0 * volume_factor,
            long_session_minutes=120,

            objectives=tuple(objectives),
            guidelines=tuple(guidelines),
            warnings=tuple(warnings),
        )