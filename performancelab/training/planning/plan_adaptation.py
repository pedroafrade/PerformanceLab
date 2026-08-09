"""
PerformanceLab

Training plan adaptation record.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from .workout_outcome import (
    WorkoutOutcomeStatus,
)


@dataclass(frozen=True, slots=True)
class TrainingPlanAdaptation:
    """
    Immutable record of one incremental change to a
    future planned workout.
    """

    reconciled_on: date
    workout_day: date
    workout_title: str

    previous_duration: timedelta
    revised_duration: timedelta

    trigger_status: WorkoutOutcomeStatus
    load_difference: float | None = None

    previous_distance: float | None = None
    revised_distance: float | None = None

    previous_elevation_gain: float | None = None
    revised_elevation_gain: float | None = None

    previous_prescription: str | None = None
    revised_prescription: str | None = None

    def __post_init__(self) -> None:

        self._validate_date(
            self.reconciled_on,
            field_name="reconciled_on",
        )

        self._validate_date(
            self.workout_day,
            field_name="workout_day",
        )

        if (
            not isinstance(
                self.workout_title,
                str,
            )
            or not self.workout_title.strip()
        ):
            raise ValueError(
                "workout_title must be a non-empty string."
            )

        self._validate_duration(
            self.previous_duration,
            field_name="previous_duration",
        )

        self._validate_duration(
            self.revised_duration,
            field_name="revised_duration",
        )

        if (
            self.previous_duration
            == self.revised_duration
        ):
            raise ValueError(
                "An adaptation must change workout duration."
            )

        if self.trigger_status not in {
            WorkoutOutcomeStatus.MISSED,
            WorkoutOutcomeStatus.MODIFIED,
            WorkoutOutcomeStatus.SUBSTITUTE,
        }:
            raise ValueError(
                "trigger_status must describe an outcome "
                "that can adapt the future plan."
            )

        if (
            self.load_difference is not None
            and (
                isinstance(
                    self.load_difference,
                    bool,
                )
                or not isinstance(
                    self.load_difference,
                    (int, float),
                )
            )
        ):
            raise TypeError(
                "load_difference must be numeric or None."
            )

    @property
    def duration_change(self) -> timedelta:
        """
        Signed change applied to planned duration.
        """

        return (
            self.revised_duration
            - self.previous_duration
        )

    @property
    def is_reduction(self) -> bool:
        """
        Whether the future session was shortened.
        """

        return (
            self.revised_duration
            < self.previous_duration
        )

    @staticmethod
    def _validate_date(
        value,
        *,
        field_name: str,
    ) -> None:

        if (
            not isinstance(value, date)
            or isinstance(value, datetime)
        ):
            raise TypeError(
                f"{field_name} must be a date."
            )

    @staticmethod
    def _validate_duration(
        value,
        *,
        field_name: str,
    ) -> None:

        if not isinstance(
            value,
            timedelta,
        ):
            raise TypeError(
                f"{field_name} must be a timedelta."
            )

        if value <= timedelta():
            raise ValueError(
                f"{field_name} must be positive."
            )