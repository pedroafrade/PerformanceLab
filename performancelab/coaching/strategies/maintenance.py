"""
PerformanceLab

Maintenance Strategy

Preserves current fitness with stable training volume,
controlled intensity, and sufficient recovery.
"""

from performancelab.coaching.context import CoachContext
from performancelab.coaching.strategy import (
    CoachStrategy,
    StrategyPlan,
)


class MaintenanceStrategy(CoachStrategy):

    name = "MaintenanceStrategy"
    phase = "Maintenance"

    # ======================================================

    def build(
        self,
        context: CoachContext,
    ) -> StrategyPlan:

        objectives = [
            "Maintain current aerobic fitness.",
            "Preserve training consistency.",
            "Balance quality training with recovery.",
        ]

        guidelines = [
            "Keep weekly training volume stable.",
            "Include controlled intensity without progression.",
            "Maintain one longer aerobic session.",
            "Avoid unnecessary increases in training load.",
        ]

        warnings: list[str] = []

        volume_factor = 1.00
        target_sessions = 5
        intensity_sessions = 1
        long_sessions = 1
        recovery_days = 2
        focus = "fitness maintenance"

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

        if should_reduce_volume:
            volume_factor = 0.90
            intensity_sessions = 0
            recovery_days = 3
            focus = "aerobic maintenance"

            warnings.append(
                "Fatigue is elevated; reduce training stress "
                "while maintaining consistency."
            )

        if (
            context.average_rpe is not None
            and context.average_rpe >= 8
        ):
            volume_factor = min(
                volume_factor,
                0.90,
            )
            intensity_sessions = 0
            recovery_days = max(
                recovery_days,
                3,
            )
            focus = "aerobic maintenance"

            warnings.append(
                "Recent perceived effort is high."
            )

        event_name = self._event_name(
            context
        )

        if event_name is not None:
            objectives.append(
                f"Maintain readiness for {event_name}."
            )

        recovery_priority = (
            "high"
            if (
                should_reduce_volume
                or (
                    context.average_rpe
                    is not None
                    and context.average_rpe
                    >= 8
                )
            )
            else "normal"
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

            # Keep the single maintenance quality session explicit and
            # controlled instead of falling back to a generic Quality Run.
            key_session_focus="tempo",
            secondary_focus="aerobic endurance",

            recovery_priority=(
                recovery_priority
            ),

            race_specificity=0.40,

            target_weekly_minutes=target_weekly_minutes,
            target_weekly_load=(
                400.0
                * volume_factor
            ),
            long_session_minutes=long_session_minutes,

            objectives=tuple(
                objectives
            ),
            guidelines=tuple(
                guidelines
            ),
            warnings=tuple(
                warnings
            ),
        )
