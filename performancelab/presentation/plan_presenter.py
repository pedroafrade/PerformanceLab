"""
PerformanceLab

Complete training-plan presenter.
"""

from collections import defaultdict
from datetime import date, timedelta
import re

from performancelab.training.load import (
    planned_weekly_load,
    planned_workout_load,
)
from performancelab.training.planning import (
    TrainingPlanAdaptation,
    WorkoutOutcomeStatus,
)
from .plan_models import (
    CompletePlanData,
    PlanAdaptationData,
    PlanChartPointData,
    PlanCurrentPhaseData,
    PlanPhaseData,
    PlanProgressionPointData,
    PlanWeekData,
    PlanWorkoutData,
)


class PlanPresenter:
    """
    Organizes a complete TrainingPlan into calendar weeks.
    """

    def __init__(
        self,
        *,
        plan,
        history,
    ) -> None:

        self.plan = plan
        self.history = history

    def _outcomes_by_workout(
        self,
        *,
        reference_day: date,
    ) -> dict[object, object]:
        """
        Indexes complete workout outcomes by planned workout.
        """

        return {
            outcome.planned_workout: outcome
            for outcome in (
                self.plan.assess_outcomes(
                    history=self.history,
                    reference_day=reference_day,
                )
            )
        }
    def _outcome_for_presented_workout(
        self,
        workout,
        outcomes,
    ):
        """
        Finds the domain outcome corresponding to one
        presentation workout.
        """

        domain_workout = next(
            (
                planned
                for planned in self.plan
                if (
                    planned.scheduled_at
                    == workout.scheduled_at
                    and (
                        planned.title
                        or ""
                    )
                    == (
                        workout.title
                        or ""
                    )
                )
            ),
            None,
        )

        if domain_workout is None:
            return None

        return outcomes.get(
            domain_workout
        )
    
    @staticmethod
    def _phase_objective(
        phase_name: str,
    ) -> str:
        """
        Returns a concise presentation objective
        for one training-plan phase.
        """

        objectives = {
            "Build": (
                "Develop sustainable training volume "
                "and aerobic durability."
            ),
            "Peak": (
                "Increase race-specific endurance "
                "and key-session quality."
            ),
            "Taper": (
                "Reduce fatigue while preserving "
                "race readiness."
            ),
            "Race": (
                "Execute the target event with "
                "freshness and specificity."
            ),
            "Transition": (
                "Recover from racing while maintaining "
                "gentle movement."
            ),
            "Regeneration": (
                "Restore physical and mental freshness "
                "before rebuilding."
            ),
        }

        return objectives.get(
            phase_name,
            (
                "Follow the planned sessions for "
                "the current phase."
            ),
        )

    @staticmethod
    def _phase_timeline_data(
        weeks,
        *,
        reference_day: date,
    ) -> tuple[PlanPhaseData, ...]:
        """
        Groups consecutive plan weeks into phases.
        """

        if not weeks:
            return ()

        phases = []

        phase_name = (
            weeks[0].phase
            or "Unassigned"
        )

        phase_start = (
            weeks[0].start_date
        )

        phase_end = (
            weeks[0].end_date
        )

        for week in weeks[1:]:

            week_phase = (
                week.phase
                or "Unassigned"
            )

            if week_phase == phase_name:

                phase_end = (
                    week.end_date
                )

                continue

            phases.append(
                PlanPhaseData(
                    name=phase_name,
                    start_date=phase_start,
                    end_date=phase_end,
                    is_current=(
                        phase_start
                        <= reference_day
                        <= phase_end
                    ),
                )
            )

            phase_name = week_phase
            phase_start = (
                week.start_date
            )
            phase_end = (
                week.end_date
            )

        phases.append(
            PlanPhaseData(
                name=phase_name,
                start_date=phase_start,
                end_date=phase_end,
                is_current=(
                    phase_start
                    <= reference_day
                    <= phase_end
                ),
            )
        )

        return tuple(
            phases
        )


    @staticmethod
    def _current_phase_data(
        weeks,
        *,
        reference_day: date,
    ) -> PlanCurrentPhaseData | None:
        """
        Builds the phase containing the reference day.
        """

        current_index = next(
            (
                index
                for index, week
                in enumerate(weeks)
                if (
                    week.start_date
                    <= reference_day
                    <= week.end_date
                )
            ),
            None,
        )

        if current_index is None:
            return None

        current_week = weeks[
            current_index
        ]

        phase_name = (
            current_week.phase
            or "Unassigned"
        )

        phase_start_index = (
            current_index
        )

        while (
            phase_start_index > 0
            and (
                weeks[
                    phase_start_index - 1
                ].phase
                == current_week.phase
            )
        ):
            phase_start_index -= 1

        phase_end_index = (
            current_index
        )

        while (
            phase_end_index
            < len(weeks) - 1
            and (
                weeks[
                    phase_end_index + 1
                ].phase
                == current_week.phase
            )
        ):
            phase_end_index += 1

        remaining_phase_weeks = (
            weeks[
                current_index:
                phase_end_index + 1
            ]
        )

        remaining_workouts = tuple(
            workout
            for week in remaining_phase_weeks
            for workout in week.workouts
            if (
                workout.scheduled_at.date()
                >= reference_day
            )
        )

        sessions_remaining = len(
            remaining_workouts
        )

        planned_load_remaining = sum(
            float(
                workout.planned_load
                or 0.0
            )
            for workout in remaining_workouts
        )

        longest_session_minutes = max(
            (
                round(
                    workout.duration
                    .total_seconds()
                    / 60
                )
                for workout in remaining_workouts
                if workout.duration is not None
            ),
            default=0,
        )

        return PlanCurrentPhaseData(
            name=phase_name,
            objective=(
                PlanPresenter
                ._phase_objective(
                    phase_name
                )
            ),
            start_date=(
                weeks[
                    phase_start_index
                ].start_date
            ),
            end_date=(
                weeks[
                    phase_end_index
                ].end_date
            ),
            weeks_remaining=(
                phase_end_index
                - current_index
                + 1
            ),
            sessions_remaining=(
                sessions_remaining
            ),
            planned_load_remaining=(
                planned_load_remaining
            ),
            longest_session_minutes=(
                longest_session_minutes
            ),
        )

    @staticmethod
    def _adaptation_reason(
        adaptation: TrainingPlanAdaptation,
    ) -> str:
        """
        Explains why a future session was adapted.
        """

        if (
            adaptation.load_difference
            is not None
            and adaptation.load_difference > 0
        ):
            return (
                "Completed load was higher than planned."
            )

        if (
            adaptation.load_difference
            is not None
            and adaptation.load_difference < 0
        ):
            return (
                "Completed load was lower than planned."
            )

        if (
            adaptation.trigger_status
            is WorkoutOutcomeStatus.MISSED
        ):
            return (
                "A missed session changed future training."
            )

        if (
            adaptation.trigger_status
            is WorkoutOutcomeStatus.SUBSTITUTE
        ):
            return (
                "A substitute activity changed future training."
            )

        return (
            "A modified session changed future training."
        )


    @staticmethod
    def _adaptation_prescription(
        workout,
    ) -> str | None:
        """
        Returns the most useful concise execution dose
        available for one planned workout.
        """

        if workout is None:
            return None

        interval_step = next(
            (
                str(step).strip()
                for step in getattr(
                    workout,
                    "structure",
                    (),
                )
                if (
                    str(step).strip()
                    and "×" in str(step)
                )
            ),
            None,
        )

        if interval_step:
            return interval_step

        prescription_summary = str(
            getattr(
                workout,
                "prescription_summary",
                "",
            )
            or ""
        ).strip()

        return (
            prescription_summary
            or None
        )


    def _adapted_workout(
        self,
        adaptation: TrainingPlanAdaptation,
    ):
        """
        Finds the current planned workout represented by
        an adaptation record.
        """

        return next(
            (
                workout
                for workout in self.plan
                if (
                    workout.day
                    == adaptation.workout_day
                    and (
                        workout.title
                        or ""
                    )
                    == adaptation.workout_title
                )
            ),
            None,
        )

    def _adaptation_data(
        self,
        adaptation: TrainingPlanAdaptation,
    ) -> PlanAdaptationData:
        """
        Converts one domain adaptation into UI data.

        Older persisted adaptations may not contain the
        revised prescription. In that case the current
        adapted workout provides a safe fallback.
        """

        adapted_workout = (
            self._adapted_workout(
                adaptation
            )
        )

        revised_prescription = (
            adaptation.revised_prescription
            or self._adaptation_prescription(
                adapted_workout
            )
        )

        return PlanAdaptationData(
            reconciled_on=(
                adaptation.reconciled_on
            ),
            workout_day=(
                adaptation.workout_day
            ),
            workout_title=(
                adaptation.workout_title
            ),
            previous_minutes=round(
                adaptation.previous_duration
                .total_seconds()
                / 60
            ),
            revised_minutes=round(
                adaptation.revised_duration
                .total_seconds()
                / 60
            ),
            reason=(
                PlanPresenter
                ._adaptation_reason(
                    adaptation
                )
            ),
            previous_distance=(
                adaptation.previous_distance
            ),
            revised_distance=(
                adaptation.revised_distance
            ),
            previous_elevation_gain=(
                adaptation.previous_elevation_gain
            ),
            revised_elevation_gain=(
                adaptation.revised_elevation_gain
            ),
            previous_prescription=(
                adaptation.previous_prescription
            ),
            revised_prescription=(
                revised_prescription
            ),
        )


    def _latest_adaptation_data(
        self,
    ) -> PlanAdaptationData | None:
        """
        Returns the most recently reconciled adaptation.
        """

        if not self.plan.adaptations:
            return None

        latest = max(
            self.plan.adaptations,
            key=lambda adaptation: (
                adaptation.reconciled_on,
                adaptation.workout_day,
            ),
        )

        return self._adaptation_data(
            latest
        )
    @staticmethod
    def _target_event_title(
        workout,
    ) -> str:
        """
        Returns the most specific available race name.
        """

        title = (
            PlanPresenter
            ._repair_text_encoding(
                workout.title
            )
            .strip()
        )

        if (
            title
            and title.lower()
            not in {
                "race",
                "competition",
                "event",
            }
        ):
            return title

        objective = (
            PlanPresenter
            ._repair_text_encoding(
                workout.objective
            )
            .strip()
        )

        match = re.search(
            (
                r"Perform effectively at "
                r"(.+?)(?:\.|$)"
            ),
            objective,
            flags=re.IGNORECASE,
        )

        if match is not None:

            event_title = (
                match.group(1)
                .strip()
            )

            print("OBJECTIVE:", repr(workout.objective))
            print("EVENT:", repr(event_title))

            if event_title:
                return event_title

        return title or "Race"


    def _target_event_data(
        self,
    ) -> tuple[
        str | None,
        date | None,
    ]:
        """
        Returns the final race in the domain plan.
        """

        races = tuple(
            workout
            for workout in self.plan
            if (
                str(
                    workout.intensity
                    or ""
                )
                .strip()
                .lower()
                == "race effort"
            )
        )

        if not races:
            return (
                None,
                None,
            )

        target_event = max(
            races,
            key=lambda workout: (
                workout.scheduled_at
            ),
        )

        return (
            self._target_event_title(
                target_event
            ),
            target_event.scheduled_at.date(),
        )
    
    def build(
        self,
        *,
        reference_day: date,
    ) -> CompletePlanData:
        """
        Builds the complete plan grouped by Monday-first weeks.
        """

        outcomes = (
            self._outcomes_by_workout(
                reference_day=reference_day
            )
        )

        workouts_by_week = defaultdict(
            list
        )

        for workout in self.plan:

            week_start = (
                workout.day
                - timedelta(
                    days=workout.day.weekday()
                )
            )

            workouts_by_week[
                week_start
            ].append(
                workout
            )

        weeks = []
        progression = []

        for week_start in sorted(
            workouts_by_week
        ):

            planned_workouts = tuple(
                sorted(
                    workouts_by_week[
                        week_start
                    ],
                    key=lambda workout: (
                        workout.scheduled_at
                    ),
                )
            )

            workout_data = tuple(
                PlanWorkoutData(
                    scheduled_at=(
                        workout.scheduled_at
                    ),
                    sport=workout.sport,
                    title=(
                        self._target_event_title(
                            workout
                        )
                        if (
                            str(
                                workout.intensity
                                or ""
                            )
                            .strip()
                            .lower()
                            == "race effort"
                        )
                        else (
                            workout.title
                            or "Planned workout"
                        )
                    ),
                    duration=workout.duration,
                    distance=workout.distance,
                    elevation_gain=(
                        workout.elevation_gain
                    ),
                    intensity=workout.intensity,
                    phase=workout.phase,
                    planned_load=(
                        planned_workout_load(
                            workout
                        )
                    ),
                    is_race=(
                        str(
                            workout.intensity
                            or ""
                        ).strip().lower()
                        == "race effort"
                    ),
                    status=(
                        outcomes[workout].status.value
                        if workout in outcomes
                        else "pending"
                    ),
                    prescription_summary=(
                        workout
                        .prescription_summary
                    ),
                    structure=tuple(
                        workout.structure
                    ),
                )
                for workout in planned_workouts
            )
            displayed_week_start = (
                max(
                    week_start,
                    self.plan.start_date,
                )
                if self.plan.start_date
                is not None
                else week_start
            )

            displayed_week_end = (
                min(
                    (
                        week_start
                        + timedelta(days=6)
                    ),
                    self.plan.end_date,
                )
                if self.plan.end_date
                is not None
                else (
                    week_start
                    + timedelta(days=6)
                )
            )

            phase = self.plan.phase_on(
                displayed_week_start
            )

            weekly_load = (
                planned_weekly_load(
                    planned_workouts
                )
            )

            duration_minutes = sum(
                (
                    workout.duration
                    .total_seconds()
                    / 60
                )
                for workout
                in planned_workouts
                if workout.duration
                is not None
            )

            distance = sum(
                float(
                    workout.distance
                )
                for workout
                in planned_workouts
                if isinstance(
                    workout.distance,
                    (int, float),
                )
                and not isinstance(
                    workout.distance,
                    bool,
                )
            )

            elevation_gain = sum(
                float(
                    workout.elevation_gain
                )
                for workout
                in planned_workouts
                if isinstance(
                    workout.elevation_gain,
                    (int, float),
                )
                and not isinstance(
                    workout.elevation_gain,
                    bool,
                )
            )

            weeks.append(
                PlanWeekData(
                    start_date=(
                        displayed_week_start
                    ),
                    end_date=(
                        displayed_week_end
                    ),
                    phase=phase,
                    planned_load=(
                        weekly_load
                    ),
                    workouts=(
                        workout_data
                    ),
                )
            )

            progression.append(
                PlanProgressionPointData(
                    week_start=week_start,
                    phase=phase,
                    planned_load=(
                        weekly_load
                    ),
                    duration_minutes=(
                        duration_minutes
                    ),
                    distance=distance,
                    elevation_gain=(
                        elevation_gain
                    ),
                )
            )

        weeks_data = tuple(
            weeks
        )

        chart_points = tuple(
            PlanChartPointData(
                day=(
                    workout.scheduled_at.date()
                ),
                title=workout.title,
                phase=workout.phase,
                planned_load=(
                    workout.planned_load
                ),
                completed_load=(
                    outcome.completed_load
                    if (
                        outcome := (
                            self
                            ._outcome_for_presented_workout(
                                workout,
                                outcomes,
                            )
                        )
                    )
                    else None
                ),
                distance=workout.distance,
                elevation_gain=(
                    workout.elevation_gain
                ),
                duration=workout.duration,
                intensity=workout.intensity,
                is_race=workout.is_race,
                status=workout.status,
            )
            for week in weeks_data
            for workout in week.workouts
        )
        (
            target_event_title,
            target_event_date,
        ) = self._target_event_data()
        return CompletePlanData(
            plan_id=self.plan.plan_id,
            start_date=self.plan.start_date,
            end_date=self.plan.end_date,
            reference_day=reference_day,
            weeks=weeks_data,
            chart_points=chart_points,
            progression=tuple(
                progression
            ),
            phases=(
                self._phase_timeline_data(
                    weeks_data,
                    reference_day=(
                        reference_day
                    ),
                )
            ),
            current_phase=(
                self._current_phase_data(
                    weeks_data,
                    reference_day=(
                        reference_day
                    ),
                )
            ),
            target_event_title=(
                target_event_title
            ),
            target_event_date=(
                target_event_date
            ),
            latest_adaptation=(
                self._latest_adaptation_data()
            ),
        )

    @staticmethod
    def _repair_text_encoding(
        value: str | None,
    ) -> str:
        """
        Repairs common UTF-8 mojibake in persisted text.
        """

        text = str(
            value
            or ""
        )

        if not text:
            return text

        mojibake_markers = (
            "Ã",
            "Â",
            "â€",
            "â€“",
            "â€”",
        )

        if not any(
            marker in text
            for marker in mojibake_markers
        ):
            return text

        try:
            return (
                text
                .encode("latin-1")
                .decode("utf-8")
            )

        except (
            UnicodeEncodeError,
            UnicodeDecodeError,
        ):
            return text