"""
PerformanceLab

Daily training guidance.

Explains why today's planned session is appropriate,
classifies the daily training decision and defines
conservative execution boundaries.
"""

from dataclasses import dataclass
from datetime import timedelta
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

    COMPLETED = "completed"
    PROCEED = "proceed"
    REDUCE_VOLUME = "reduce_volume"
    EASY_ONLY = "easy_only"
    RECOVERY_AS_PLANNED = (
        "recovery_as_planned"
    )
    RECOVERY_ONLY = "recovery_only"
    REST = "rest"
    REVIEW_REQUIRED = "review_required"

@dataclass(frozen=True, slots=True)
class TemporaryWorkoutAdjustment:
    """
    Temporary execution prescription for today.

    This object never changes the persistent TrainingPlan.
    A maximum duration is an upper boundary, not a target
    that must be completed.
    """

    title: str
    intensity: str
    maximum_duration: timedelta

    replaces_planned_session: bool
    explanation: str

@dataclass(frozen=True, slots=True)
class DailyTrainingGuidance:
    """
    Immutable guidance for one planned training day.
    """

    decision: DailyTrainingDecision

    temporary_adjustment: (
        TemporaryWorkoutAdjustment
        | None
    )

    reasons: tuple[str, ...]
    cautions: tuple[str, ...]


def build_daily_training_guidance(
    *,
    training_state: TrainingState,
    workout: PlannedWorkout | None,
    workout_completed: bool = False,
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
    if not isinstance(
        workout_completed,
        bool,
    ):
        raise TypeError(
            "workout_completed must be a bool."
        )

    if workout_completed:
        return DailyTrainingGuidance(
            decision=(
                DailyTrainingDecision.COMPLETED
            ),
            temporary_adjustment=None,
            reasons=(
                (
                    "Today's activity has already "
                    "been completed."
                ),
                (
                    "The completed activity now "
                    "provides today's training stimulus."
                ),
            ),
            cautions=(
                (
                    "Do not repeat the planned session "
                    "to compensate for differences from "
                    "the prescription."
                ),
                (
                    "Use the remaining day for recovery "
                    "unless a separate session was "
                    "explicitly planned."
                ),
            ),
        )

    if (
        workout is None
        or workout.is_rest
    ):
        return DailyTrainingGuidance(
            decision=(
                DailyTrainingDecision.REST
            ),
            temporary_adjustment=None,
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
    temporary_adjustment = (
        _temporary_workout_adjustment(
            decision=decision,
            workout=workout,
        )
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
        temporary_adjustment=(
            temporary_adjustment
        ),
        reasons=tuple(reasons),
        cautions=tuple(cautions),
    )

def _temporary_workout_adjustment(
    *,
    decision: DailyTrainingDecision,
    workout: PlannedWorkout,
) -> TemporaryWorkoutAdjustment | None:
    """
    Builds a conservative execution prescription for today.

    Proceed and race-review decisions do not create a
    replacement prescription.
    """

    if decision in {
        DailyTrainingDecision.COMPLETED,
        DailyTrainingDecision.PROCEED,
        (
            DailyTrainingDecision
            .RECOVERY_AS_PLANNED
        ),
        DailyTrainingDecision.REST,
        DailyTrainingDecision.REVIEW_REQUIRED,
    }:
        return None

    if workout.duration is None:
        return None

    if (
        workout.duration.total_seconds()
        <= 0
    ):
        return None

    if (
        decision
        is DailyTrainingDecision.REDUCE_VOLUME
    ):
        return TemporaryWorkoutAdjustment(
            title=(
                workout.title
                or "Reduced planned session"
            ),
            intensity=(
                workout.intensity
                or "Controlled"
            ),
            maximum_duration=(
                _rounded_duration(
                    workout.duration,
                    fraction=0.80,
                    maximum_minutes=None,
                    minimum_minutes=5,
                )
            ),
            replaces_planned_session=False,
            explanation=(
                "Keep the planned training type but use "
                "no more than 80% of its duration."
            ),
        )

    if (
        decision
        is DailyTrainingDecision.EASY_ONLY
    ):
        return TemporaryWorkoutAdjustment(
            title="Easy session",
            intensity="Easy",
            maximum_duration=(
                _rounded_duration(
                    workout.duration,
                    fraction=0.60,
                    maximum_minutes=45,
                    minimum_minutes=20,
                )
            ),
            replaces_planned_session=True,
            explanation=(
                "Replace the planned quality work with "
                "easy continuous training."
            ),
        )

    if (
        decision
        is DailyTrainingDecision.RECOVERY_ONLY
    ):
        return TemporaryWorkoutAdjustment(
            title="Rest or very light recovery",
            intensity="Very easy",
            maximum_duration=(
                _rounded_duration(
                    workout.duration,
                    fraction=1.0,
                    maximum_minutes=20,
                    minimum_minutes=5,
                )
            ),
            replaces_planned_session=True,
            explanation=(
                "Rest is valid. If choosing active recovery, "
                "keep it very light and within this maximum."
            ),
        )

    return None


def _rounded_duration(
    duration: timedelta,
    *,
    fraction: float,
    maximum_minutes: int | None,
    minimum_minutes: int,
) -> timedelta:
    """
    Scales a duration and rounds it to a practical
    five-minute boundary.
    """

    original_minutes = (
        duration.total_seconds()
        / 60
    )

    adjusted_minutes = (
        original_minutes
        * fraction
    )

    rounded_minutes = int(
        adjusted_minutes
        / 5
        + 0.5
    ) * 5

    rounded_minutes = max(
        minimum_minutes,
        rounded_minutes,
    )

    if maximum_minutes is not None:
        rounded_minutes = min(
            rounded_minutes,
            maximum_minutes,
        )

    rounded_minutes = min(
        rounded_minutes,
        max(
            minimum_minutes,
            int(original_minutes),
        ),
    )

    return timedelta(
        minutes=rounded_minutes
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
        if _is_suitable_recovery_session(
            workout
        ):
            return (
                DailyTrainingDecision
                .RECOVERY_AS_PLANNED
            )

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
        DailyTrainingDecision.COMPLETED: (
            "Today's training stimulus is complete."
        ),
        DailyTrainingDecision.PROCEED: (
            "The planned session can proceed."
        ),
        DailyTrainingDecision.REDUCE_VOLUME: (
            "The planned session should be shortened today."
        ),
        DailyTrainingDecision.EASY_ONLY: (
            "Replace planned intensity with easy training today."
        ),
        (
            DailyTrainingDecision
            .RECOVERY_AS_PLANNED
        ): (
            "The planned recovery session already "
            "matches today's recovery needs."
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
        is (
            DailyTrainingDecision
            .RECOVERY_AS_PLANNED
        )
    ):
        return (
            (
                "Keep the planned recovery session "
                "very easy and within its duration."
            ),
            (
                "Rest instead if subjective feedback "
                "indicates that even light activity "
                "is inappropriate."
            ),
        )

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

def _is_suitable_recovery_session(
    workout: PlannedWorkout,
) -> bool:
    """
    Identifies a planned session that already satisfies
    a conservative recovery recommendation.
    """

    if workout.duration is None:
        return False

    duration_minutes = (
        workout.duration.total_seconds()
        / 60
    )

    if (
        duration_minutes <= 0
        or duration_minutes > 20
    ):
        return False

    title = str(
        workout.title
        or ""
    ).strip().lower()

    intensity = str(
        workout.intensity
        or ""
    ).strip().lower()

    return (
        "recovery" in title
        and intensity in {
            "very easy",
            "recovery",
        }
    )

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