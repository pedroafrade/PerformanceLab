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


EARLY_TAPER_MIN_DAYS = 8
EARLY_TAPER_MAX_DAYS = 14
EARLY_TAPER_LONG_MINUTES = 75
EARLY_TAPER_EVENT_ELEVATION_RATIO = 0.45


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

        elevation_demand = (
            self._event_elevation_demand(
                context
            )
        )

        key_session_focus = (
            self._key_session_focus(
                event_sport=event_sport,
            )
        )

        long_session_minutes = None
        long_session_elevation_gain = None

        if self._uses_reduced_trail_long_session(
            context=context,
            event_sport=event_sport,
        ):
            long_sessions = 1
            long_session_minutes = (
                EARLY_TAPER_LONG_MINUTES
            )
            long_session_elevation_gain = (
                self._reduced_trail_elevation_target(
                    context
                )
            )

            guidelines.append(
                (
                    "Retain one reduced trail endurance "
                    "session early in the taper."
                )
            )

        should_reduce_volume = getattr(
            context,
            "should_reduce_volume",
            context.tsb < -10,
        )

        if should_reduce_volume:
            volume_factor = 0.50
            intensity_sessions = 0
            long_sessions = 0
            long_session_minutes = None
            long_session_elevation_gain = None
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
            long_sessions = 0
            long_session_minutes = None
            long_session_elevation_gain = None
            recovery_days = max(
                recovery_days,
                4,
            )
            focus = "fatigue reduction"

            warnings.append(
                "Recent perceived effort is high."
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

        typical_weekly_minutes = getattr(
            training_reference,
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

        if long_session_minutes is not None:
            target_weekly_minutes = max(
                target_weekly_minutes,
                long_session_minutes,
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

            key_session_focus=(
                key_session_focus
            ),
            secondary_focus="race readiness",

            recovery_priority="high",

            race_specificity=0.95,

            elevation_demand=elevation_demand,

            target_weekly_minutes=(
                target_weekly_minutes
            ),
            target_weekly_load=(
                350.0 * volume_factor
            ),
            long_session_minutes=(
                long_session_minutes
            ),
            long_session_elevation_gain=(
                long_session_elevation_gain
            ),

            objectives=tuple(objectives),
            guidelines=tuple(guidelines),
            warnings=tuple(warnings),
        )

    # ======================================================

    @staticmethod
    def _uses_reduced_trail_long_session(
        *,
        context: CoachContext,
        event_sport: str | None,
    ) -> bool:
        """
        Keeps one reduced specific endurance session during
        the first taper week for a trail primary event.
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

        return (
            is_trail
            and isinstance(
                days_until_event,
                int,
            )
            and not isinstance(
                days_until_event,
                bool,
            )
            and EARLY_TAPER_MIN_DAYS
            <= days_until_event
            <= EARLY_TAPER_MAX_DAYS
        )

    # ======================================================

    @classmethod
    def _reduced_trail_elevation_target(
        cls,
        context: CoachContext,
    ) -> int | None:
        """
        Uses a reduced proportion of event elevation to retain
        trail specificity without reproducing peak load.
        """

        event_entry = getattr(
            context,
            "phase_event",
            None,
        )

        event = getattr(
            event_entry,
            "event",
            None,
        )

        event_elevation_gain = getattr(
            event,
            "elevation_gain",
            None,
        )

        if (
            not isinstance(
                event_elevation_gain,
                (int, float),
            )
            or isinstance(
                event_elevation_gain,
                bool,
            )
            or event_elevation_gain <= 0
        ):
            return None

        target = (
            float(event_elevation_gain)
            * EARLY_TAPER_EVENT_ELEVATION_RATIO
        )

        return cls._round_elevation_to_twenty_five(
            target
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
    def _round_elevation_to_twenty_five(
        elevation_gain: float,
    ) -> int:
        """
        Rounds elevation to a practical twenty-five-metre
        target.
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
        Rounds taper volume to a practical five-minute
        increment.
        """

        return int(
            round(minutes / 5) * 5
        )