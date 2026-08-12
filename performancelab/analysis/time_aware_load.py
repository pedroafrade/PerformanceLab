"""
PerformanceLab

Time-aware training load.

Extends the daily CTL and ATL baseline through the
current day without pretending that the whole calendar
day has already elapsed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import exp


HOURS_PER_DAY = 24.0
CTL_TIME_CONSTANT_DAYS = 42.0
ATL_TIME_CONSTANT_DAYS = 7.0


def decay_training_load(
    value: float,
    *,
    elapsed_hours: float,
    time_constant_days: float,
) -> float:
    """
    Applies continuous exponential decay over a partial
    day.
    """

    if elapsed_hours < 0:
        raise ValueError(
            "elapsed_hours cannot be negative"
        )

    if time_constant_days <= 0:
        raise ValueError(
            "time_constant_days must be positive"
        )

    return (
        float(value)
        * exp(
            -elapsed_hours
            / (
                HOURS_PER_DAY
                * time_constant_days
            )
        )
    )


def training_load_impulse(
    load: float,
    *,
    time_constant_days: float,
) -> float:
    """
    Converts one completed workout load into the same
    exponential scale used by the daily CTL and ATL
    calculations.
    """

    if load < 0:
        raise ValueError(
            "training load cannot be negative"
        )

    if time_constant_days <= 0:
        raise ValueError(
            "time_constant_days must be positive"
        )

    alpha = (
        1.0
        - exp(
            -1.0
            / time_constant_days
        )
    )

    return alpha * load


@dataclass(
    frozen=True,
    slots=True,
)
class TimeAwareTrainingLoad:
    """
    Immutable load and recovery estimate for one instant.
    """

    reference_time: datetime
    ctl: float
    atl: float

    @property
    def tsb(self) -> float:
        return self.ctl - self.atl

    @property
    def recovery_score(self) -> float:
        """
        Preserves the existing TSB-based recovery scale.
        """

        score = self.tsb + 50.0

        return max(
            0.0,
            min(
                score,
                100.0,
            ),
        )