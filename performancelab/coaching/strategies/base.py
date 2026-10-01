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

        weekly_sessions = getattr(
            context,
            "weekly_sessions_reference",
            None,
        )
        weekly_minutes = getattr(
            context,
            "weekly_minutes_reference",
            None,
        )

        if weekly_sessions is not None:
            target_sessions = weekly_sessions
            intensity_sessions = min(
                intensity_sessions,
                max(0, target_sessions - 2),
            )
            long_sessions = min(long_sessions, target_sessions)
            recovery_days = max(recovery_days, 7 - target_sessions)

        should_reduce_volume = getattr(
            context,
            "should_reduce_volume",
            context.tsb < -10,
        )

        can_tolerate_intensity = getattr(
            context,
            "can_tolerate_intensity",
            context.tsb >= 0,
        )

        if should_reduce_volume:

            volume_factor = 0.80
            recovery_days = 3

            warnings.append(
                "Fatigue is elevated; prioritise recovery."
            )

        if not can_tolerate_intensity:

            intensity_sessions = 0

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

        target_weekly_minutes = (
            int(round((weekly_minutes * volume_factor) / 5.0) * 5)
            if weekly_minutes is not None
            else 360
        )
        long_session_minutes = min(90, target_weekly_minutes)

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
                if (
                    should_reduce_volume
                    or (
                        context.average_rpe is not None
                        and context.average_rpe >= 8
                    )
                )
                else "normal"
            ),

            race_specificity=0.00,

            target_weekly_minutes=target_weekly_minutes,
            target_weekly_load=400.0 * volume_factor,
            long_session_minutes=long_session_minutes,

            objectives=tuple(objectives),
            guidelines=tuple(guidelines),
            warnings=tuple(warnings),
        )
