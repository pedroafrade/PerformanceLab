"""
PerformanceLab

Coaching Strategy

Base abstractions for weekly coaching strategies.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from numbers import Real

from .context import CoachContext

LONG_ELEVATION_EVENT_RATIO = 0.65
LONG_ELEVATION_PROGRESSION_WEEKS = 8
LONG_ELEVATION_TARGET_STEPS = 4
MAX_WEEKLY_ELEVATION_INCREASE = 100
ELEVATION_INCREMENT = 25

@dataclass(frozen=True)
class StrategyPlan:
    """
    Describes the strategic targets for one training week.

    It defines what the week should achieve, but does not contain
    concrete scheduled workouts.
    """

    strategy: str
    phase: str

    volume_factor: float

    target_sessions: int
    intensity_sessions: int
    long_sessions: int
    recovery_days: int

    # More concrete weekly targets
    focus: str | None = None

    key_session_focus: str | None = None
    secondary_focus: str | None = None

    recovery_priority: str = "normal"
    race_specificity: float = 0.0
    elevation_demand: str | None = None

    target_weekly_minutes: int | None = None
    target_weekly_load: float | None = None
    long_session_minutes: int | None = None
    long_session_elevation_gain: int | None = None

    objectives: tuple[str, ...] = field(
        default_factory=tuple,
    )
    guidelines: tuple[str, ...] = field(
        default_factory=tuple,
    )
    warnings: tuple[str, ...] = field(
        default_factory=tuple,
    )

    def __post_init__(self) -> None:
        self._validate_text(
            self.strategy,
            field="strategy",
        )
        self._validate_text(
            self.phase,
            field="phase",
        )

        if self.focus is not None:
            self._validate_text(
                self.focus,
                field="focus",
            )

        if self.key_session_focus is not None:
            self._validate_text(
                self.key_session_focus,
                field="key_session_focus",
            )

        if self.secondary_focus is not None:
            self._validate_text(
                self.secondary_focus,
                field="secondary_focus",
            )

        self._validate_recovery_priority(
            self.recovery_priority
        )

        self._validate_ratio(
            self.race_specificity,
            field="race_specificity",
        )

        self._validate_elevation_demand(
            self.elevation_demand
        )

        self._validate_non_negative_number(
            self.volume_factor,
            field="volume_factor",
        )

        self._validate_non_negative_integer(
            self.target_sessions,
            field="target_sessions",
        )
        self._validate_non_negative_integer(
            self.intensity_sessions,
            field="intensity_sessions",
        )
        self._validate_non_negative_integer(
            self.long_sessions,
            field="long_sessions",
        )
        self._validate_non_negative_integer(
            self.recovery_days,
            field="recovery_days",
        )

        self._validate_optional_non_negative_integer(
            self.target_weekly_minutes,
            field="target_weekly_minutes",
        )
        self._validate_optional_non_negative_integer(
            self.long_session_minutes,
            field="long_session_minutes",
        )
        self._validate_optional_non_negative_integer(
            self.long_session_elevation_gain,
            field="long_session_elevation_gain",
        )
        self._validate_optional_non_negative_number(
            self.target_weekly_load,
            field="target_weekly_load",
        )

        if self.target_sessions > 7:
            raise ValueError(
                "target_sessions cannot exceed 7"
            )

        if self.recovery_days > 7:
            raise ValueError(
                "recovery_days cannot exceed 7"
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

        if (
            self.long_sessions == 0
            and self.long_session_minutes is not None
        ):
            raise ValueError(
                "long_session_minutes requires at least "
                "one long session"
            )
        if (
            self.long_sessions == 0
            and (
                self.long_session_elevation_gain
                is not None
            )
        ):
            raise ValueError(
                "long_session_elevation_gain requires "
                "at least one long session"
            )
        if (
            self.long_sessions > 0
            and self.long_session_minutes is not None
            and self.long_session_minutes == 0
        ):
            raise ValueError(
                "long_session_minutes must be greater than "
                "zero when long sessions are planned"
            )

        if (
            self.target_weekly_minutes is not None
            and self.long_session_minutes is not None
            and self.long_session_minutes
            > self.target_weekly_minutes
        ):
            raise ValueError(
                "long_session_minutes cannot exceed "
                "target_weekly_minutes"
            )

        self._validate_string_tuple(
            self.objectives,
            field="objectives",
        )
        self._validate_string_tuple(
            self.guidelines,
            field="guidelines",
        )
        self._validate_string_tuple(
            self.warnings,
            field="warnings",
        )

    @property
    def easy_sessions(self) -> int:
        """
        Returns the number of sessions not explicitly assigned
        to intensity or long-session work.

        This assumes intensity and long-session targets describe
        distinct sessions.
        """

        return max(
            0,
            self.target_sessions
            - self.intensity_sessions
            - self.long_sessions,
        )

    @property
    def training_days(self) -> int:
        """Number of planned training days."""

        return self.target_sessions

    @property
    def rest_days(self) -> int:
        """
        Number of days without a planned training session.

        Recovery days may be complete rest or active recovery,
        depending on the structure generator.
        """

        return 7 - self.target_sessions

    @property
    def has_intensity(self) -> bool:
        return self.intensity_sessions > 0

    @property
    def has_long_session(self) -> bool:
        return self.long_sessions > 0

    @property
    def has_key_session_focus(self) -> bool:

        return self.key_session_focus is not None


    @property
    def is_race_specific(self) -> bool:

        return self.race_specificity > 0

    @staticmethod
    def _validate_text(
        value: str,
        *,
        field: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                f"{field} must be a string"
            )

        if not value.strip():
            raise ValueError(
                f"{field} cannot be empty"
            )

    @staticmethod
    def _validate_non_negative_integer(
        value: int,
        *,
        field: str,
    ) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(
                f"{field} must be an integer"
            )

        if value < 0:
            raise ValueError(
                f"{field} cannot be negative"
            )

    @classmethod
    def _validate_optional_non_negative_integer(
        cls,
        value: int | None,
        *,
        field: str,
    ) -> None:
        if value is None:
            return

        cls._validate_non_negative_integer(
            value,
            field=field,
        )

    @staticmethod
    def _validate_non_negative_number(
        value: float,
        *,
        field: str,
    ) -> None:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError(
                f"{field} must be a number"
            )

        if value < 0:
            raise ValueError(
                f"{field} cannot be negative"
            )

    @classmethod
    def _validate_optional_non_negative_number(
        cls,
        value: float | None,
        *,
        field: str,
    ) -> None:
        if value is None:
            return

        cls._validate_non_negative_number(
            value,
            field=field,
        )

    @classmethod
    def _validate_ratio(
        cls,
        value: float,
        *,
        field: str,
    ) -> None:

        cls._validate_non_negative_number(
            value,
            field=field,
        )

        if value > 1:
            raise ValueError(
                f"{field} must be between 0 and 1"
            )

    @staticmethod
    def _validate_recovery_priority(
        value: str,
    ) -> None:

        if not isinstance(value, str):
            raise TypeError(
                "recovery_priority must be a string"
            )

        allowed = {
            "low",
            "normal",
            "high",
        }

        if value not in allowed:
            raise ValueError(
                "recovery_priority must be one of: "
                "low, normal, high"
            )

    @staticmethod
    def _validate_elevation_demand(
        value: str | None,
    ) -> None:

        if value is None:
            return

        if not isinstance(value, str):
            raise TypeError(
                "elevation_demand must be a string"
            )

        allowed = {
            "flat",
            "rolling",
            "hilly",
            "mountainous",
        }

        if value not in allowed:
            raise ValueError(
                "elevation_demand must be one of: "
                "flat, rolling, hilly, mountainous"
            )

    @staticmethod
    def _validate_string_tuple(
        value: tuple[str, ...],
        *,
        field: str,
    ) -> None:
        if not isinstance(value, tuple):
            raise TypeError(
                f"{field} must be a tuple"
            )

        if any(
            not isinstance(item, str)
            or not item.strip()
            for item in value
        ):
            raise ValueError(
                f"{field} must contain non-empty strings"
            )


class CoachStrategy(ABC):
    """
    Base class for all coaching strategies.
    """

    name = "CoachStrategy"
    phase = "Unknown"

    @abstractmethod
    def build(
        self,
        context: CoachContext,
    ) -> StrategyPlan:
        """
        Builds the strategic description of the next week.
        """

        raise NotImplementedError

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

    @staticmethod
    def _event_name(
        context: CoachContext,
    ) -> str | None:

        target_event = (
            getattr(
                context,
                "phase_event",
                None,
            )
            or getattr(
                context,
                "primary_event",
                None,
            )
            or getattr(
                context,
                "next_event",
                None,
            )
        )

        if target_event is None:
            return None

        event = getattr(
            target_event,
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

    @staticmethod
    def _event_sport(
        context: CoachContext,
    ) -> str | None:

        target_event = (
            getattr(
                context,
                "phase_event",
                None,
            )
            or getattr(
                context,
                "primary_event",
                None,
            )
            or getattr(
                context,
                "next_event",
                None,
            )
        )

        if target_event is None:
            return None

        event = getattr(
            target_event,
            "event",
            None,
        )

        if event is None:
            return None

        sport = getattr(
            event,
            "sport",
            None,
        )

        if not isinstance(sport, str):
            return None

        sport = sport.strip()

        return sport or None

    @staticmethod
    def _event_elevation_demand(
        context: CoachContext,
    ) -> str | None:

        target_event = (
            getattr(
                context,
                "phase_event",
                None,
            )
            or getattr(
                context,
                "primary_event",
                None,
            )
            or getattr(
                context,
                "next_event",
                None,
            )
        )

        event = getattr(
            target_event,
            "event",
            None,
        )

        return getattr(
            event,
            "elevation_demand",
            None,
        )
    
    # ======================================================

    @staticmethod
    def _event_elevation_gain(
        context: CoachContext,
    ) -> float | None:
        """
        Returns the elevation gain of the event that
        currently determines the training phase.
        """

        target_event = (
            getattr(
                context,
                "phase_event",
                None,
            )
            or getattr(
                context,
                "primary_event",
                None,
            )
            or getattr(
                context,
                "next_event",
                None,
            )
        )

        event = getattr(
            target_event,
            "event",
            None,
        )

        elevation_gain = getattr(
            event,
            "elevation_gain",
            None,
        )

        if (
            not isinstance(
                elevation_gain,
                (int, float),
            )
            or isinstance(
                elevation_gain,
                bool,
            )
            or elevation_gain <= 0
        ):
            return None

        return float(
            elevation_gain
        )

    # ======================================================

    @staticmethod
    def _round_elevation(
        elevation_gain: float,
    ) -> int:
        """
        Rounds elevation to a practical 25-metre
        increment.
        """

        return int(
            (
                elevation_gain
                + ELEVATION_INCREMENT / 2
            )
            // ELEVATION_INCREMENT
            * ELEVATION_INCREMENT
        )

    # ======================================================

    @classmethod
    def _progressive_long_elevation_gain(
        cls,
        *,
        context: CoachContext,
        baseline_elevation_gain: float,
    ) -> int | None:
        """
        Progresses long-run elevation from the athlete's
        recent capacity towards part of the event demand.

        The progression is limited to 100 metres per week
        and never requires reproducing the full event D+.
        """

        if baseline_elevation_gain <= 0:
            return None

        baseline = cls._round_elevation(
            baseline_elevation_gain
        )

        event_elevation_gain = (
            cls._event_elevation_gain(
                context
            )
        )

        days_until_event = getattr(
            context,
            "days_until_phase_event",
            None,
        )

        if (
            event_elevation_gain is None
            or days_until_event is None
        ):
            return baseline

        event_target = cls._round_elevation(
            event_elevation_gain
            * LONG_ELEVATION_EVENT_RATIO
        )

        event_target = max(
            baseline,
            event_target,
        )

        if event_target <= baseline:
            return baseline

        required_increase = (
            event_target - baseline
        )

        calculated_step = cls._round_elevation(
            required_increase
            / LONG_ELEVATION_TARGET_STEPS
        )

        weekly_step = min(
            MAX_WEEKLY_ELEVATION_INCREASE,
            max(
                ELEVATION_INCREMENT,
                calculated_step,
            ),
        )

        weeks_until_event = max(
            0,
            days_until_event // 7,
        )

        completed_weeks = max(
            0,
            LONG_ELEVATION_PROGRESSION_WEEKS
            - weeks_until_event,
        )

        progressive_target = (
            baseline
            + completed_weeks
            * weekly_step
        )

        return min(
            event_target,
            cls._round_elevation(
                progressive_target
            ),
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

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"phase={self.phase!r})"
        )