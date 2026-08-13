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
        target_sessions = 3
        intensity_sessions = 1
        long_sessions = 0
        recovery_days = 4
        focus = "race readiness"
        event_sport = self._event_sport(
            context
        )

        key_session_focus = (
            self._key_session_focus(
                event_sport=event_sport,
            )
        )

        if getattr(
            context,
            "should_reduce_volume",
            context.tsb < -10,
        ):
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

        training_state = getattr(
            context,
            "training_state",
            None,
        )

        typical_weekly_minutes = getattr(
            training_state,
            "typical_weekly_minutes",
            0.0,
        )

        if typical_weekly_minutes > 0:

            target_weekly_minutes = (
                self._round_to_five(
                    typical_weekly_minutes
                    * volume_factor
                )
            )

        else:

            target_weekly_minutes = 240

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

            key_session_focus=(
                key_session_focus
            ),
            secondary_focus="race readiness",

            recovery_priority="high",

            race_specificity=0.95,

            target_weekly_minutes=(
                target_weekly_minutes
            ),
            target_weekly_load=350.0 * volume_factor,
            long_session_minutes=None,

            objectives=tuple(objectives),
            guidelines=tuple(guidelines),
            warnings=tuple(warnings),
        )

    # ======================================================
    @staticmethod
    def _key_session_focus(
        *,
        event_sport: str | None,
    ) -> str:
        """
        Selects a brief, controlled sharpening session
        appropriate to the event modality.
        """

        is_trail = (
            event_sport is not None
            and "trail" in event_sport.lower()
        )

        return (
            "tempo"
            if is_trail
            else "threshold"
        )

    # ======================================================
    
    @staticmethod
    def _round_to_five(
        minutes: float,
    ) -> int:
        """
        Rounds taper volume to a practical five-minute
        increment.
        """

        return int(
            round(minutes / 5) * 5
        )