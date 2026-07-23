"""
PerformanceLab

Athlete Availability

Represents the athlete's real-world availability for
training during a typical week.
"""

from dataclasses import dataclass, field
from enum import IntEnum
from types import MappingProxyType
from typing import Mapping


class Weekday(IntEnum):
    """
    ISO-compatible weekday values.

    Monday is 0, matching datetime.date.weekday().
    """

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    # ======================================================

    @property
    def label(self) -> str:
        """
        Returns a human-readable weekday name.
        """

        return self.name.capitalize()


@dataclass(frozen=True)
class AthleteAvailability:
    """
    Represents how many minutes an athlete can train on
    each weekday.

    A value of zero means the athlete is unavailable.

    Availability describes real-life limitations. It does
    not represent training preferences or coaching rules.
    """

    minutes_by_day: Mapping[Weekday, int] = field(
        default_factory=dict,
    )

    # ======================================================

    def __post_init__(self) -> None:

        normalized = {
            day: 0
            for day in Weekday
        }

        for raw_day, raw_minutes in self.minutes_by_day.items():

            day = self._normalize_day(
                raw_day,
            )

            minutes = int(
                raw_minutes,
            )

            if minutes < 0:

                raise ValueError(
                    "Available training minutes cannot "
                    "be negative."
                )

            normalized[day] = minutes

        object.__setattr__(
            self,
            "minutes_by_day",
            MappingProxyType(normalized),
        )

    # ======================================================

    @classmethod
    def from_minutes(
        cls,
        *,
        monday: int = 0,
        tuesday: int = 0,
        wednesday: int = 0,
        thursday: int = 0,
        friday: int = 0,
        saturday: int = 0,
        sunday: int = 0,
    ) -> "AthleteAvailability":
        """
        Creates availability using explicit weekday fields.
        """

        return cls(
            minutes_by_day={
                Weekday.MONDAY: monday,
                Weekday.TUESDAY: tuesday,
                Weekday.WEDNESDAY: wednesday,
                Weekday.THURSDAY: thursday,
                Weekday.FRIDAY: friday,
                Weekday.SATURDAY: saturday,
                Weekday.SUNDAY: sunday,
            }
        )

    # ======================================================

    @property
    def available_days(self) -> tuple[Weekday, ...]:
        """
        Returns weekdays with available training time.
        """

        return tuple(
            day
            for day in Weekday
            if self.is_available(day)
        )

    # ======================================================

    @property
    def unavailable_days(self) -> tuple[Weekday, ...]:
        """
        Returns weekdays with no available training time.
        """

        return tuple(
            day
            for day in Weekday
            if not self.is_available(day)
        )

    # ======================================================

    @property
    def total_weekly_minutes(self) -> int:
        """
        Returns the total available training time.
        """

        return sum(
            self.minutes_by_day.values()
        )

    # ======================================================

    @property
    def total_weekly_hours(self) -> float:
        """
        Returns total available time in hours.
        """

        return self.total_weekly_minutes / 60

    # ======================================================

    def minutes_for(
        self,
        day: Weekday,
    ) -> int:
        """
        Returns available minutes for a weekday.
        """

        normalized_day = self._normalize_day(
            day,
        )

        return self.minutes_by_day[
            normalized_day
        ]

    # ======================================================

    def is_available(
        self,
        day: Weekday,
        minimum_minutes: int = 1,
    ) -> bool:
        """
        Returns whether the athlete has enough availability
        on a given weekday.
        """

        if minimum_minutes < 0:

            raise ValueError(
                "minimum_minutes cannot be negative."
            )

        return (
            self.minutes_for(day)
            >= minimum_minutes
        )

    # ======================================================

    def can_fit(
        self,
        day: Weekday,
        duration_minutes: int,
    ) -> bool:
        """
        Returns whether a session duration fits on a day.
        """

        if duration_minutes < 0:

            raise ValueError(
                "duration_minutes cannot be negative."
            )

        return (
            self.minutes_for(day)
            >= duration_minutes
        )

    # ======================================================

    def with_day(
        self,
        day: Weekday,
        minutes: int,
    ) -> "AthleteAvailability":
        """
        Returns a new availability object with one weekday
        changed.
        """

        normalized_day = self._normalize_day(
            day,
        )

        updated = dict(
            self.minutes_by_day,
        )

        updated[normalized_day] = minutes

        return AthleteAvailability(
            minutes_by_day=updated,
        )

    # ======================================================

    @staticmethod
    def _normalize_day(
        day: Weekday | int,
    ) -> Weekday:

        if isinstance(day, Weekday):

            return day

        try:

            return Weekday(day)

        except (TypeError, ValueError) as error:

            raise ValueError(
                f"Invalid weekday: {day!r}"
            ) from error