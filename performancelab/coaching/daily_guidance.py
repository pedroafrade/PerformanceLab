"""
PerformanceLab

Daily training guidance.

Explains why today's planned session is appropriate
and which execution cautions should be respected.
"""

from dataclasses import dataclass

from performancelab.analysis.training_state import (
    TrainingState,
)
from performancelab.training.planning.planned_workout import (
    PlannedWorkout,
)


@dataclass(frozen=True, slots=True)
class DailyTrainingGuidance:
    """
    Immutable guidance for one planned training day.
    """

    reasons: tuple[str, ...]
    cautions: tuple[str, ...]


def build_daily_training_guidance(
    *,
    training_state: TrainingState,
    workout: PlannedWorkout | None,
) -> DailyTrainingGuidance:
    """
    Builds conservative guidance from domain state
    and the planned session.
    """

    if not isinstance(
        training_state,
        TrainingState,
    ):
        raise TypeError(
            "training_state must be a TrainingState."
        )

    if (
        workout is not None
        and not isinstance(
            workout,
            PlannedWorkout,
        )
    ):
        raise TypeError(
            "workout must be a PlannedWorkout or None."
        )

    if (
        workout is None
        or workout.is_rest
    ):
        return DailyTrainingGuidance(
            reasons=(
                "No training session is planned today.",
            ),
            cautions=(
                "Use the day for recovery and preparation.",
            ),
        )

    reasons = [
        _readiness_reason(
            training_state
        ),
        _load_reason(
            training_state
        ),
    ]

    if workout.phase:
        reasons.append(
            (
                "The session supports the "
                f"{workout.phase} phase."
            )
        )

    cautions = list(
        _execution_cautions(
            training_state=training_state,
            workout=workout,
        )
    )

    return DailyTrainingGuidance(
        reasons=tuple(reasons),
        cautions=tuple(cautions),
    )


def _readiness_reason(
    training_state: TrainingState,
) -> str:
    """
    Explains the current physiological readiness.
    """

    if training_state.readiness == "ready":
        return (
            "Current recovery supports the "
            "planned session."
        )

    if training_state.readiness == "cautious":
        return (
            "Current load calls for a controlled "
            "training session."
        )

    if training_state.readiness == "easy":
        return (
            "Current form supports easy training "
            "rather than additional intensity."
        )

    return (
        "Current fatigue indicates that recovery "
        "should take priority."
    )


def _load_reason(
    training_state: TrainingState,
) -> str:
    """
    Explains the relationship with recent load.
    """

    if training_state.load_state == "balanced":
        return (
            "Recent load is balanced with habitual "
            "training."
        )

    if training_state.load_state == "high":
        return (
            "Recent load is high and requires "
            "conservative execution."
        )

    if training_state.load_state == "low":
        return (
            "Recent load remains below habitual "
            "training."
        )

    return (
        "There is not enough load history for a "
        "confident comparison."
    )


def _execution_cautions(
    *,
    training_state: TrainingState,
    workout: PlannedWorkout,
) -> tuple[str, ...]:
    """
    Returns conservative execution boundaries.
    """

    cautions = []

    if _is_demanding(
        workout
    ):
        cautions.append(
            "Keep every quality effort controlled."
        )
        cautions.append(
            (
                "Reduce intensity if recovery between "
                "efforts is inadequate."
            )
        )

    if training_state.should_reduce_volume:
        cautions.append(
            "Do not extend the planned duration."
        )
    elif not cautions:
        cautions.append(
            "Stay within the planned duration and intensity."
        )

    return tuple(cautions)


def _is_demanding(
    workout: PlannedWorkout,
) -> bool:
    """
    Identifies semantically demanding sessions.
    """

    intensity = str(
        workout.intensity
        or ""
    ).strip().lower()

    return intensity in {
        "hard",
        "very hard",
        "race effort",
        "moderately hard",
    }