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
from .stimulus_rebalancer import (
    StimulusRebalancer,
)
from .plan_revision import TrainingPlanRevision


MAX_OVERLOAD_DURATION_REDUCTION = 0.20
OVERLOAD_RESPONSE_FRACTION = 0.25
MAX_UNDERLOAD_DURATION_INCREASE = 0.05
UNDERLOAD_RECOVERY_FRACTION = 0.25
STIMULUS_RECOVERY_REDUCTION = 0.15
MINIMUM_QUALITY_RECOVERY_DAYS = 3


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

        adaptation_deadline = (
            self._adaptation_deadline(
                workouts=workouts,
                reference_day=reference_day,
            )
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
                self._reduce_future_demanding_workouts(
                    workouts=workouts,
                    reference_day=reference_day,
                    adaptation_deadline=(
                        adaptation_deadline
                    ),
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
                self._increase_future_easy_workouts(
                    workouts=workouts,
                    reference_day=reference_day,
                    adaptation_deadline=(
                        adaptation_deadline
                    ),
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
        stimulus_suggestions = (
            StimulusRebalancer()
            .suggest(
                workouts=tuple(
                    workouts
                ),
                outcomes=outcomes,
                training_state=training_state,
                reference_day=reference_day,
            )
        )

        (
            workouts,
            stimulus_suggestions,
        ) = self._apply_stimulus_suggestions(
            workouts=workouts,
            suggestions=(
                stimulus_suggestions
            ),
        )

        workouts = (
            self._rebalance_recovery_after_stimulus(
                workouts=workouts,
                suggestions=stimulus_suggestions,
                adaptation_deadline=(
                    adaptation_deadline
                ),
            )
        )

        merged_stimulus_suggestions = (
            self._merge_stimulus_suggestions(
                existing=(
                    plan.stimulus_suggestions
                ),
                new=(
                    stimulus_suggestions
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

        revisions, active_revision_id = (
            self._revision_history(
                plan=plan,
                original_workouts=original_workouts,
                revised_workouts=tuple(workouts),
                reference_day=reference_day,
            )
        )

        combined_adaptations = (
            plan.adaptations
            + adaptation_records
        )
        if tuple(original_workouts) != tuple(workouts):
            revisions = tuple(
                replace(
                    revision,
                    adaptations=combined_adaptations,
                    stimulus_suggestions=merged_stimulus_suggestions,
                )
                if revision.revision_id == active_revision_id
                else revision
                for revision in revisions
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
            adaptations=combined_adaptations,
            stimulus_suggestions=(
                merged_stimulus_suggestions
            ),
            original_workouts=(
                plan.original_workouts
                or original_workouts
            ),
            revisions=revisions,
            active_revision_id=active_revision_id,
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
    def _revision_history(
        *,
        plan: TrainingPlan,
        original_workouts,
        revised_workouts,
        reference_day: date,
    ):
        """Records complete recoverable plan snapshots."""

        existing = plan.revisions

        if tuple(original_workouts) == tuple(revised_workouts):
            return existing, plan.active_revision_id

        if existing:
            parent_revision_id = (
                plan.active_revision_id
                or existing[-1].revision_id
            )
            revisions = existing
        else:
            baseline = TrainingPlanRevision(
                created_on=(
                    plan.start_date
                    or reference_day
                ),
                source="generated",
                workouts=tuple(original_workouts),
                reason="Initial generated plan.",
                start_date=plan.start_date,
                end_date=plan.end_date,
                primary_event_id=plan.primary_event_id,
                competition_event_ids=plan.competition_event_ids,
                adaptations=(),
                stimulus_suggestions=(),
            )
            parent_revision_id = baseline.revision_id
            revisions = (baseline,)

        adapted_revision = TrainingPlanRevision(
            created_on=reference_day,
            source="automatic_adaptation",
            workouts=tuple(revised_workouts),
            reason=(
                "Training outcomes changed the remaining "
                "plan before the next race."
            ),
            parent_revision_id=parent_revision_id,
            start_date=plan.start_date,
            end_date=plan.end_date,
            events=(
                next(
                    (
                        revision.events
                        for revision in reversed(revisions)
                        if revision.events is not None
                    ),
                    None,
                )
            ),
            primary_event_id=plan.primary_event_id,
            competition_event_ids=plan.competition_event_ids,
        )

        return (
            (*revisions, adapted_revision),
            adapted_revision.revision_id,
        )

    # ======================================================
    @staticmethod
    def _rebalance_recovery_after_stimulus(
        *,
        workouts,
        suggestions,
        adaptation_deadline,
    ):
        """
        Rechecks the remaining quality sequence after an
        applied stimulus substitution.

        A later unprotected quality session less than three
        calendar days away is shortened conservatively.
        Long runs, taper, races and recovery remain intact.
        """

        applied_days = tuple(
            sorted(
                suggestion.candidate_workout_day
                for suggestion in suggestions
                if suggestion.applied
            )
        )

        if not applied_days:
            return list(workouts)

        updated = list(workouts)

        for applied_day in applied_days:
            next_quality_index = next(
                (
                    index
                    for index, workout
                    in enumerate(updated)
                    if (
                        workout.day > applied_day
                        and (
                            adaptation_deadline is None
                            or workout.day < adaptation_deadline
                        )
                        and (
                            workout.day - applied_day
                        ).days
                        < MINIMUM_QUALITY_RECOVERY_DAYS
                        and workout.duration is not None
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

            if next_quality_index is None:
                continue

            candidate = updated[next_quality_index]
            revised_duration = (
                candidate.duration
                * (1.0 - STIMULUS_RECOVERY_REDUCTION)
            )
            factor = (
                revised_duration.total_seconds()
                / candidate.duration.total_seconds()
            )

            updated[next_quality_index] = replace(
                candidate,
                duration=revised_duration,
                distance=(
                    TrainingPlanAdapter._scaled_metric(
                        candidate.distance,
                        factor=factor,
                    )
                ),
                elevation_gain=(
                    TrainingPlanAdapter._scaled_metric(
                        candidate.elevation_gain,
                        factor=factor,
                    )
                ),
                structure=(
                    TrainingPlanAdapter._adapted_structure(
                        workout=candidate,
                        duration=revised_duration,
                        main_label="Controlled quality work",
                    )
                ),
                prescription_summary=(
                    "Reduced to protect recovery after "
                    "stimulus rebalancing."
                ),
            )

        return updated

    # ======================================================
    @staticmethod
    def _apply_stimulus_suggestions(
        *,
        workouts,
        suggestions,
    ):
        """
        Applies safe stimulus substitutions to an existing
        future quality slot.

        Duration and calendar position are preserved. Long
        sessions, taper, races and recovery are already
        excluded by StimulusRebalancer.
        """

        revised_workouts = list(
            workouts
        )
        applied_suggestions = []

        stimulus_titles = {
            "hills": "Hill Reps",
            "threshold": "LT2 Run",
            "tempo": "Tempo Run",
            "vo2max": "VO2max Intervals",
            "speed": "Speed Reps",
        }

        stimulus_intensities = {
            "hills": "Hard",
            "threshold": "LT2",
            "tempo": "Tempo",
            "vo2max": "VO2max",
            "speed": "Fast",
        }

        for suggestion in suggestions:

            candidate_index = next(
                (
                    index
                    for index, workout
                    in enumerate(
                        revised_workouts
                    )
                    if (
                        workout.day
                        == suggestion
                        .candidate_workout_day
                    )
                ),
                None,
            )

            source_workout = next(
                (
                    workout
                    for workout in workouts
                    if (
                        workout.day
                        == suggestion
                        .source_workout_day
                    )
                ),
                None,
            )

            if (
                candidate_index is None
                or source_workout is None
            ):
                applied_suggestions.append(
                    suggestion
                )
                continue

            candidate = revised_workouts[
                candidate_index
            ]

            stimulus_name = (
                suggestion.missing_stimulus
                .value
            )

            revised_title = (
                stimulus_titles.get(
                    stimulus_name,
                    source_workout.title
                    or candidate.title
                    or "Quality session",
                )
            )

            revised_intensity = (
                stimulus_intensities.get(
                    stimulus_name,
                    source_workout.intensity
                    or candidate.intensity,
                )
            )

            provisional_workout = replace(
                candidate,
                structure=(
                    source_workout.structure
                    or candidate.structure
                ),
                title=revised_title,
                description=(
                    source_workout.description
                    or (
                        f"Adapted {stimulus_name} "
                        "session"
                    )
                ),
                intensity=revised_intensity,
                objective=(
                    source_workout.objective
                    or (
                        f"Restore the missed "
                        f"{stimulus_name} stimulus."
                    )
                ),
                purpose="intensity",
                focus=stimulus_name,
            )

            revised_structure = (
                TrainingPlanAdapter
                ._adapted_structure(
                    workout=(
                        provisional_workout
                    ),
                    duration=(
                        candidate.duration
                    ),
                    main_label=(
                        revised_title
                    ),
                )
                if candidate.duration
                is not None
                else candidate.structure
            )

            revised_workout = replace(
                provisional_workout,
                structure=(
                    revised_structure
                ),
                prescription_summary=(
                    f"{revised_title} adapted "
                    f"from missed "
                    f"{suggestion.source_workout_title}"
                ),
            )

            revised_workouts[
                candidate_index
            ] = revised_workout

            applied_suggestions.append(
                replace(
                    suggestion,
                    recommendation=(
                        f"{suggestion.candidate_workout_title} "
                        f"on "
                        f"{suggestion.candidate_workout_day:%d %b} "
                        f"was changed to "
                        f"{revised_title}."
                    ),
                    applied=True,
                )
            )

        return (
            revised_workouts,
            tuple(
                applied_suggestions
            ),
        )

    @staticmethod
    def _merge_stimulus_suggestions(
        *,
        existing,
        new,
    ):
        """
        Merges stimulus adaptations without duplicating the
        same source and candidate session.

        An applied version replaces an older pending version.
        """

        suggestions_by_key = {}

        for suggestion in (
            *existing,
            *new,
        ):

            key = (
                suggestion.source_workout_day,
                suggestion.missing_stimulus,
                suggestion.candidate_workout_day,
            )

            current = (
                suggestions_by_key.get(
                    key
                )
            )

            if (
                current is None
                or (
                    suggestion.applied
                    and not current.applied
                )
            ):
                suggestions_by_key[
                    key
                ] = suggestion

        return tuple(
            suggestions_by_key.values()
        )

    # ======================================================

    @staticmethod
    def _scaled_metric(
        value: float | None,
        *,
        factor: float,
    ) -> float | None:
        """
        Scales a planned distance or elevation value while
        preserving missing metrics.
        """

        if value is None:
            return None

        return round(
            float(value)
            * factor,
            1,
        )


    @staticmethod
    def _workout_dose(
        workout: PlannedWorkout,
    ) -> str | None:
        """
        Returns the most useful concise workout dose.

        Interval prescriptions take priority over generic
        summary text.
        """

        interval_step = next(
            (
                str(step).strip()
                for step in workout.structure
                if (
                    str(step).strip()
                    and "×" in str(step)
                )
            ),
            None,
        )

        if interval_step:
            return interval_step

        summary = str(
            workout.prescription_summary
            or ""
        ).strip()

        return (
            summary
            or None
        )

    
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
        Records the before/after prescription of every
        adapted future session.
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

            if not candidates:
                candidates = (
                    overload_outcomes
                    + underload_outcomes
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
                    previous_distance=(
                        original.distance
                    ),
                    revised_distance=(
                        revised.distance
                    ),
                    previous_elevation_gain=(
                        original.elevation_gain
                    ),
                    revised_elevation_gain=(
                        revised.elevation_gain
                    ),
                    previous_prescription=(
                        TrainingPlanAdapter
                        ._workout_dose(
                            original
                        )
                    ),
                    revised_prescription=(
                        TrainingPlanAdapter
                        ._workout_dose(
                            revised
                        )
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
    def _reduce_future_demanding_workouts(
        *,
        workouts: list[PlannedWorkout],
        reference_day: date,
        adaptation_deadline: date | None,
        reduction_fraction: float,
    ) -> list[PlannedWorkout]:
        """
        Reduces every eligible demanding session remaining
        in the active block.

        The same bounded response is applied consistently
        across quality sessions before the next race. Taper,
        competition and recovery sessions remain protected.
        """

        updated = list(
            workouts
        )

        candidate_indices = [
            index
            for index, workout
            in enumerate(updated)
            if (
                workout.day > reference_day
                and (
                    adaptation_deadline is None
                    or workout.day
                    < adaptation_deadline
                )
                and workout.duration is not None
                and workout.duration.total_seconds() > 0
                and TrainingPlanAdapter._is_demanding(
                    workout
                )
                and not TrainingPlanAdapter._is_protected(
                    workout
                )
            )
        ]

        for candidate_index in candidate_indices:

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

            duration_factor = (
                adjusted_duration.total_seconds()
                / candidate.duration.total_seconds()
            )

            adjusted_distance = (
                TrainingPlanAdapter
                ._scaled_metric(
                    candidate.distance,
                    factor=duration_factor,
                )
            )

            adjusted_elevation_gain = (
                TrainingPlanAdapter
                ._scaled_metric(
                    candidate.elevation_gain,
                    factor=duration_factor,
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
                distance=adjusted_distance,
                elevation_gain=(
                    adjusted_elevation_gain
                ),
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
    def _increase_future_easy_workouts(
        *,
        workouts: list[PlannedWorkout],
        reference_day: date,
        adaptation_deadline: date | None,
        missing_load: float | None,
        preferred_sport_families: tuple[
            str,
            ...,
        ] = (),
    ) -> list[PlannedWorkout]:
        """
        Distributes a bounded part of known missing load
        across eligible easy sessions in the active block.

        Sessions from the planned sport family are preferred.
        When missing load is unknown, only the first safe
        session receives the conservative maximum increase.
        """

        updated = list(
            workouts
        )

        candidate_indices = [
            index
            for index, workout
            in enumerate(updated)
            if (
                workout.day > reference_day
                and (
                    adaptation_deadline is None
                    or workout.day
                    < adaptation_deadline
                )
                and workout.duration is not None
                and workout.duration.total_seconds() > 0
                and TrainingPlanAdapter._is_easy(
                    workout
                )
                and not TrainingPlanAdapter._is_protected(
                    workout
                )
            )
        ]

        preferred_indices = [
            index
            for index in candidate_indices
            if (
                TrainingPlanAdapter
                ._sport_family(
                    updated[index].sport
                )
                in preferred_sport_families
            )
        ]

        if preferred_indices:
            candidate_indices = (
                preferred_indices
            )

        if not candidate_indices:
            return updated

        remaining_recoverable_load = (
            (
                missing_load
                * UNDERLOAD_RECOVERY_FRACTION
            )
            if missing_load is not None
            else None
        )

        if remaining_recoverable_load is None:
            candidate_indices = (
                candidate_indices[:1]
            )

        for candidate_index in candidate_indices:

            if (
                remaining_recoverable_load
                is not None
                and remaining_recoverable_load
                <= 0
            ):
                break

            candidate = updated[
                candidate_index
            ]

            candidate_load = (
                planned_workout_load(
                    candidate
                )
            )

            if (
                remaining_recoverable_load
                is not None
            ):

                if (
                    candidate_load is None
                    or candidate_load <= 0
                ):
                    continue

                increase_fraction = min(
                    MAX_UNDERLOAD_DURATION_INCREASE,
                    (
                        remaining_recoverable_load
                        / candidate_load
                    ),
                )

            else:

                increase_fraction = (
                    MAX_UNDERLOAD_DURATION_INCREASE
                )

            if increase_fraction <= 0:
                continue

            adjusted_duration = (
                candidate.duration
                * (
                    1.0
                    + increase_fraction
                )
            )

            duration_factor = (
                adjusted_duration.total_seconds()
                / candidate.duration.total_seconds()
            )

            adjusted_distance = (
                TrainingPlanAdapter
                ._scaled_metric(
                    candidate.distance,
                    factor=duration_factor,
                )
            )

            adjusted_elevation_gain = (
                TrainingPlanAdapter
                ._scaled_metric(
                    candidate.elevation_gain,
                    factor=duration_factor,
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
                distance=adjusted_distance,
                elevation_gain=(
                    adjusted_elevation_gain
                ),
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

            if (
                remaining_recoverable_load
                is not None
                and candidate_load is not None
            ):
                remaining_recoverable_load = max(
                    0.0,
                    (
                        remaining_recoverable_load
                        - (
                            candidate_load
                            * increase_fraction
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
        Transfers the explicit hill-repetition dose from the
        missed session.

        Repetitions, work duration and recovery duration are
        preserved whenever they fit safely in the new slot.
        Only preparation and cool-down time are adjusted.
        """

        original_structure = tuple(
            str(step).strip()
            for step in workout.structure
            if str(step).strip()
        )

        explicit_repetitions = None
        repetition_minutes = 3
        recovery_minutes = 2

        for step in original_structure:

            normalized = step.lower()

            if (
                "×" in step
                and "min uphill" in normalized
            ):

                try:
                    repetitions_part = (
                        normalized
                        .split("×", 1)[0]
                        .strip()
                        .split()[-1]
                    )

                    explicit_repetitions = max(
                        1,
                        int(
                            repetitions_part
                        ),
                    )

                except (
                    ValueError,
                    IndexError,
                ):
                    explicit_repetitions = None

                try:
                    interval_part = (
                        normalized
                        .split("×", 1)[1]
                        .split(
                            "min uphill",
                            1,
                        )[0]
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

        cool_down_minutes = min(
            8,
            max(
                5,
                total_minutes // 8,
            ),
        )

        available_minutes = max(
            1,
            (
                total_minutes
                - cool_down_minutes
                - 5
            ),
        )

        if explicit_repetitions is not None:

            repetitions = (
                explicit_repetitions
            )

        else:

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

        def main_block_minutes(
            repetition_count,
        ):

            return (
                repetition_count
                * repetition_minutes
                + (
                    repetition_count - 1
                )
                * recovery_minutes
            )

        # Reduce the dose only when the original prescription
        # cannot physically fit in the future session.
        while (
            repetitions > 1
            and main_block_minutes(
                repetitions
            )
            > available_minutes
        ):
            repetitions -= 1

        prescribed_main_minutes = (
            main_block_minutes(
                repetitions
            )
        )

        warm_up_minutes = max(
            5,
            (
                total_minutes
                - prescribed_main_minutes
                - cool_down_minutes
            ),
        )

        return (
            (
                f"Warm up "
                f"{warm_up_minutes} min"
            ),
            (
                f"{repetitions}×"
                f"{repetition_minutes} min uphill"
            ),
            (
                f"Recover {recovery_minutes} min "
                "easy downhill between repetitions"
            ),
            (
                f"Cool down "
                f"{cool_down_minutes} min"
            ),
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
    def _adaptation_deadline(
        *,
        workouts: list[PlannedWorkout],
        reference_day: date,
    ) -> date | None:
        """
        Returns the next competition day.

        An outcome from the current training block must not
        alter taper, competition or post-race recovery in a
        later block.
        """

        competition_days = tuple(
            workout.day
            for workout in workouts
            if (
                workout.day > reference_day
                and (
                    str(
                        workout.phase or ""
                    ).strip().lower()
                    == "race"
                    or str(
                        workout.title or ""
                    ).strip().lower()
                    == "race"
                )
            )
        )

        return (
            min(competition_days)
            if competition_days
            else None
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
            "recovery",
            "regeneration",
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
