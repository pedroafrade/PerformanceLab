"""
PerformanceLab

Training State

Represents the athlete's current physiological training state.

This object summarizes recent training load, fitness, fatigue and
recovery into a single immutable domain model that can be consumed
by the planning engine without exposing low-level physiological
metrics.
"""

from __future__ import annotations

from dataclasses import dataclass

from performancelab.physiology import (
    risk_score as workload_ratio_band,
)


@dataclass(frozen=True, slots=True)
class TrainingState:
    """
    Snapshot of an athlete's current training state.

    The values stored in this object describe the athlete at a
    specific moment in time. The object is immutable and should be
    recreated whenever new training data becomes available.
    """

    ctl: float
    atl: float
    tsb: float
    acute_chronic_ratio: float | None
    monotony: float | None
    strain: float | None
    consistency: float | None
    weekly_frequency: float | None
    days_since_last_workout: int | None
    recent_training_load: float | None
    typical_weekly_minutes: float = 0.0
    typical_weekly_sessions: float = 0.0
    typical_running_long_session_minutes: float = 0.0
    typical_running_long_session_elevation_gain: float = 0.0

    @property
    def fitness(self) -> float:
        """Long-term fitness indicator."""

        return self.ctl

    @property
    def fatigue(self) -> float:
        """Short-term fatigue indicator."""

        return self.atl

    @property
    def form(self) -> float:
        """Current freshness indicator."""

        return self.tsb

    @property
    def needs_recovery(self) -> bool:
        """
        Indicates whether the athlete should enter a recovery phase
        based on current physiological state.
        """

        return self.tsb < -20

    @property
    def can_absorb_more_volume(self) -> bool:
        """
        Returns whether the athlete appears able to tolerate
        additional training volume.
        """

        return self.tsb > -10

    @property
    def can_tolerate_intensity(self) -> bool:
        """
        Returns whether the athlete appears ready for quality
        sessions.
        """

        return self.tsb >= 0

    @property
    def load_state(self) -> str:
        """
        Describes the relationship between recent and habitual load.
        """

        band = workload_ratio_band(
            self.acute_chronic_ratio
        )

        if band == "Low":
            return "low"

        if band == "Moderate":
            return "balanced"

        if band == "High":
            return "high"

        return "unknown"

    @property
    def fatigue_level(self) -> str:
        """
        Returns a semantic description of current fatigue.
        """

        if self.needs_recovery:
            return "high"

        if not self.can_tolerate_intensity:
            return "moderate"

        return "low"

    @property
    def should_reduce_volume(self) -> bool:
        """
        Indicates whether planned volume should be reduced.
        """

        return (
            self.needs_recovery
            or self.load_state == "high"
        )

    @property
    def readiness(self) -> str:
        """
        Returns the athlete's current training readiness.
        """

        if self.needs_recovery:
            return "recovery"

        if self.should_reduce_volume:
            return "cautious"

        if not self.can_tolerate_intensity:
            return "easy"

        return "ready"

    @property
    def recovery_score(self) -> float:
        """Returns a simple recovery score between 0 and 100."""

        score = self.tsb + 50

        return max(
            0.0,
            min(
                score,
                100.0,
            ),
        )

    @property
    def recovery_status(self) -> str:
        """Returns a concise description of the recovery state."""

        if self.needs_recovery:
            return "Recovery needed"

        if self.can_tolerate_intensity:
            return "Good"

        if self.can_absorb_more_volume:
            return "Moderate"

        return "Low"

    @property
    def recovery_recommendation(self) -> str:
        """Returns a training recommendation for the recovery state."""

        if self.needs_recovery:
            return (
                "Prioritise recovery before the next demanding "
                "training session."
            )

        if self.can_tolerate_intensity:
            return "Ready for a normal training session."

        if self.can_absorb_more_volume:
            return (
                "Training can continue, but keep demanding sessions "
                "controlled."
            )

        return (
            "Keep training easy and monitor recovery before adding "
            "more load."
        )

    @property
    def training_trend(self) -> str:
        """Returns the current training trend."""

        if self.ctl > self.atl:
            return "building"

        if self.tsb > 10:
            return "fresh"

        if self.needs_recovery:
            return "fatigued"

        return "stable"

    def __repr__(self) -> str:
        return (
            "TrainingState("
            f"CTL={self.ctl:.1f}, "
            f"ATL={self.atl:.1f}, "
            f"TSB={self.tsb:.1f})"
        )