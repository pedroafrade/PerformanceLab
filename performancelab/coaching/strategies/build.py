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

        event_sport = self._event_sport(
            context
        )

        if (
            event_sport is not None
            and "trail" in event_sport.lower()
        ):
            focus = "hills"

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

        typical_weekly_sessions = getattr(
            training_state,
            "typical_weekly_sessions",
            0.0,
        )

        typical_long_minutes = getattr(
            training_state,
            "typical_running_long_session_minutes",
            0.0,
        )

        if typical_weekly_sessions > 0:

            target_sessions = max(
                1,
                min(
                    7,
                    int(
                        typical_weekly_sessions
                        + 0.5
                    ),
                ),
            )

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

        max_intensity_sessions = max(
            0,
            target_sessions - 2,
        )

        intensity_sessions = min(
            intensity_sessions,
            max_intensity_sessions,
        )

        if typical_weekly_minutes > 0:

            target_weekly_minutes = (
                self._round_to_five(
                    typical_weekly_minutes
                    * volume_factor
                )
            )

        else:

            target_weekly_minutes = 420

        if typical_long_minutes > 0:

            long_session_minutes = (
                self._round_to_five(
                    typical_long_minutes
                )
            )

            can_progress_long = getattr(
                training_state,
                "can_absorb_more_volume",
                context.tsb > -10,
            )

            if (
                volume_factor > 1.0
                and can_progress_long
            ):
                long_session_minutes += 5

        else:

            long_session_minutes = 120

        long_session_minutes = min(
            long_session_minutes,
            target_weekly_minutes,
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

            key_session_focus=focus,
            secondary_focus="aerobic endurance",

            recovery_priority=(
                "high"
                if (
                    context.tsb < -10
                    or (
                        context.average_rpe is not None
                        and context.average_rpe >= 8
                    )
                )
                else "normal"
            ),

            race_specificity=0.30,

            elevation_demand=(
                self._event_elevation_demand(
                    context
                )
            ),

            target_weekly_minutes=target_weekly_minutes,
            target_weekly_load=500.0 * volume_factor,
            long_session_minutes=long_session_minutes,

            objectives=tuple(objectives),
            guidelines=tuple(guidelines),
            warnings=tuple(warnings),
        )

    # ======================================================

    @staticmethod
    def _round_to_five(
        minutes: float,
    ) -> int:
        """
        Rounds a training duration to a practical
        five-minute increment.
        """

        return int(
            round(minutes / 5) * 5
        )