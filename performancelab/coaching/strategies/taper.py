"""
PerformanceLab

Taper Strategy

Reduces training volume while preserving selected intensity
before an upcoming event.
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

        days = context.days_until_event

        objectives = [
            "Reduce accumulated fatigue.",
            "Preserve fitness and movement quality.",
            "Arrive at the event physically and mentally fresh.",
        ]

        guidelines = [
            (
                "Reduce training volume while retaining "
                "small amounts of controlled intensity."
            ),
            (
                "Avoid introducing unfamiliar sessions, "
                "equipment or training methods."
            ),
            (
                "Prioritize sleep, recovery and consistent "
                "daily routines."
            ),
        ]

        warnings = []

        volume_factor = self._volume_factor(days)

        target_sessions = 5
        intensity_sessions = 1
        recovery_days = 2

        if days is not None and days <= 7:

            target_sessions = 4
            recovery_days = 3

            guidelines.append(
                "Keep the final demanding stimulus short "
                "and early in the week."
            )

        if days is not None and days <= 2:

            target_sessions = 2
            intensity_sessions = 0
            recovery_days = 5

            guidelines.append(
                "Only use very short activation sessions "
                "before the event."
            )

        priority = self._event_priority(context)

        if priority == "B":

            volume_factor = max(
                volume_factor,
                0.70,
            )

            warnings.append(
                "B-priority event: use a reduced taper "
                "rather than a full peak taper."
            )

        elif priority == "C":

            volume_factor = max(
                volume_factor,
                0.85,
            )

            target_sessions = max(
                target_sessions,
                5,
            )

            warnings.append(
                "C-priority event: treat the event as part "
                "of the training process."
            )

        event_name = self._event_name(context)

        if event_name is not None:

            objectives.append(
                f"Prepare to perform at {event_name}."
            )

        return StrategyPlan(

            strategy=self.name,

            phase=self.phase,

            volume_factor=volume_factor,

            target_sessions=target_sessions,

            intensity_sessions=intensity_sessions,

            long_sessions=0,

            recovery_days=recovery_days,

            objectives=tuple(objectives),

            guidelines=tuple(guidelines),

            warnings=tuple(warnings),
        )

    # ======================================================

    @staticmethod
    def _volume_factor(
        days_until_event: int | None,
    ) -> float:

        if days_until_event is None:

            return 0.75

        if days_until_event <= 2:

            return 0.25

        if days_until_event <= 7:

            return 0.50

        if days_until_event <= 14:

            return 0.65

        return 0.80