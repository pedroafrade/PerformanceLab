"""
PerformanceLab

Training Constraints

Represents hard rules that a generated training plan must
respect.
"""

from dataclasses import dataclass, field

from .availability import Weekday


@dataclass(frozen=True)
class TrainingConstraints:
    """
    Hard limits used during plan generation and review.

    Unlike preferences, constraints should not be violated
    by the automatic generator.
    """

    max_weekly_minutes: int | None = None

    max_session_minutes: int | None = None

    max_weekday_minutes: int | None = None

    max_weekend_minutes: int | None = None

    max_consecutive_training_days: int = 6

    max_intensity_sessions: int = 2

    max_long_sessions: int = 1

    max_sessions_per_day: int = 1

    minimum_recovery_days: int = 1

    no_intensity_days: tuple[Weekday, ...] = field(
        default_factory=tuple,
    )

    blocked_days: tuple[Weekday, ...] = field(
        default_factory=tuple,
    )

    allow_double_sessions: bool = False

    # ======================================================

    def __post_init__(self) -> None:

        self._validate_optional_non_negative(
            "max_weekly_minutes",
            self.max_weekly_minutes,
        )

        self._validate_optional_non_negative(
            "max_session_minutes",
            self.max_session_minutes,
        )

        self._validate_optional_non_negative(
            "max_weekday_minutes",
            self.max_weekday_minutes,
        )

        self._validate_optional_non_negative(
            "max_weekend_minutes",
            self.max_weekend_minutes,
        )

        self._validate_non_negative(
            "max_consecutive_training_days",
            self.max_consecutive_training_days,
        )

        self._validate_non_negative(
            "max_intensity_sessions",
            self.max_intensity_sessions,
        )

        self._validate_non_negative(
            "max_long_sessions",
            self.max_long_sessions,
        )

        self._validate_non_negative(
            "max_sessions_per_day",
            self.max_sessions_per_day,
        )

        self._validate_non_negative(
            "minimum_recovery_days",
            self.minimum_recovery_days,
        )

        if self.max_consecutive_training_days > 7:

            raise ValueError(
                "max_consecutive_training_days cannot "
                "exceed 7."
            )

        if self.minimum_recovery_days > 7:

            raise ValueError(
                "minimum_recovery_days cannot exceed 7."
            )

        if (
            not self.allow_double_sessions
            and self.max_sessions_per_day > 1
        ):

            raise ValueError(
                "max_sessions_per_day cannot exceed 1 when "
                "double sessions are disabled."
            )

        no_intensity_days = self._normalize_days(
            self.no_intensity_days,
        )

        blocked_days = self._normalize_days(
            self.blocked_days,
        )

        object.__setattr__(
            self,
            "no_intensity_days",
            no_intensity_days,
        )

        object.__setattr__(
            self,
            "blocked_days",
            blocked_days,
        )

    # ======================================================

    @property
    def max_weekly_hours(self) -> float | None:
        """
        Returns the weekly duration limit in hours.
        """

        if self.max_weekly_minutes is None:

            return None

        return self.max_weekly_minutes / 60

    # ======================================================

    def is_blocked(
        self,
        day: Weekday,
    ) -> bool:
        """
        Returns whether all training is blocked on a day.
        """

        return (
            Weekday(day)
            in self.blocked_days
        )

    # ======================================================

    def allows_intensity(
        self,
        day: Weekday,
    ) -> bool:
        """
        Returns whether an intensity session may be placed
        on the given weekday.
        """

        normalized_day = Weekday(day)

        return (
            normalized_day
            not in self.blocked_days
            and normalized_day
            not in self.no_intensity_days
        )

    # ======================================================

    def duration_limit_for(
        self,
        day: Weekday,
    ) -> int | None:
        """
        Returns the most restrictive applicable duration
        limit for a weekday.
        """

        normalized_day = Weekday(day)

        limits = [
            limit
            for limit in (
                self.max_session_minutes,
                self._day_type_limit(
                    normalized_day,
                ),
            )
            if limit is not None
        ]

        if not limits:

            return None

        return min(limits)

    # ======================================================

    def allows_duration(
        self,
        day: Weekday,
        duration_minutes: int,
    ) -> bool:
        """
        Returns whether a duration complies with the
        configured session and weekday limits.
        """

        if duration_minutes < 0:

            raise ValueError(
                "duration_minutes cannot be negative."
            )

        if self.is_blocked(day):

            return False

        limit = self.duration_limit_for(
            day,
        )

        return (
            limit is None
            or duration_minutes <= limit
        )

    # ======================================================

    def _day_type_limit(
        self,
        day: Weekday,
    ) -> int | None:

        if day in (
            Weekday.SATURDAY,
            Weekday.SUNDAY,
        ):

            return self.max_weekend_minutes

        return self.max_weekday_minutes

    # ======================================================

    @staticmethod
    def _validate_non_negative(
        name: str,
        value: int,
    ) -> None:

        if value < 0:

            raise ValueError(
                f"{name} cannot be negative."
            )

    # ======================================================

    @staticmethod
    def _validate_optional_non_negative(
        name: str,
        value: int | None,
    ) -> None:

        if value is not None and value < 0:

            raise ValueError(
                f"{name} cannot be negative."
            )

    # ======================================================

    @staticmethod
    def _normalize_days(
        days: tuple[Weekday, ...],
    ) -> tuple[Weekday, ...]:

        normalized = []

        for day in days:

            try:

                weekday = Weekday(day)

            except (TypeError, ValueError) as error:

                raise ValueError(
                    f"Invalid weekday: {day!r}"
                ) from error

            if weekday not in normalized:

                normalized.append(
                    weekday,
                )

        return tuple(normalized)