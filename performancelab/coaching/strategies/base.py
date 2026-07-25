"""
PerformanceLab

Base Strategy

Establishes a consistent aerobic training routine and prepares
the athlete for future build phases.
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
            "Develop aerobic endurance.",
            "Build consistent training habits.",
            "Prepare for future training load.",
        ]

        guidelines = [
            (
                "Prioritise easy aerobic sessions."
            ),
            (
                "Increase training volume gradually."
            ),
            (
                "Include one longer endurance session."
            ),
            (
                "Avoid excessive high-intensity work."
            ),
        ]

        warnings = []

        volume_factor = 0.90
        target_sessions = 5
        intensity_sessions = 1
        long_sessions = 1
        recovery_days = 2

        focus = "aerobic endurance"

        if context.tsb < -10:

            volume_factor = 0.80
            recovery_days = 3

            warnings.append(
                "Fatigue is elevated; prioritise recovery."
            )

        if (
            context.average_rpe is not None
            and context.average_rpe >= 8
        ):

            volume_factor = min(
                volume_factor,
                0.80,
            )

            recovery_days = max(
                recovery_days,
                3,
            )

            warnings.append(
                "Recent perceived effort is high."
            )

        event_name = self._event_name(context)

        if event_name is not None:

            objectives.append(
                f"Build a strong aerobic foundation for {event_name}."
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
            secondary_focus="training consistency",

            recovery_priority=(
                "high"
                if context.tsb < -10
                or (
                    context.average_rpe is not None
                    and context.average_rpe >= 8
                )
                else "normal"
            ),

            race_specificity=0.00,

            target_weekly_minutes=360,
            target_weekly_load=400.0 * volume_factor,
            long_session_minutes=90,

            objectives=tuple(objectives),
            guidelines=tuple(guidelines),
            warnings=tuple(warnings),
        )