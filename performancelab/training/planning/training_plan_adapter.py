"""
PerformanceLab

Training Plan Adapter

Applies incremental revisions to future planned workouts.
"""

from dataclasses import replace
from datetime import date, datetime

from performancelab.analysis.training_state import (
    TrainingState,
)
from performancelab.training.load import (
    planned_workout_load,
)
from .planned_workout import PlannedWorkout
from .training_plan import TrainingPlan
from .workout_outcome import (
    WorkoutOutcome,
    WorkoutOutcomeStatus,
)


MAX_OVERLOAD_DURATION_REDUCTION = 0.20
OVERLOAD_RESPONSE_FRACTION = 0.25
MAX_UNDERLOAD_DURATION_INCREASE = 0.05
UNDERLOAD_RECOVERY_FRACTION = 0.25


class TrainingPlanAdapter:
    """
    Adapts a persistent training plan after reconciling it
    with completed training history.
    """

    def adapt(
        self,
        *,
        plan: TrainingPlan,
        outcomes: tuple[WorkoutOutcome, ...],
        training_state: TrainingState,
        reference_day: date,
    ) -> TrainingPlan:
        """
        Returns an incrementally revised training plan.

        Equivalent completed workouts and pending future
        workouts do not require changes.
        """

        self._validate_inputs(
            plan=plan,
            outcomes=outcomes,
            training_state=training_state,
            reference_day=reference_day,
        )

        workouts = list(
            plan.workouts
        )

        overload_outcomes = tuple(
            outcome
            for outcome in outcomes
            if outcome.status
            in {
                WorkoutOutcomeStatus.MODIFIED,
                WorkoutOutcomeStatus.SUBSTITUTE,
            }
            and outcome.load_difference
            is not None
            and outcome.load_difference
            > 0
        )

        overload_reduction = (
            self._overload_reduction(
                overload_outcomes
            )
        )

        if (
            overload_reduction > 0
            and training_state.should_reduce_volume
        ):
            workouts = (
                self._reduce_next_demanding_workout(
                    workouts=workouts,
                    reference_day=reference_day,
                    reduction_fraction=(
                        overload_reduction
                    ),
                )
            )

        underload_outcomes = tuple(
            outcome
            for outcome in outcomes
            if (
                outcome.status
                is WorkoutOutcomeStatus.MISSED
                or (
                    outcome.status
                    in {
                        WorkoutOutcomeStatus.MODIFIED,
                        WorkoutOutcomeStatus.SUBSTITUTE,
                    }
                    and (
                        outcome.load_difference is not None
                        and outcome.load_difference < 0
                    )
                )
            )
        )

        has_underload = bool(
            underload_outcomes
        )

        missing_load = (
            self._missing_load(
                underload_outcomes
            )
        )

        if (
            has_underload
            and training_state.can_absorb_more_volume
        ):
            workouts = (
                self._increase_next_easy_workout(
                    workouts=workouts,
                    reference_day=reference_day,
                    missing_load=missing_load,
                    preferred_sport_families=tuple(
                        dict.fromkeys(
                            self._sport_family(
                                outcome
                                .planned_workout
                                .sport
                            )
                            for outcome
                            in underload_outcomes
                        )
                    ),
                )
            )

        return TrainingPlan(
            plan_id=plan.plan_id,
            start_date=plan.start_date,
            end_date=plan.end_date,
            reconciled_through=(
                plan.reconciled_through
            ),
            reconciled_workout_ids=(
                plan.reconciled_workout_ids
            ),
            reconciled_workout_signatures=(
                plan.reconciled_workout_signatures
            ),
            primary_event_id=(
                plan.primary_event_id
            ),
            competition_event_ids=(
                plan.competition_event_ids
            ),
            workouts=workouts,
        )

    # ======================================================

    @staticmethod
    def _overload_reduction(
        outcomes: tuple[
            WorkoutOutcome,
            ...,
        ],
    ) -> float:
        planned_load = 0.0
        excess_load = 0.0

        for outcome in outcomes:
            if (
                outcome.planned_load
                is None
                or outcome.planned_load
                <= 0
            ):
                continue

            load_difference = (
                outcome.load_difference
            )

            if (
                load_difference is None
                or load_difference <= 0
            ):
                continue

            planned_load += (
                outcome.planned_load
            )
            excess_load += (
                load_difference
            )

        if (
            planned_load <= 0
            or excess_load <= 0
        ):
            return 0.0

        overload_ratio = (
            excess_load
            / planned_load
        )

        return min(
            MAX_OVERLOAD_DURATION_REDUCTION,
            overload_ratio
            * OVERLOAD_RESPONSE_FRACTION,
        )
    
    # ======================================================

    @staticmethod
    def _reduce_next_demanding_workout(
        *,
        workouts: list[PlannedWorkout],
        reference_day: date,
        reduction_fraction: float,
    ) -> list[PlannedWorkout]:
        """
        Reduce the next demanding workout proportionally to excess load.
        """

        updated = list(
            workouts
        )

        candidate_index = next(
            (
                index
                for index, workout
                in enumerate(updated)
                if (
                    workout.day
                    > reference_day
                    and workout.duration is not None
                    and workout.duration.total_seconds()
                    > 0
                    and TrainingPlanAdapter._is_demanding(
                        workout
                    )
                    and not TrainingPlanAdapter._is_protected(
                        workout
                    )
                )
            ),
            None,
        )

        if candidate_index is None:
            return updated

        candidate = updated[
            candidate_index
        ]

        updated[candidate_index] = replace(
            candidate,
            duration=(
                candidate.duration
                * (
                    1.0
                    - reduction_fraction
                )
            ),
        )

        return updated

    # ======================================================
    @staticmethod
    def _missing_load(
        outcomes: tuple[
            WorkoutOutcome,
            ...,
        ],
    ) -> float | None:
        """
        Returns total known missing load.

        None means at least one missed workout does not
        have enough planned-load information.
        """

        missing_load = 0.0

        for outcome in outcomes:

            if (
                outcome.status
                is WorkoutOutcomeStatus.MISSED
            ):

                if outcome.planned_load is None:
                    return None

                missing_load += max(
                    0.0,
                    outcome.planned_load,
                )

                continue

            load_difference = (
                outcome.load_difference
            )

            if (
                load_difference is not None
                and load_difference < 0
            ):
                missing_load += (
                    -load_difference
                )

        return missing_load

    # ======================================================
    
    @staticmethod
    def _increase_next_easy_workout(
        *,
        workouts: list[PlannedWorkout],
        reference_day: date,
        missing_load: float | None,
        preferred_sport_families: tuple[
            str,
            ...,
        ] = (),
    ) -> list[PlannedWorkout]:
        """
        Adds a small fraction of missing load to the next
        unprotected easy workout.

        The missed workout is never moved to another day.
        """

        updated = list(
            workouts
        )

        candidate_indices = [
            index
            for index, workout
            in enumerate(updated)
            if (
                workout.day
                > reference_day
                and workout.duration is not None
                and workout.duration.total_seconds()
                > 0
                and TrainingPlanAdapter._is_easy(
                    workout
                )
                and not TrainingPlanAdapter._is_protected(
                    workout
                )
            )
        ]

        candidate_index = next(
            (
                index
                for index in candidate_indices
                if (
                    TrainingPlanAdapter
                    ._sport_family(
                        updated[index].sport
                    )
                    in preferred_sport_families
                )
            ),
            (
                candidate_indices[0]
                if candidate_indices
                else None
            ),
        )

        if candidate_index is None:
            return updated

        candidate = updated[
            candidate_index
        ]
        increase_fraction = (
            MAX_UNDERLOAD_DURATION_INCREASE
        )

        candidate_load = (
            planned_workout_load(
                candidate
            )
        )

        if (
            missing_load is not None
            and candidate_load is not None
            and candidate_load > 0
        ):

            recoverable_load = (
                missing_load
                * UNDERLOAD_RECOVERY_FRACTION
            )

            increase_fraction = min(
                MAX_UNDERLOAD_DURATION_INCREASE,
                recoverable_load
                / candidate_load,
            )

        if increase_fraction <= 0:
            return updated
        
        updated[candidate_index] = replace(
            candidate,
            duration=(
                candidate.duration
                * (
                    1.0
                    + increase_fraction
                )
            ),
        )

        return updated

    # ======================================================

    @staticmethod
    def _is_easy(
        workout: PlannedWorkout,
    ) -> bool:
        """
        Returns whether a workout can safely receive a
        small duration increase.
        """

        description = (
            TrainingPlanAdapter._description(
                workout
            )
        )

        return any(
            token in description
            for token in (
                "easy",
                "recovery",
            )
        )

    # ======================================================

    @staticmethod
    def _is_demanding(
        workout: PlannedWorkout,
    ) -> bool:
        """
        Returns whether a workout represents a demanding
        training session.
        """

        description = (
            TrainingPlanAdapter._description(
                workout
            )
        )

        return any(
            token in description
            for token in (
                "tempo",
                "lt2",
                "threshold",
                "interval",
                "hill",
                "speed",
                "vo2",
            )
        )

    # ======================================================

    @staticmethod
    def _is_protected(
        workout: PlannedWorkout,
    ) -> bool:
        """
        Protects competitions and critical race preparation
        from incremental adaptation.
        """

        phase = str(
            workout.phase or ""
        ).strip().lower()

        if phase in {
            "taper",
            "race",
        }:
            return True

        description = (
            TrainingPlanAdapter._description(
                workout
            )
        )

        return any(
            token in description
            for token in (
                "race",
                "shakeout",
                "pre-race",
                "pre race",
            )
        )

    # ======================================================
    @staticmethod
    def _sport_family(
        sport,
    ) -> str:
        """
        Normalizes sports into comparable training families.
        """

        normalized = str(
            sport or ""
        ).strip().lower()

        if any(
            token in normalized
            for token in (
                "run",
                "running",
                "trail",
                "jog",
            )
        ):
            return "running"

        if any(
            token in normalized
            for token in (
                "cycl",
                "bike",
                "bicycle",
            )
        ):
            return "cycling"

        if "swim" in normalized:
            return "swimming"

        return normalized or "other"

    # ======================================================
    
    @staticmethod
    def _description(
        workout: PlannedWorkout,
    ) -> str:
        """
        Returns normalized semantic workout information.
        """

        return " ".join(
            str(value or "")
            for value in (
                workout.title,
                workout.intensity,
                workout.objective,
            )
        ).strip().lower()

    # ======================================================

    @staticmethod
    def _validate_inputs(
        *,
        plan: TrainingPlan,
        outcomes: tuple[WorkoutOutcome, ...],
        training_state: TrainingState,
        reference_day: date,
    ) -> None:

        if not isinstance(
            plan,
            TrainingPlan,
        ):
            raise TypeError(
                "plan must be a TrainingPlan."
            )

        if not isinstance(
            outcomes,
            tuple,
        ):
            raise TypeError(
                "outcomes must be a tuple."
            )

        if not all(
            isinstance(
                outcome,
                WorkoutOutcome,
            )
            for outcome in outcomes
        ):
            raise TypeError(
                "outcomes must contain WorkoutOutcome "
                "objects."
            )

        if not isinstance(
            training_state,
            TrainingState,
        ):
            raise TypeError(
                "training_state must be a TrainingState."
            )

        if (
            not isinstance(
                reference_day,
                date,
            )
            or isinstance(
                reference_day,
                datetime,
            )
        ):
            raise TypeError(
                "reference_day must be a date."
            )