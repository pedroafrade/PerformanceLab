"""
PerformanceLab

Activity Coach Signals

Produces deterministic signals from completed activity data.
These signals are evidence for the Training Coach and contain
no generated coaching narrative.
"""

from dataclasses import dataclass
from enum import Enum

from performancelab.training.planning.workout_outcome import (
    EQUIVALENT_LOAD_TOLERANCE,
)


class ActivitySignalCategory(Enum):
    """
    Area of evidence represented by an activity signal.
    """

    LOAD = "load"
    CARDIOVASCULAR = "cardiovascular"
    SPECIFICITY = "specificity"
    RECOVERY = "recovery"


class ActivitySignalSeverity(Enum):
    """
    Interpretation level of an activity signal.
    """

    INFO = "info"
    POSITIVE = "positive"
    CAUTION = "caution"


@dataclass(frozen=True)
class ActivityCoachSignal:
    """
    Immutable evidence extracted from one completed activity.
    """

    code: str
    category: ActivitySignalCategory
    severity: ActivitySignalSeverity

    observed: float | None = None
    reference: float | None = None
    ratio: float | None = None
    unit: str = ""


def assess_activity_signals(
    *,
    planned_load: float | None,
    completed_load: float | None,
    duration_minutes: float | None,
    average_heart_rate: float | None,
    threshold_heart_rate: float | None,
    distance: float | None,
    elevation_gain: float | None,
    event_distance: float | None,
    event_elevation_gain: float | None,
    readiness: str | None,
    state_is_current: bool,
) -> tuple[ActivityCoachSignal, ...]:
    """
    Builds deterministic signals for the Training Coach.

    The function only classifies available evidence. It does not
    generate recommendations or infer symptoms that were not
    recorded by the athlete.
    """

    signals: list[
        ActivityCoachSignal
    ] = []

    _append_load_signal(
        signals=signals,
        planned_load=planned_load,
        completed_load=completed_load,
    )

    _append_cardiovascular_signal(
        signals=signals,
        duration_minutes=duration_minutes,
        average_heart_rate=(
            average_heart_rate
        ),
        threshold_heart_rate=(
            threshold_heart_rate
        ),
    )

    _append_specificity_signal(
        signals=signals,
        code="event_distance_exposure",
        observed=distance,
        reference=event_distance,
        unit="km",
    )

    _append_specificity_signal(
        signals=signals,
        code="event_elevation_exposure",
        observed=elevation_gain,
        reference=event_elevation_gain,
        unit="m",
    )

    _append_recovery_signal(
        signals=signals,
        readiness=readiness,
        state_is_current=state_is_current,
    )

    return tuple(
        signals
    )


def _append_load_signal(
    *,
    signals: list[ActivityCoachSignal],
    planned_load: float | None,
    completed_load: float | None,
) -> None:
    """
    Compares planned and completed session load.
    """

    if (
        completed_load is None
        or completed_load < 0
    ):
        return

    if (
        planned_load is None
        or planned_load <= 0
    ):
        signals.append(
            ActivityCoachSignal(
                code="unplanned_training_load",
                category=(
                    ActivitySignalCategory.LOAD
                ),
                severity=(
                    ActivitySignalSeverity.INFO
                ),
                observed=completed_load,
                unit="AU",
            )
        )
        return

    ratio = (
        completed_load
        / planned_load
    )

    upper_limit = (
        1.0
        + EQUIVALENT_LOAD_TOLERANCE
    )
    lower_limit = (
        1.0
        - EQUIVALENT_LOAD_TOLERANCE
    )

    if ratio > upper_limit:
        code = "load_above_plan"
        severity = (
            ActivitySignalSeverity.CAUTION
        )
    elif ratio < lower_limit:
        code = "load_below_plan"
        severity = (
            ActivitySignalSeverity.INFO
        )
    else:
        code = "load_near_plan"
        severity = (
            ActivitySignalSeverity.POSITIVE
        )

    signals.append(
        ActivityCoachSignal(
            code=code,
            category=(
                ActivitySignalCategory.LOAD
            ),
            severity=severity,
            observed=completed_load,
            reference=planned_load,
            ratio=ratio,
            unit="AU",
        )
    )


def _append_cardiovascular_signal(
    *,
    signals: list[ActivityCoachSignal],
    duration_minutes: float | None,
    average_heart_rate: float | None,
    threshold_heart_rate: float | None,
) -> None:
    """
    Detects prolonged cardiovascular demand.

    This deliberately avoids assigning an exact heart-rate zone.
    Terrain, temperature, humidity and cardiac drift may influence
    the relationship between heart rate and effort.
    """

    if (
        duration_minutes is None
        or duration_minutes < 60
        or average_heart_rate is None
        or threshold_heart_rate is None
        or threshold_heart_rate <= 0
    ):
        return

    ratio = (
        average_heart_rate
        / threshold_heart_rate
    )

    if ratio < 0.90:
        return

    signals.append(
        ActivityCoachSignal(
            code=(
                "sustained_high_"
                "cardiovascular_demand"
            ),
            category=(
                ActivitySignalCategory
                .CARDIOVASCULAR
            ),
            severity=(
                ActivitySignalSeverity.CAUTION
            ),
            observed=average_heart_rate,
            reference=threshold_heart_rate,
            ratio=ratio,
            unit="bpm",
        )
    )


def _append_specificity_signal(
    *,
    signals: list[ActivityCoachSignal],
    code: str,
    observed: float | None,
    reference: float | None,
    unit: str,
) -> None:
    """
    Measures activity exposure relative to the target event.
    """

    if (
        observed is None
        or observed < 0
        or reference is None
        or reference <= 0
    ):
        return

    ratio = (
        observed
        / reference
    )

    signals.append(
        ActivityCoachSignal(
            code=code,
            category=(
                ActivitySignalCategory
                .SPECIFICITY
            ),
            severity=(
                ActivitySignalSeverity.POSITIVE
                if ratio >= 0.50
                else ActivitySignalSeverity.INFO
            ),
            observed=observed,
            reference=reference,
            ratio=ratio,
            unit=unit,
        )
    )


def _append_recovery_signal(
    *,
    signals: list[ActivityCoachSignal],
    readiness: str | None,
    state_is_current: bool,
) -> None:
    """
    Adds recovery evidence only when the physiological state
    represents the selected activity's current context.
    """

    if (
        not state_is_current
        or not readiness
    ):
        return

    normalized = (
        readiness
        .strip()
        .lower()
    )

    if normalized in {
        "recovery",
        "cautious",
    }:
        code = "recovery_attention"
        severity = (
            ActivitySignalSeverity.CAUTION
        )
    elif normalized == "ready":
        code = "recovery_supports_training"
        severity = (
            ActivitySignalSeverity.POSITIVE
        )
    else:
        return

    signals.append(
        ActivityCoachSignal(
            code=code,
            category=(
                ActivitySignalCategory.RECOVERY
            ),
            severity=severity,
        )
    )