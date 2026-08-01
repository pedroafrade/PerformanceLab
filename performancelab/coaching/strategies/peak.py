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
        event_sport = self._event_sport(
            context
        )

        key_session_focus = (
            self._key_session_focus(
                context=context,
                event_sport=event_sport,
            )
        )
        elevation_demand = (
            self._event_elevation_demand(
                context
            )
        )

        training_state = getattr(
            context,
            "training_state",
            None,
        )

        typical_long_elevation_gain = getattr(
            training_state,
            (
                "typical_running_long_session_"
                "elevation_gain"
            ),
            0.0,
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
                self._progressive_long_elevation_gain(
                    context=context,
                    baseline_elevation_gain=(
                        typical_long_elevation_gain
                    ),
                )
            )

        if context.tsb < -10:
            volume_factor = 0.80
            intensity_sessions = 1
            recovery_days = 3
            focus = "race-specific endurance"
            key_session_focus = "tempo"

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
            key_session_focus = "tempo"

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

            key_session_focus=(
                key_session_focus
            ),
            secondary_focus="race pace",

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

            race_specificity=0.80,

            elevation_demand=elevation_demand,

            target_weekly_minutes=330,
            target_weekly_load=450.0 * volume_factor,
            long_session_minutes=90,
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
        Selects a concrete race-specific session for the
        current Peak week.

        VO2max is used less frequently than threshold and
        tempo work. Trail plans retain climbing specificity.
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