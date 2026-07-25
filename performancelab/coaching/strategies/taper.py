"""
PerformanceLab

Taper Strategy

Reduces training load before competition while preserving
enough intensity to maintain sharpness.
"""

from performancelab.coaching.context import CoachContext
from performancelab.coaching.strategy import (
    CoachStrategy,
    StrategyPlan,
)


class TaperStrategy(CoachStrategy):

    name = "TaperStrategy"
    phase = "Taper"

    # ======================================================

    def build(
        self,
        context: CoachContext,
    ) -> StrategyPlan:

        objectives = [
            "Reduce accumulated fatigue.",
            "Preserve race-specific sharpness.",
            "Improve readiness for competition.",
        ]

        guidelines = [
            "Reduce training volume substantially.",
            "Keep intensity brief and controlled.",
            "Avoid introducing new training stress.",
            "Prioritise recovery, sleep, and consistency.",
        ]

        warnings: list[str] = []

        volume_factor = 0.65
        target_sessions = 4
        intensity_sessions = 1
        long_sessions = 0
        recovery_days = 3
        focus = "race readiness"

        if context.tsb < -10:
            volume_factor = 0.50
            intensity_sessions = 0
            recovery_days = 4
            focus = "fatigue reduction"

            warnings.append(
                "Fatigue remains elevated; prioritise recovery "
                "over additional race-specific work."
            )

        if (
            context.average_rpe is not None
            and context.average_rpe >= 8
        ):
            volume_factor = min(
                volume_factor,
                0.50,
            )
            intensity_sessions = 0
            recovery_days = max(
                recovery_days,
                4,
            )
            focus = "fatigue reduction"

            warnings.append(
                "Recent perceived effort is high."
            )

        event_name = self._event_name(context)

        if event_name is not None:
            objectives.append(
                f"Arrive rested and prepared for {event_name}."
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

            key_session_focus=focus,
            secondary_focus="race readiness",

            recovery_priority="high",

            race_specificity=0.95,

            target_weekly_minutes=240,
            target_weekly_load=350.0 * volume_factor,
            long_session_minutes=None,

            objectives=tuple(objectives),
            guidelines=tuple(guidelines),
            warnings=tuple(warnings),
        )