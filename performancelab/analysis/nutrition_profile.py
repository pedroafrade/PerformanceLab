"""
PerformanceLab

Nutrition Profile

Represents an athlete's tested endurance nutrition and
hydration preferences.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from math import floor


@dataclass(frozen=True, slots=True)
class NutritionProfile:
    """
    Immutable endurance nutrition profile.

    Values describe an athlete's tested intake ranges.
    They are planning references rather than universal
    medical prescriptions.
    """

    carbohydrate_per_hour: int = 80

    fluid_lower_ml_per_hour: int = 450
    fluid_upper_ml_per_hour: int = 600

    sodium_lower_mg_per_hour: int = 400
    sodium_upper_mg_per_hour: int = 600

    gel_carbohydrate_grams: int = 25

    pre_race_carbohydrate_lower: int = 60
    pre_race_carbohydrate_upper: int = 80

    source: str = "default"

    def __post_init__(self) -> None:

        integer_fields = (
            "carbohydrate_per_hour",
            "fluid_lower_ml_per_hour",
            "fluid_upper_ml_per_hour",
            "sodium_lower_mg_per_hour",
            "sodium_upper_mg_per_hour",
            "gel_carbohydrate_grams",
            "pre_race_carbohydrate_lower",
            "pre_race_carbohydrate_upper",
        )

        for field_name in integer_fields:

            value = getattr(
                self,
                field_name,
            )

            if (
                not isinstance(value, int)
                or isinstance(value, bool)
            ):
                raise TypeError(
                    f"{field_name} must be an integer."
                )

            if value <= 0:
                raise ValueError(
                    f"{field_name} must be positive."
                )

        if (
            self.fluid_lower_ml_per_hour
            > self.fluid_upper_ml_per_hour
        ):
            raise ValueError(
                "Fluid lower limit cannot exceed "
                "the upper limit."
            )

        if (
            self.sodium_lower_mg_per_hour
            > self.sodium_upper_mg_per_hour
        ):
            raise ValueError(
                "Sodium lower limit cannot exceed "
                "the upper limit."
            )

        if (
            self.pre_race_carbohydrate_lower
            > self.pre_race_carbohydrate_upper
        ):
            raise ValueError(
                "Pre-race carbohydrate lower limit "
                "cannot exceed the upper limit."
            )

        normalized_source = str(
            self.source
        ).strip().lower()

        if not normalized_source:
            raise ValueError(
                "Nutrition profile source cannot be empty."
            )

        object.__setattr__(
            self,
            "source",
            normalized_source,
        )

    # ======================================================

    def carbohydrate_for(
        self,
        duration: timedelta,
    ) -> int:
        """
        Returns total carbohydrate rounded to a practical
        five-gram increment.
        """

        hours = self._duration_hours(
            duration
        )

        return self._round_to_increment(
            hours
            * self.carbohydrate_per_hour,
            increment=5,
        )

    # ======================================================

    def fluid_for(
        self,
        duration: timedelta,
    ) -> tuple[int, int]:
        """
        Returns the planned fluid range in millilitres,
        rounded to 50 ml.
        """

        hours = self._duration_hours(
            duration
        )

        return (
            self._round_to_increment(
                hours
                * self.fluid_lower_ml_per_hour,
                increment=50,
            ),
            self._round_to_increment(
                hours
                * self.fluid_upper_ml_per_hour,
                increment=50,
            ),
        )

    # ======================================================

    def sodium_for(
        self,
        duration: timedelta,
    ) -> tuple[int, int]:
        """
        Returns the planned sodium range in milligrams,
        rounded to 50 mg.
        """

        hours = self._duration_hours(
            duration
        )

        return (
            self._round_to_increment(
                hours
                * self.sodium_lower_mg_per_hour,
                increment=50,
            ),
            self._round_to_increment(
                hours
                * self.sodium_upper_mg_per_hour,
                increment=50,
            ),
        )

    # ======================================================

    @staticmethod
    def _duration_hours(
        duration: timedelta,
    ) -> float:

        if not isinstance(
            duration,
            timedelta,
        ):
            raise TypeError(
                "duration must be a timedelta."
            )

        seconds = (
            duration.total_seconds()
        )

        if seconds <= 0:
            raise ValueError(
                "duration must be positive."
            )

        return seconds / 3600

    # ======================================================

    @staticmethod
    def _round_to_increment(
        value: float,
        *,
        increment: int,
    ) -> int:

        return (
            floor(
                value / increment
                + 0.5
            )
            * increment
        )