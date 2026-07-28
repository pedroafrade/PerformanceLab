"""
PerformanceLab

Performance Profile

Represents the athlete's intrinsic physiological profile.

Unlike TrainingState, which reflects the athlete's current
training condition, PerformanceProfile represents relatively
stable physiological characteristics that evolve slowly over
time.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PerformanceProfile:
    """
    Immutable snapshot of an athlete's physiological profile.

    This object describes the athlete's capabilities rather than
    their current fatigue or readiness.
    """

    age: int | None

    gender: str | None

    height: float | None

    weight: float | None

    ftp: float | None

    vo2max: float | None

    threshold_power: float | None

    threshold_hr: int | None

    threshold_pace: float | None

    max_hr: int | None

    resting_hr: int | None

    running_economy: float | None

    @property
    def has_power_profile(self) -> bool:
        """Returns whether power-based metrics are available."""

        return self.ftp is not None

    @property
    def has_heart_rate_profile(self) -> bool:
        """Returns whether heart-rate metrics are available."""

        return (
            self.max_hr is not None
            and self.resting_hr is not None
        )

    @property
    def heart_rate_reserve(self) -> int | None:
        """
        Heart Rate Reserve (HRR).

        Returns
        -------
        int | None
            Maximum HR minus resting HR.
        """

        if (
            self.max_hr is None
            or self.resting_hr is None
        ):
            return None

        return self.max_hr - self.resting_hr

    @property
    def bmi(self) -> float | None:
        """
        Body Mass Index.

        Returns
        -------
        float | None
        """

        if (
            self.height is None
            or self.weight is None
            or self.height <= 0
        ):
            return None

        return self.weight / (self.height ** 2)

    def __repr__(self) -> str:

        return (
            "PerformanceProfile("
            f"FTP={self.ftp}, "
            f"VO2max={self.vo2max}, "
            f"Weight={self.weight})"
        )