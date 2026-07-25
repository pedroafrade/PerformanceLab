"""
PerformanceLab

Training Focus

Supported strategic focuses for a training week.
"""

from __future__ import annotations

from enum import StrEnum


class TrainingFocus(StrEnum):
    AEROBIC_ENDURANCE = "aerobic endurance"
    RECOVERY = "recovery"

    THRESHOLD = "threshold"
    VO2MAX = "vo2max"
    TEMPO = "tempo"
    HILLS = "hills"
    SPEED = "speed"

    @classmethod
    def from_value(
        cls,
        value: str | TrainingFocus,
    ) -> TrainingFocus:
        """
        Converts a string or existing TrainingFocus into
        a normalized TrainingFocus value.
        """

        if isinstance(
            value,
            cls,
        ):
            return value

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "focus must be a string or TrainingFocus"
            )

        normalized_value = value.strip().lower()

        if not normalized_value:
            raise ValueError(
                "focus must not be empty"
            )

        try:
            return cls(
                normalized_value
            )
        except ValueError as error:
            raise ValueError(
                f"Unsupported training focus: {value!r}"
            ) from error