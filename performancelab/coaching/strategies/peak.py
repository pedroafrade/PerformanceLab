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
        secondary_intensity_focus = (
            self._secondary_intensity_focus(
                key_session_focus=(
                    key_session_focus
                ),
                event_sport=event_sport,
            )
        )
        elevation_demand = (
            self._event_elevation_demand(
                context
            )
        )

        training_reference = getattr(
            context,
            "training_reference",
            None,
        )

        if training_reference is None:
            training_reference = getattr(
                context,
                "training_state",
                None,
            )

        typical_long_elevation_gain = getattr(
            training_reference,
            (
                "typical_running_long_session_"
                "elevation_gain"
            ),
            0.0,
        )

        # Use the same observed frequency as Build. A phase change is not
        # evidence that the athlete can suddenly sustain five sessions.
        typical_sessions = getattr(
            context,
            "weekly_sessions_reference",
            getattr(training_reference, "typical_weekly_sessions", 0.0),
        )
        if typical_sessions > 0:
            target_sessions = min(
                target_sessions, max(1, int(typical_sessions + 0.5))
            )
            long_sessions = min(long_sessions, target_sessions)
            intensity_sessions = min(
                intensity_sessions, max(0, target_sessions - 2)
            )
            recovery_days = max(recovery_days, 7 - target_sessions)

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

        if getattr(
            context,
            "should_reduce_volume",
            context.tsb < -10,
        ):
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

        if typical_sessions > 0:
            intensity_sessions = min(
                intensity_sessions, max(0, target_sessions - 2)
            )

        typical_minutes = getattr(
            context,
            "weekly_minutes_reference",
            None,
        )
        target_weekly_minutes = (
            int(round((typical_minutes * volume_factor) / 5.0) * 5)
            if typical_minutes is not None
            else 330
        )
        long_session_minutes = min(
            90,
            target_weekly_minutes,
        )

        if not getattr(
            context,
            "training_reference_is_declared",
            True,
        ):
            warnings.append(
                "Training history is limited; peak volume uses a "
                "conservative provisional baseline."
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
            secondary_intensity_focus=(
                secondary_intensity_focus
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

            target_weekly_minutes=target_weekly_minutes,
            target_weekly_load=450.0 * volume_factor,
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
    def _secondary_intensity_focus(
        *,
        key_session_focus: str,
        event_sport: str | None,
    ) -> str:
        """
        Selects a complementary second quality session
        instead of repeating the primary stimulus.
        """

        is_trail = (
            event_sport is not None
            and "trail"
            in event_sport.lower()
        )

        if is_trail:

            complements = {
                "hills": "threshold",
                "threshold": "tempo",
                "tempo": "hills",
                "vo2max": "threshold",
                "speed": "tempo",
            }

        else:

            complements = {
                "hills": "tempo",
                "threshold": "tempo",
                "tempo": "threshold",
                "vo2max": "threshold",
                "speed": "tempo",
            }

        return complements.get(
            key_session_focus,
            "tempo",
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
                "hills",
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
