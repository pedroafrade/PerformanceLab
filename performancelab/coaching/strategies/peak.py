"""
PerformanceLab

Peak Strategy

Sharpens race-specific fitness while slightly reducing
overall training volume.
"""

from performancelab.coaching.context import CoachContext
from performancelab.coaching.strategy import (
    CoachStrategy,
    StrategyPlan,
)


class PeakStrategy(CoachStrategy):

    name = "PeakStrategy"
    phase = "Peak"

    # ======================================================

    def build(
        self,
        context: CoachContext,
    ) -> StrategyPlan:

        objectives = [
            "Sharpen race-specific fitness.",
            "Preserve intensity while reducing excess volume.",
            "Improve readiness for peak performance.",
        ]

        guidelines = [
            "Prioritise quality over training volume.",
            "Keep demanding sessions controlled and specific.",
            "Maintain one reduced long endurance session.",
            "Allow sufficient recovery between key sessions.",
        ]

        warnings: list[str] = []

        volume_factor = 0.90
        target_sessions = 5
        intensity_sessions = 2
        long_sessions = 1
        recovery_days = 2
        focus = "race-specific intensity"

        if context.tsb < -10:
            volume_factor = 0.80
            intensity_sessions = 1
            recovery_days = 3
            focus = "race-specific endurance"

            warnings.append(
                "Fatigue is elevated; reduce training stress "
                "without removing all race-specific work."
            )

        if (
            context.average_rpe is not None
            and context.average_rpe >= 8
        ):
            volume_factor = min(
                volume_factor,
                0.80,
            )
            intensity_sessions = 1
            recovery_days = max(
                recovery_days,
                3,
            )
            focus = "race-specific endurance"

            warnings.append(
                "Recent perceived effort is high."
            )

        event_name = self._event_name(context)

        if event_name is not None:
            objectives.append(
                f"Sharpen readiness for {event_name}."
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

            target_weekly_minutes=330,
            target_weekly_load=450.0 * volume_factor,
            long_session_minutes=90,

            objectives=tuple(objectives),
            guidelines=tuple(guidelines),
            warnings=tuple(warnings),
        )