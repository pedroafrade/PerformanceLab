"""
PerformanceLab

Daily training guidance.

Explains why today's planned session is appropriate,
classifies the daily training decision and defines
conservative execution boundaries.
"""

from dataclasses import dataclass
from enum import Enum

from performancelab.analysis.training_state import (
    TrainingState,
)
from performancelab.training.planning.planned_workout import (
    PlannedWorkout,
)


class DailyTrainingDecision(str, Enum):
    """
    Deterministic decision for today's planned training.

    The decision does not mutate the persistent plan.
    """

    PROCEED = "proceed"
    REDUCE_VOLUME = "reduce_volume"
    EASY_ONLY = "easy_only"
    RECOVERY_ONLY = "recovery_only"
    REST = "rest"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True, slots=True)
class DailyTrainingGuidance:
    """
    Immutable guidance for one planned training day.
    """

    decision: DailyTrainingDecision
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

    This function classifies today's execution decision.
    It does not modify the persistent TrainingPlan.
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
            decision=(
                DailyTrainingDecision.REST
            ),
            reasons=(
                "No training session is planned today.",
            ),
            cautions=(
                "Use the day for recovery and preparation.",
            ),
        )

    decision = _daily_training_decision(
        training_state=training_state,
        workout=workout,
    )

    reasons = [
        _readiness_reason(
            training_state
        ),
        _load_reason(
            training_state
        ),
        _decision_reason(
            decision
        ),
    ]

    if workout.phase:
        reasons.append(
            (
                "The planned session supports the "
                f"{workout.phase} phase."
            )
        )

    cautions = list(
        _execution_cautions(
            training_state=training_state,
            workout=workout,
            decision=decision,
        )
    )

    return DailyTrainingGuidance(
        decision=decision,
        reasons=tuple(reasons),
        cautions=tuple(cautions),
    )


def _daily_training_decision(
    *,
    training_state: TrainingState,
    workout: PlannedWorkout,
) -> DailyTrainingDecision:
    """
    Classifies today's execution without changing the plan.

    A race is never automatically replaced from physiological
    estimates alone. It is instead marked for explicit review.
    """

    if _is_race(
        workout
    ):
        if (
            training_state.readiness
            == "recovery"
            or training_state.should_reduce_volume
        ):
            return (
                DailyTrainingDecision
                .REVIEW_REQUIRED
            )

        return DailyTrainingDecision.PROCEED

    if training_state.readiness == "recovery":
        return (
            DailyTrainingDecision
            .RECOVERY_ONLY
        )

    if _is_demanding(
        workout
    ):
        if (
            training_state.readiness == "easy"
            or not (
                training_state
                .can_tolerate_intensity
            )
        ):
            return (
                DailyTrainingDecision
                .EASY_ONLY
            )

        if training_state.should_reduce_volume:
            return (
                DailyTrainingDecision
                .REDUCE_VOLUME
            )

    elif training_state.should_reduce_volume:
        return (
            DailyTrainingDecision
            .REDUCE_VOLUME
        )

    return DailyTrainingDecision.PROCEED


def _decision_reason(
    decision: DailyTrainingDecision,
) -> str:
    """
    Explains the deterministic daily decision.
    """

    reasons = {
        DailyTrainingDecision.PROCEED: (
            "The planned session can proceed."
        ),
        DailyTrainingDecision.REDUCE_VOLUME: (
            "The planned session should be shortened today."
        ),
        DailyTrainingDecision.EASY_ONLY: (
            "Replace planned intensity with easy training today."
        ),
        DailyTrainingDecision.RECOVERY_ONLY: (
            "Recovery should replace the planned training stimulus today."
        ),
        DailyTrainingDecision.REST: (
            "No training stimulus is recommended today."
        ),
        DailyTrainingDecision.REVIEW_REQUIRED: (
            "The planned race requires an explicit readiness review."
        ),
    }

    return reasons[
        decision
    ]


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
    decision: DailyTrainingDecision,
) -> tuple[str, ...]:
    """
    Returns conservative execution boundaries.
    """

    if (
        decision
        is DailyTrainingDecision.RECOVERY_ONLY
    ):
        return (
            (
                "Do not perform the planned intensity "
                "or volume today."
            ),
            (
                "Use rest or very light recovery work "
                "according to subjective feedback."
            ),
        )

    if (
        decision
        is DailyTrainingDecision.EASY_ONLY
    ):
        return (
            "Do not perform the planned quality intervals.",
            (
                "Keep the replacement session easy and "
                "shorter than the original session."
            ),
        )

    if (
        decision
        is DailyTrainingDecision.REDUCE_VOLUME
    ):
        return (
            "Shorten the planned duration.",
            (
                "Do not add repetitions, distance "
                "or elevation."
            ),
        )

    if (
        decision
        is DailyTrainingDecision.REVIEW_REQUIRED
    ):
        return (
            (
                "Do not use the recovery estimate alone "
                "to make a race decision."
            ),
            (
                "Review symptoms, subjective readiness "
                "and race priority before starting."
            ),
        )

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


def _is_race(
    workout: PlannedWorkout,
) -> bool:
    """
    Identifies competition sessions protected from
    automatic replacement.
    """

    title = str(
        workout.title
        or ""
    ).strip().lower()

    intensity = str(
        workout.intensity
        or ""
    ).strip().lower()

    return (
        title == "race"
        or intensity == "race effort"
    )


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