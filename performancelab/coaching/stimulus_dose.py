"""
PerformanceLab

Stimulus Dose

Defines the quantitative physiological dose of a workout.
"""

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class StimulusDose:
    """
    Immutable quantitative limits for a workout stimulus.

    Work minutes refer only to the principal physiological
    work. Warm-up, recovery intervals and cool-down are not
    included in these values.
    """

    minimum_work_minutes: int
    target_work_minutes: int
    maximum_work_minutes: int

    maximum_repetition_minutes: int | None = None
    recovery_minutes: int | None = None

    def __post_init__(self) -> None:
        self._validate_positive_integer(
            self.minimum_work_minutes,
            field="minimum_work_minutes",
        )

        self._validate_positive_integer(
            self.target_work_minutes,
            field="target_work_minutes",
        )

        self._validate_positive_integer(
            self.maximum_work_minutes,
            field="maximum_work_minutes",
        )

        if not (
            self.minimum_work_minutes
            <= self.target_work_minutes
            <= self.maximum_work_minutes
        ):
            raise ValueError(
                "work minutes must satisfy "
                "minimum <= target <= maximum"
            )

        if self.maximum_repetition_minutes is not None:
            self._validate_positive_integer(
                self.maximum_repetition_minutes,
                field="maximum_repetition_minutes",
            )

            if (
                self.maximum_repetition_minutes
                > self.maximum_work_minutes
            ):
                raise ValueError(
                    "maximum_repetition_minutes cannot exceed "
                    "maximum_work_minutes"
                )

        if self.recovery_minutes is not None:
            self._validate_positive_integer(
                self.recovery_minutes,
                field="recovery_minutes",
            )

    @staticmethod
    def _validate_positive_integer(
        value: int,
        *,
        field: str,
    ) -> None:
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
        ):
            raise TypeError(
                f"{field} must be an integer"
            )

        if value <= 0:
            raise ValueError(
                f"{field} must be greater than zero"
            )