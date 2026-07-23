"""
PerformanceLab

Coaching Strategy

Base abstractions for weekly coaching strategies.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .context import CoachContext


@dataclass(frozen=True)
class StrategyPlan:
    """
    Describes the intended structure of a training week.

    This object does not contain concrete PlannedWorkout
    instances. A future WorkoutGenerator will convert this
    strategy plan into scheduled workouts.
    """

    strategy: str

    phase: str

    volume_factor: float

    target_sessions: int

    intensity_sessions: int

    long_sessions: int

    recovery_days: int

    objectives: tuple[str, ...] = field(
        default_factory=tuple,
    )

    guidelines: tuple[str, ...] = field(
        default_factory=tuple,
    )

    warnings: tuple[str, ...] = field(
        default_factory=tuple,
    )

    # ======================================================

    def __post_init__(self):

        if self.volume_factor < 0:

            raise ValueError(
                "volume_factor cannot be negative"
            )

        if self.target_sessions < 0:

            raise ValueError(
                "target_sessions cannot be negative"
            )

        if self.intensity_sessions < 0:

            raise ValueError(
                "intensity_sessions cannot be negative"
            )

        if self.long_sessions < 0:

            raise ValueError(
                "long_sessions cannot be negative"
            )

        if self.recovery_days < 0:

            raise ValueError(
                "recovery_days cannot be negative"
            )

        if self.intensity_sessions > self.target_sessions:

            raise ValueError(
                "intensity_sessions cannot exceed "
                "target_sessions"
            )

        if self.long_sessions > self.target_sessions:

            raise ValueError(
                "long_sessions cannot exceed "
                "target_sessions"
            )


class CoachStrategy(ABC):
    """
    Base class for all coaching strategies.
    """

    name = "CoachStrategy"

    phase = "Unknown"

    # ======================================================

    @abstractmethod
    def build(
        self,
        context: CoachContext,
    ) -> StrategyPlan:
        """
        Builds the strategic description of the next week.
        """

        raise NotImplementedError

    # ======================================================

    @staticmethod
    def _has_training_history(
        context: CoachContext,
    ) -> bool:
        """
        Returns whether the athlete has recorded sports.

        This is intentionally conservative until the context
        includes a dedicated workout count.
        """

        return bool(context.sports)

    # ======================================================

    @staticmethod
    def _event_name(
        context: CoachContext,
    ) -> str | None:

        if context.next_event is None:

            return None

        event = getattr(
            context.next_event,
            "event",
            None,
        )

        if event is None:

            return None

        return getattr(
            event,
            "name",
            None,
        )

    # ======================================================

    @staticmethod
    def _event_priority(
        context: CoachContext,
    ) -> str | None:

        if context.next_event is None:

            return None

        priority = getattr(
            context.next_event,
            "priority",
            None,
        )

        if priority is None:

            return None

        return str(priority).upper()

    # ======================================================

    def __repr__(self):

        return (
            f"{self.__class__.__name__}("
            f"phase='{self.phase}')"
        )