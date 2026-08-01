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
        event_sport = self._event_sport(
            context
        )

        focus = self._key_session_focus(
            context=context,
            event_sport=event_sport,
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
        typical_long_elevation_gain = getattr(
            training_state,
            (
                "typical_running_long_session_"
                "elevation_gain"
            ),
            0.0,
        )

        elevation_demand = (
            self._event_elevation_demand(
                context
            )
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

        long_session_elevation_gain = None

        if (
            elevation_demand
            in {
                "rolling",
                "hilly",
                "mountainous",
            }
            and typical_long_elevation_gain > 0
        ):
            long_session_elevation_gain = (
                self._round_elevation_to_twenty_five(
                    typical_long_elevation_gain
                )
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

            elevation_demand=elevation_demand,

            target_weekly_minutes=target_weekly_minutes,
            target_weekly_load=500.0 * volume_factor,
            long_session_minutes=long_session_minutes,
            long_session_elevation_gain=(
                long_session_elevation_gain
            ),
            objectives=tuple(objectives),
            guidelines=tuple(guidelines),
            warnings=tuple(warnings),
        )

    # ======================================================
    @staticmethod
    def _key_session_focus(
        *,
        context: CoachContext,
        event_sport: str | None,
    ) -> str:
        """
        Rotates the demanding-session focus between training
        weeks while preserving event specificity.

        VO2max work is used less frequently than threshold
        and tempo work.
        """

        days_until_event = getattr(
            context,
            "days_until_phase_event",
            None,
        )

        is_trail = (
            event_sport is not None
            and "trail" in event_sport.lower()
        )

        if days_until_event is None:

            return (
                "hills"
                if is_trail
                else "threshold"
            )

        weeks_until_event = max(
            0,
            days_until_event // 7,
        )

        if is_trail:

            rotation = (
                "hills",
                "threshold",
                "tempo",
            )

        else:

            rotation = (
                "threshold",
                "tempo",
                "vo2max",
                "threshold",
            )

        return rotation[
            weeks_until_event
            % len(rotation)
        ]

    # ======================================================
    @staticmethod
    def _round_elevation_to_twenty_five(
        elevation_gain: float,
    ) -> int:
        """
        Rounds elevation gain to a practical
        twenty-five-metre increment.
        """

        return int(
            (
                elevation_gain
                + 12.5
            )
            // 25
            * 25
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