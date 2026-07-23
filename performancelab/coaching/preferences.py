"""
PerformanceLab

Athlete Preferences

Represents the athlete's preferred weekly training
arrangement.

Preferences are soft requirements. The generator should try
to respect them but may deviate when necessary.
"""

from dataclasses import dataclass, field

from .availability import Weekday


@dataclass(frozen=True)
class AthletePreferences:
    """
    Soft preferences used when arranging a training week.
    """

    preferred_long_day: Weekday | None = None

    preferred_rest_days: tuple[Weekday, ...] = field(
        default_factory=tuple,
    )

    preferred_intensity_days: tuple[Weekday, ...] = field(
        default_factory=tuple,
    )

    preferred_sports: tuple[str, ...] = field(
        default_factory=tuple,
    )

    morning_only: bool = False

    avoid_double_sessions: bool = True

    prefers_trail: bool = False

    # ======================================================

    def __post_init__(self) -> None:

        preferred_long_day = (
            self._normalize_optional_day(
                self.preferred_long_day,
            )
        )

        preferred_rest_days = (
            self._normalize_days(
                self.preferred_rest_days,
            )
        )

        preferred_intensity_days = (
            self._normalize_days(
                self.preferred_intensity_days,
            )
        )

        preferred_sports = tuple(
            sport.strip()
            for sport in self.preferred_sports
            if sport.strip()
        )

        if (
            preferred_long_day is not None
            and preferred_long_day
            in preferred_rest_days
        ):

            raise ValueError(
                "preferred_long_day cannot also be a "
                "preferred rest day."
            )

        object.__setattr__(
            self,
            "preferred_long_day",
            preferred_long_day,
        )

        object.__setattr__(
            self,
            "preferred_rest_days",
            preferred_rest_days,
        )

        object.__setattr__(
            self,
            "preferred_intensity_days",
            preferred_intensity_days,
        )

        object.__setattr__(
            self,
            "preferred_sports",
            preferred_sports,
        )

    # ======================================================

    def prefers_rest(
        self,
        day: Weekday,
    ) -> bool:
        """
        Returns whether the athlete prefers resting on a day.
        """

        return (
            Weekday(day)
            in self.preferred_rest_days
        )

    # ======================================================

    def prefers_intensity(
        self,
        day: Weekday,
    ) -> bool:
        """
        Returns whether the athlete prefers intensity on a
        given day.
        """

        return (
            Weekday(day)
            in self.preferred_intensity_days
        )

    # ======================================================

    def prefers_sport(
        self,
        sport: str,
    ) -> bool:
        """
        Returns whether a sport appears in the preferred
        sports list.

        An empty preferred_sports collection means that no
        sport preference has been declared.
        """

        if not self.preferred_sports:

            return True

        normalized = sport.casefold()

        return any(
            preferred.casefold() == normalized
            for preferred in self.preferred_sports
        )

    # ======================================================

    @staticmethod
    def _normalize_optional_day(
        day: Weekday | int | None,
    ) -> Weekday | None:

        if day is None:

            return None

        try:

            return Weekday(day)

        except (TypeError, ValueError) as error:

            raise ValueError(
                f"Invalid weekday: {day!r}"
            ) from error

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