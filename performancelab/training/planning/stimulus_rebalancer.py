"""
PerformanceLab

Stimulus rebalancing suggestions.

Produces explainable proposals without changing the
persistent training plan.
"""

from dataclasses import dataclass
from datetime import date, timedelta

from .planned_workout import (
    PlannedWorkout,
)
from .workout_stimulus import (
    WorkoutStimulus,
    planned_workout_stimulus,
)


REBALANCEABLE_STIMULI = {
    WorkoutStimulus.HILLS,
    WorkoutStimulus.THRESHOLD,
    WorkoutStimulus.TEMPO,
    WorkoutStimulus.VO2MAX,
    WorkoutStimulus.SPEED,
}

MINIMUM_DAYS_BEFORE_RACE = 3


@dataclass(
    frozen=True,
    slots=True,
)
class StimulusRebalanceSuggestion:
    """
    One non-destructive proposed stimulus substitution.
    """

    created_on: date

    source_workout_day: date
    source_workout_title: str

    missing_stimulus: WorkoutStimulus
    completed_stimulus: WorkoutStimulus

    candidate_workout_day: date
    candidate_workout_title: str
    candidate_stimulus: WorkoutStimulus

    recommendation: str
    rationale: str

    applied: bool = False


class StimulusRebalancer:
    """
    Finds safe opportunities to recover a missing stimulus.

    Suggestions never mutate the plan and require explicit
    athlete confirmation before they can be applied.
    """

    def suggest(
        self,
        *,
        workouts: tuple[
            PlannedWorkout,
            ...,
        ]
        | list[
            PlannedWorkout
        ],
        outcomes,
        training_state,
        reference_day: date,
    ) -> tuple[
        StimulusRebalanceSuggestion,
        ...,
    ]:
        """
        Returns conservative stimulus substitutions before
        the next race.
        """

        if not isinstance(
            reference_day,
            date,
        ):
            raise TypeError(
                "reference_day must be a date."
            )

        if not getattr(
            training_state,
            "can_tolerate_intensity",
            False,
        ):
            return ()
        outcomes = tuple(
            outcomes
        )
        ordered_workouts = tuple(
            sorted(
                workouts,
                key=lambda workout: (
                    workout.scheduled_at
                ),
            )
        )

        race_day = self._next_race_day(
            workouts=ordered_workouts,
            reference_day=reference_day,
        )

        used_candidate_days = set()
        suggestions = []

        for outcome in sorted(
            outcomes,
            key=lambda item: (
                item.planned_workout.day
            ),
        ):

            if not getattr(
                outcome,
                "has_stimulus_gap",
                False,
            ):
                continue

            missing_stimulus = (
                outcome.planned_stimulus
            )

            if (
                missing_stimulus
                not in REBALANCEABLE_STIMULI
            ):
                continue

            if self._stimulus_was_recovered(
                outcomes=outcomes,
                missing_stimulus=(
                    missing_stimulus
                ),
                source_day=(
                    outcome.planned_workout.day
                ),
                reference_day=reference_day,
            ):
                continue

            candidate = (
                self._candidate_workout(
                    workouts=ordered_workouts,
                    missing_stimulus=(
                        missing_stimulus
                    ),
                    source_workout=(
                        outcome.planned_workout
                    ),
                    reference_day=(
                        reference_day
                    ),
                    race_day=race_day,
                    used_candidate_days=(
                        used_candidate_days
                    ),
                )
            )

            if candidate is None:
                continue

            used_candidate_days.add(
                candidate.day
            )

            candidate_stimulus = (
                planned_workout_stimulus(
                    candidate
                )
            )

            suggestions.append(
                StimulusRebalanceSuggestion(
                    created_on=reference_day,
                    source_workout_day=(
                        outcome
                        .planned_workout
                        .day
                    ),
                    source_workout_title=(
                        outcome
                        .planned_workout
                        .title
                        or "Planned workout"
                    ),
                    missing_stimulus=(
                        missing_stimulus
                    ),
                    completed_stimulus=(
                        outcome
                        .completed_stimulus
                    ),
                    candidate_workout_day=(
                        candidate.day
                    ),
                    candidate_workout_title=(
                        candidate.title
                        or "Quality session"
                    ),
                    candidate_stimulus=(
                        candidate_stimulus
                    ),
                    recommendation=(
                        self._recommendation(
                            missing_stimulus=(
                                missing_stimulus
                            ),
                            candidate=(
                                candidate
                            ),
                        )
                    ),
                    rationale=(
                        self._rationale(
                            missing_stimulus=(
                                missing_stimulus
                            ),
                            completed_stimulus=(
                                outcome
                                .completed_stimulus
                            ),
                            candidate_stimulus=(
                                candidate_stimulus
                            ),
                            race_day=race_day,
                        )
                    ),
                )
            )

        return tuple(
            suggestions
        )

    @staticmethod
    def _stimulus_was_recovered(
        *,
        outcomes,
        missing_stimulus: WorkoutStimulus,
        source_day: date,
        reference_day: date,
    ) -> bool:
        """
        Returns True when the missing stimulus was completed
        later, before or on the current reference day.

        This prevents an already recovered physiological
        stimulus from being prescribed again unnecessarily.
        """

        return any(
            (
                outcome.planned_workout.day
                > source_day
            )
            and (
                outcome.planned_workout.day
                <= reference_day
            )
            and (
                getattr(
                    outcome,
                    "completed_stimulus",
                    WorkoutStimulus.UNKNOWN,
                )
                is missing_stimulus
            )
            for outcome in outcomes
        )

    @staticmethod
    def _candidate_workout(
        *,
        workouts,
        missing_stimulus: WorkoutStimulus,
        source_workout: PlannedWorkout,
        reference_day: date,
        race_day: date | None,
        used_candidate_days: set[date],
    ) -> PlannedWorkout | None:
        """
        Finds an existing future intensity slot.

        Long sessions are intentionally excluded: replacing
        endurance with intensity requires a separate athlete
        decision and stronger evidence.
        """

        source_sport_family = (
            StimulusRebalancer
            ._sport_family(
                source_workout.sport
            )
        )

        candidates = []

        for workout in workouts:

            if workout.day <= reference_day:
                continue

            if workout.day in used_candidate_days:
                continue

            if (
                race_day is not None
                and workout.day
                > (
                    race_day
                    - timedelta(
                        days=(
                            MINIMUM_DAYS_BEFORE_RACE
                        )
                    )
                )
            ):
                continue

            candidate_stimulus = (
                planned_workout_stimulus(
                    workout
                )
            )

            purpose = str(
                workout.purpose or ""
            ).strip().lower()

            is_intensity_slot = (
                purpose == "intensity"
                or (
                    not purpose
                    and candidate_stimulus
                    in REBALANCEABLE_STIMULI
                )
            )

            if not is_intensity_slot:
                continue

            if (
                StimulusRebalancer
                ._is_protected(
                    workout
                )
            ):
                continue

            if (
                StimulusRebalancer
                ._sport_family(
                    workout.sport
                )
                != source_sport_family
            ):
                continue

            if (
                candidate_stimulus
                not in REBALANCEABLE_STIMULI
                or candidate_stimulus
                is missing_stimulus
            ):
                continue

            candidates.append(
                workout
            )

        return (
            min(
                candidates,
                key=lambda workout: (
                    workout.day
                ),
            )
            if candidates
            else None
        )

    @staticmethod
    def _next_race_day(
        *,
        workouts,
        reference_day: date,
    ) -> date | None:
        """
        Returns the next explicit competition day.
        """

        race_days = tuple(
            workout.day
            for workout in workouts
            if (
                workout.day > reference_day
                and (
                    str(
                        workout.purpose or ""
                    ).strip().lower()
                    == "race"
                    or (
                        planned_workout_stimulus(
                            workout
                        )
                        is WorkoutStimulus.RACE
                    )
                )
            )
        )

        return (
            min(race_days)
            if race_days
            else None
        )

    @staticmethod
    def _is_protected(
        workout: PlannedWorkout,
    ) -> bool:
        """
        Protects taper, race and post-race recovery.
        """

        phase = str(
            workout.phase or ""
        ).strip().lower()

        purpose = str(
            workout.purpose or ""
        ).strip().lower()

        return (
            phase
            in {
                "taper",
                "race",
                "recovery",
                "regeneration",
            }
            or purpose
            in {
                "pre_race",
                "shakeout",
                "race",
                "recovery",
            }
        )

    @staticmethod
    def _recommendation(
        *,
        missing_stimulus: WorkoutStimulus,
        candidate: PlannedWorkout,
    ) -> str:
        """
        Builds the proposed athlete decision.
        """

        stimulus_label = (
            missing_stimulus.value
            .replace(
                "_",
                " ",
            )
            .title()
        )

        return (
            f"Consider changing "
            f"{candidate.title or 'the quality session'} "
            f"on {candidate.day.strftime('%d %b')} "
            f"to {stimulus_label} work."
        )

    @staticmethod
    def _rationale(
        *,
        missing_stimulus: WorkoutStimulus,
        completed_stimulus: (
            WorkoutStimulus
        ),
        candidate_stimulus: (
            WorkoutStimulus
        ),
        race_day: date | None,
    ) -> str:
        """
        Explains the detected gap and protected constraints.
        """

        if (
            completed_stimulus
            is WorkoutStimulus.UNKNOWN
        ):
            gap_explanation = (
                f"The planned "
                f"{missing_stimulus.value} session "
                "was not completed."
            )
        else:
            completed_label = (
                completed_stimulus.value
                .replace(
                    "_",
                    " ",
                )
            )

            gap_explanation = (
                f"The planned "
                f"{missing_stimulus.value} stimulus "
                f"was replaced by "
                f"{completed_label}."
            )

        candidate_label = (
            candidate_stimulus.value
            .replace(
                "_",
                " ",
            )
        )

        race_context = (
            (
                " The proposed slot remains at least "
                f"{MINIMUM_DAYS_BEFORE_RACE} days before "
                f"the race on "
                f"{race_day.strftime('%d %b')}."
            )
            if race_day is not None
            else ""
        )

        return (
            f"{gap_explanation} "
            f"A future {candidate_label} intensity session "
            "can be reconsidered to recover the missing "
            "stimulus without adding another demanding "
            "training day. The Long Run is preserved."
            f"{race_context}"
        )

    @staticmethod
    def _sport_family(
        sport,
    ) -> str:
        """
        Normalises sports for safe same-family substitution.
        """

        normalised = str(
            sport or ""
        ).strip().lower()

        if any(
            token in normalised
            for token in (
                "run",
                "running",
                "trail",
                "jog",
            )
        ):
            return "running"

        if any(
            token in normalised
            for token in (
                "cycl",
                "bike",
                "bicycle",
            )
        ):
            return "cycling"

        if "swim" in normalised:
            return "swimming"

        return normalised or "other"