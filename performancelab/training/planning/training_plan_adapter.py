"""
PerformanceLab

Training Plan Adapter

Applies incremental revisions to future planned workouts.
"""

from dataclasses import replace
from datetime import date, datetime
from math import ceil

from performancelab.analysis.training_state import (
    TrainingState,
)
from performancelab.training.load import (
    planned_workout_load,
)
from .planned_workout import PlannedWorkout
from .plan_adaptation import (
    TrainingPlanAdaptation,
)
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
        original_workouts = tuple(
            plan.workouts
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

        adaptation_records = (
            self._adaptation_records(
                original_workouts=(
                    original_workouts
                ),
                revised_workouts=tuple(
                    workouts
                ),
                reference_day=(
                    reference_day
                ),
                overload_outcomes=(
                    overload_outcomes
                ),
                underload_outcomes=(
                    underload_outcomes
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
            adaptations=(
                plan.adaptations
                + adaptation_records
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
    def _adaptation_records(
        *,
        original_workouts: tuple[
            PlannedWorkout,
            ...,
        ],
        revised_workouts: tuple[
            PlannedWorkout,
            ...,
        ],
        reference_day: date,
        overload_outcomes: tuple[
            WorkoutOutcome,
            ...,
        ],
        underload_outcomes: tuple[
            WorkoutOutcome,
            ...,
        ],
    ) -> tuple[
        TrainingPlanAdaptation,
        ...,
    ]:
        """
        Records duration changes made to future sessions.
        """

        records = []

        for original, revised in zip(
            original_workouts,
            revised_workouts,
        ):
            if (
                original.duration is None
                or revised.duration is None
                or original.duration
                == revised.duration
            ):
                continue

            if (
                revised.duration
                < original.duration
            ):
                candidates = (
                    overload_outcomes
                )
            else:
                candidates = (
                    underload_outcomes
                )

            trigger = max(
                candidates,
                key=(
                    TrainingPlanAdapter
                    ._outcome_priority
                ),
                default=None,
            )

            if trigger is None:
                continue

            records.append(
                TrainingPlanAdaptation(
                    reconciled_on=(
                        reference_day
                    ),
                    workout_day=(
                        revised.day
                    ),
                    workout_title=(
                        revised.title
                        or original.title
                        or "Planned workout"
                    ),
                    previous_duration=(
                        original.duration
                    ),
                    revised_duration=(
                        revised.duration
                    ),
                    trigger_status=(
                        trigger.status
                    ),
                    load_difference=(
                        trigger.load_difference
                    ),
                )
            )

        return tuple(
            records
        )

    @staticmethod
    def _outcome_priority(
        outcome: WorkoutOutcome,
    ) -> float:
        """
        Gives priority to the outcome with the largest
        known load effect.
        """

        if (
            outcome.load_difference
            is not None
        ):
            return abs(
                outcome.load_difference
            )

        if outcome.planned_load is not None:
            return abs(
                outcome.planned_load
            )

        return 0.0
    
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

        adjusted_duration = (
            candidate.duration
            * (
                1.0
                - reduction_fraction
            )
        )

        adjusted_minutes = max(
            1,
            round(
                adjusted_duration.total_seconds()
                / 60
            ),
        )

        adjusted_structure = (
            TrainingPlanAdapter
            ._adapted_structure(
                workout=candidate,
                duration=adjusted_duration,
                main_label=(
                    "Controlled quality work"
                ),
            )
        )

        interval_summary = next(
            (
                step
                for step in adjusted_structure
                if "×" in step
            ),
            None,
        )

        prescription_summary = (
            (
                f"{interval_summary} · "
                f"{adjusted_minutes} min total"
            )
            if interval_summary is not None
            else (
                "Reduced quality session · "
                f"{adjusted_minutes} min total"
            )
        )

        updated[candidate_index] = replace(
            candidate,
            duration=adjusted_duration,
            prescription_summary=(
                prescription_summary
            ),
            structure=adjusted_structure,
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
        
        adjusted_duration = (
            candidate.duration
            * (
                1.0
                + increase_fraction
            )
        )

        adjusted_minutes = max(
            1,
            round(
                adjusted_duration.total_seconds()
                / 60
            ),
        )

        updated[candidate_index] = replace(
            candidate,
            duration=adjusted_duration,
            prescription_summary=(
                "Adjusted easy session · "
                f"{adjusted_minutes} min total"
            ),
            structure=(
                TrainingPlanAdapter
                ._adapted_structure(
                    workout=candidate,
                    duration=adjusted_duration,
                    main_label=(
                        "Easy aerobic training"
                    ),
                )
            ),
        )

        return updated

    # ======================================================
    @staticmethod
    def _adapted_threshold_structure(
        total_minutes: int,
    ) -> tuple[str, ...]:
        """
        Builds a conservative threshold prescription while
        preserving the existing LT2 adaptation behaviour.
        """

        repetitions = 3
        recovery_minutes = 2

        work_minutes = max(
            4,
            ceil(
                total_minutes
                / (
                    repetitions
                    * 2
                )
            ),
        )

        total_work_minutes = (
            repetitions
            * work_minutes
        )

        total_recovery_minutes = (
            (
                repetitions
                - 1
            )
            * recovery_minutes
        )

        preparation_minutes = (
            total_minutes
            - total_work_minutes
            - total_recovery_minutes
        )

        cool_down_minutes = max(
            4,
            round(
                preparation_minutes
                * 0.35
            ),
        )

        warm_up_minutes = (
            preparation_minutes
            - cool_down_minutes
        )

        return (
            (
                "Warm up "
                f"{warm_up_minutes} min"
            ),
            (
                f"{repetitions}×"
                f"{work_minutes} min "
                "at LT2"
            ),
            (
                "Recover "
                f"{recovery_minutes} min "
                "easy between repetitions"
            ),
            (
                "Cool down "
                f"{cool_down_minutes} min"
            ),
        )

    @staticmethod
    def _adapted_hill_structure(
        *,
        workout: PlannedWorkout,
        total_minutes: int,
    ) -> tuple[str, ...]:
        """
        Preserves an explicit hill-repetition prescription
        when a hill session is shortened.
        """

        original_structure = tuple(
            str(step).strip()
            for step in workout.structure
            if str(step).strip()
        )

        repetition_minutes = 3
        recovery_minutes = 2

        for step in original_structure:

            normalized = step.lower()

            if (
                "×" in step
                and "min uphill" in normalized
            ):

                try:
                    interval_part = (
                        normalized
                        .split("×", 1)[1]
                        .split("min uphill", 1)[0]
                        .strip()
                    )

                    repetition_minutes = max(
                        1,
                        int(
                            interval_part
                            .split()[-1]
                        ),
                    )

                except (
                    ValueError,
                    IndexError,
                ):
                    pass

            if (
                normalized.startswith(
                    "recover "
                )
                and " min " in normalized
            ):

                try:
                    recovery_minutes = max(
                        1,
                        int(
                            normalized
                            .split(
                                "recover ",
                                1,
                            )[1]
                            .split(
                                " min",
                                1,
                            )[0]
                        ),
                    )

                except (
                    ValueError,
                    IndexError,
                ):
                    pass

        warm_up_minutes = min(
            10,
            max(
                7,
                total_minutes // 4,
            ),
        )

        cool_down_minutes = min(
            5,
            max(
                4,
                total_minutes // 8,
            ),
        )

        available_minutes = max(
            1,
            (
                total_minutes
                - warm_up_minutes
                - cool_down_minutes
            ),
        )

        repetition_block = (
            repetition_minutes
            + recovery_minutes
        )

        repetitions = max(
            3,
            (
                available_minutes
                + recovery_minutes
            )
            // repetition_block,
        )

        while (
            repetitions > 3
            and (
                repetitions
                * repetition_minutes
                + (
                    repetitions - 1
                )
                * recovery_minutes
            )
            > available_minutes
        ):
            repetitions -= 1

        prescribed_main_minutes = (
            repetitions
            * repetition_minutes
            + (
                repetitions - 1
            )
            * recovery_minutes
        )

        remaining_minutes = max(
            0,
            (
                total_minutes
                - prescribed_main_minutes
                - cool_down_minutes
            ),
        )

        warm_up_minutes = max(
            5,
            remaining_minutes,
        )

        return (
            f"Warm up {warm_up_minutes} min",
            (
                f"{repetitions}×"
                f"{repetition_minutes} min uphill"
            ),
            (
                f"Recover {recovery_minutes} min "
                "easy downhill between repetitions"
            ),
            f"Cool down {cool_down_minutes} min",
        )


    @staticmethod
    def _adapted_vo2_structure(
        total_minutes: int,
    ) -> tuple[str, ...]:
        """
        Builds an executable VO2max interval session.
        """

        repetition_minutes = 3
        recovery_minutes = 2

        warm_up_minutes = min(
            12,
            max(
                8,
                total_minutes // 4,
            ),
        )

        cool_down_minutes = min(
            8,
            max(
                5,
                total_minutes // 7,
            ),
        )

        available_minutes = max(
            1,
            (
                total_minutes
                - warm_up_minutes
                - cool_down_minutes
            ),
        )

        repetitions = max(
            2,
            (
                available_minutes
                + recovery_minutes
            )
            // (
                repetition_minutes
                + recovery_minutes
            ),
        )

        return (
            f"Warm up {warm_up_minutes} min",
            (
                f"{repetitions}×"
                f"{repetition_minutes} min "
                "at VO₂max effort"
            ),
            (
                f"Recover {recovery_minutes} min "
                "easy between repetitions"
            ),
            f"Cool down {cool_down_minutes} min",
        )


    @staticmethod
    def _adapted_speed_structure(
        total_minutes: int,
    ) -> tuple[str, ...]:
        """
        Builds an executable short-speed prescription.
        """

        warm_up_minutes = min(
            10,
            max(
                7,
                total_minutes // 4,
            ),
        )

        cool_down_minutes = min(
            5,
            max(
                4,
                total_minutes // 8,
            ),
        )

        available_minutes = max(
            2,
            (
                total_minutes
                - warm_up_minutes
                - cool_down_minutes
            ),
        )

        repetitions = max(
            4,
            min(
                10,
                available_minutes // 2,
            ),
        )

        return (
            f"Warm up {warm_up_minutes} min",
            (
                f"{repetitions}×30 sec fast"
            ),
            (
                "Recover 90 sec easy "
                "after each repetition"
            ),
            f"Cool down {cool_down_minutes} min",
        )
    
    @staticmethod
    def _adapted_structure(
        *,
        workout: PlannedWorkout,
        duration,
        main_label: str,
    ) -> tuple[str, ...]:
        """
        Builds an executable prescription for an adapted
        workout while preserving the session's key stimulus.

        Interval sessions retain explicit repetitions and
        recoveries instead of being reduced to one generic
        main-work block.
        """

        total_minutes = max(
            1,
            round(
                duration.total_seconds()
                / 60
            ),
        )

        description = (
            TrainingPlanAdapter
            ._description(
                workout
            )
        )

        target_guidance = tuple(
            step
            for step in workout.structure
            if str(
                step
            ).strip().lower().startswith(
                (
                    "heart rate target:",
                    "power target:",
                    "pace target:",
                )
            )
        )

        if total_minutes <= 15:

            timed_steps = (
                (
                    f"{main_label} "
                    f"{total_minutes} min"
                ),
            )

            return (
                *timed_steps,
                *target_guidance,
            )

        if any(
            token in description
            for token in (
                "lt2",
                "threshold",
            )
        ):
            timed_steps = (
                TrainingPlanAdapter
                ._adapted_threshold_structure(
                    total_minutes
                )
            )

        elif "hill" in description:

            timed_steps = (
                TrainingPlanAdapter
                ._adapted_hill_structure(
                    workout=workout,
                    total_minutes=total_minutes,
                )
            )

        elif any(
            token in description
            for token in (
                "vo2",
                "vo₂",
            )
        ):
            timed_steps = (
                TrainingPlanAdapter
                ._adapted_vo2_structure(
                    total_minutes
                )
            )

        elif "speed" in description:

            timed_steps = (
                TrainingPlanAdapter
                ._adapted_speed_structure(
                    total_minutes
                )
            )

        else:

            warm_up_minutes = min(
                10,
                max(
                    5,
                    total_minutes // 4,
                ),
            )

            cool_down_minutes = min(
                5,
                max(
                    3,
                    total_minutes // 6,
                ),
            )

            main_minutes = max(
                1,
                (
                    total_minutes
                    - warm_up_minutes
                    - cool_down_minutes
                ),
            )

            timed_steps = (
                (
                    "Warm up "
                    f"{warm_up_minutes} min"
                ),
                (
                    f"{main_label} "
                    f"{main_minutes} min"
                ),
                (
                    "Cool down "
                    f"{cool_down_minutes} min"
                ),
            )

        return (
            *timed_steps,
            *target_guidance,
        )

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
                "recovery",
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