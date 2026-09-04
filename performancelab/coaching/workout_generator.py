"""
PerformanceLab

Workout Generator

Converts a concrete TrainingWeek into planned workouts.
"""

from datetime import date, datetime, time, timedelta

from performancelab.training.planning.planned_workout import PlannedWorkout

from performancelab.physiology.thresholds import lthr

from performancelab.race.event import (
    ELEVATION_METRES_PER_EFFORT_KILOMETRE,
)

from .context import CoachContext
from .draft_slot import DraftTrainingSlot
from .heart_rate_target import (
    heart_rate_target_for,
)
from .session_purpose import SessionPurpose
from .strategy import StrategyPlan
from .training_week import TrainingWeek
from .workout_template import WorkoutTemplate
from .workout_templates import template_for

LONG_RUN_FALLBACK_PACE_FACTOR = 1.15

class WorkoutGenerator:
    """
    Converts DraftTrainingSlot objects into PlannedWorkout objects.

    The generator receives a TrainingWeek so that weekday-based
    coaching slots can be converted into concrete calendar dates.

    The generator does not decide:

    - how many sessions the week contains;
    - which weekdays should contain training;
    - which session purposes should be used;
    - the total weekly volume.

    Those decisions belong to StrategyPlan and
    WeekStructureGenerator.
    """

    # ======================================================

    def __init__(
        self,
        include_rest_days: bool = False,
    ) -> None:

        if not isinstance(
            include_rest_days,
            bool,
        ):

            raise TypeError(
                "include_rest_days must be a bool"
            )

        self.include_rest_days = include_rest_days

    # ======================================================

    def generate(
        self,
        *,
        strategy_plan: StrategyPlan,
        training_week: TrainingWeek,
        coach_context: CoachContext,
    ) -> tuple[PlannedWorkout, ...]:
        """
        Generates planned workouts from a concrete training week.

        Results are returned in chronological order.
        """

        self._validate_strategy_plan(
            strategy_plan
        )

        self._validate_training_week(
            training_week
        )

        self._validate_context(
            coach_context
        )

        sport = self._select_sport(
            coach_context
        )

        workouts: list[PlannedWorkout] = []
        intensity_index = 0

        for slot in training_week:

            scheduled_day = training_week.scheduled_date(
                slot
            )

            workout = self._generate_slot(
                slot=slot,
                scheduled_day=scheduled_day,
                sport=sport,
                strategy_plan=strategy_plan,
                coach_context=coach_context,
                intensity_index=(
                    intensity_index
                ),
            )
            if (
                slot.purpose
                is SessionPurpose.INTENSITY
            ):
                intensity_index += 1
            if workout is not None:

                workouts.append(
                    workout
                )

        return tuple(workouts)

    # ======================================================

    def _generate_slot(
        self,
        *,
        slot: DraftTrainingSlot,
        scheduled_day: date,
        sport: str | None,
        strategy_plan: StrategyPlan,
        coach_context: CoachContext,
        intensity_index: int = 0,
    ) -> PlannedWorkout | None:

        if slot.purpose is SessionPurpose.REST:

            return self._generate_rest(
                scheduled_day
            )

        focus = self._focus_for_slot(
            purpose=slot.purpose,
            strategy_plan=strategy_plan,
            intensity_index=intensity_index,
        )

        template = template_for(
            slot.purpose,
            focus=focus,
        )

        template = template.customized_for(
            strategy_plan
        )

        template = self._apply_sport(
            template=template,
            sport=sport,
        )

        return self._build_workout(
            slot=slot,
            scheduled_day=scheduled_day,
            template=template,
            coach_context=coach_context,
            strategy_plan=strategy_plan,
        )

    # ======================================================

    @staticmethod
    def _phase_for_slot(
        *,
        phase: str,
        purpose: SessionPurpose,
    ) -> str:
        """
        Keeps Race exclusively for the competition itself.

        Other sessions produced during race week belong to
        the taper that precedes the event.
        """

        if (
            phase.strip().lower()
            == "race"
            and purpose
            is not SessionPurpose.RACE
        ):
            return "Taper"

        return phase

    # ======================================================

    @staticmethod
    def _focus_for_slot(
        *,
        purpose: SessionPurpose,
        strategy_plan: StrategyPlan,
        intensity_index: int = 0,
    ) -> str | None:
        """
        Selects the most appropriate strategic focus for a slot.

        Demanding and race sessions use the primary key-session
        focus. Long and easy sessions use the secondary focus when
        available. Other session purposes retain the general focus.
        """

        if purpose is SessionPurpose.INTENSITY:

            if intensity_index > 0:
                return (
                    strategy_plan
                    .secondary_intensity_focus
                    or strategy_plan
                    .key_session_focus
                    or strategy_plan.focus
                )

            return (
                strategy_plan.key_session_focus
                or strategy_plan.focus
            )

        if purpose is SessionPurpose.RACE:
            return (
                strategy_plan.key_session_focus
                or strategy_plan.focus
            )
        
        if purpose in {
            SessionPurpose.LONG,
            SessionPurpose.EASY,
            SessionPurpose.TECHNIQUE,
            SessionPurpose.CROSS_TRAINING,
        }:
            return (
                strategy_plan.secondary_focus
                or strategy_plan.focus
            )

        if purpose is SessionPurpose.RECOVERY:
            return "recovery"

        return strategy_plan.focus

    # ======================================================
    @staticmethod
    def _event_for_day(
        *,
        coach_context: CoachContext,
        scheduled_day: date,
    ):
        """
        Returns the registered event occurring on the
        scheduled workout day.
        """

        candidates = list(
            getattr(
                coach_context,
                "upcoming_events",
                (),
            )
            or ()
        )

        for attribute_name in (
            "phase_event",
            "primary_event",
            "next_event",
        ):

            candidate = getattr(
                coach_context,
                attribute_name,
                None,
            )

            if (
                candidate is not None
                and candidate not in candidates
            ):
                candidates.append(
                    candidate
                )

        for event_entry in candidates:

            event = getattr(
                event_entry,
                "event",
                None,
            )

            if (
                event is not None
                and getattr(
                    event,
                    "date",
                    None,
                )
                == scheduled_day
            ):
                return event

        return None

    # ======================================================

    def _generate_rest(
        self,
        scheduled_day: date,
    ) -> PlannedWorkout | None:
        """
        Returns a rest placeholder when configured to do so.

        By default, rest slots do not generate workouts.
        """

        if not self.include_rest_days:

            return None

        return PlannedWorkout(
            scheduled_at=self._scheduled_at(
                scheduled_day
            ),
        )

    # ======================================================

    def _build_workout(
        self,
        *,
        slot: DraftTrainingSlot,
        scheduled_day: date,
        template: WorkoutTemplate,
        coach_context: CoachContext,
        strategy_plan: StrategyPlan | None = None,
    ) -> PlannedWorkout:

        duration_minutes = slot.duration_minutes

        if (
            duration_minutes is None
            and slot.purpose is not SessionPurpose.RACE
        ):

            raise ValueError(
                "training slots must have a duration"
            )

        if (
            duration_minutes is not None
            and duration_minutes <= 0
        ):

            raise ValueError(
                "training slots must have a positive duration"
            )

        duration_minutes = (
            self._prescribed_session_duration_minutes(
                template=template,
                requested_duration_minutes=duration_minutes,
                coach_context=coach_context,
            )
        )

        structure = self._prescribed_structure(
            template=template,
            duration_minutes=duration_minutes,
            coach_context=coach_context,
            strategy_plan=strategy_plan,
        )

        heart_rate_guidance = (
            self._heart_rate_guidance(
                purpose=slot.purpose,
                strategy_plan=strategy_plan,
                coach_context=coach_context,
                focus=(
                    self._template_focus(
                        template
                    )
                ),
            )
        )

        if heart_rate_guidance is not None:

            structure = (
                *structure,
                heart_rate_guidance,
            )

        race_event = (
            self._event_for_day(
                coach_context=coach_context,
                scheduled_day=scheduled_day,
            )
            if slot.purpose
            is SessionPurpose.RACE
            else None
        )

        training_reference = getattr(
            coach_context,
            "training_reference",
            None,
        )

        if training_reference is None:

            training_reference = getattr(
                coach_context,
                "training_state",
                None,
            )

        if race_event is not None:

            planned_distance = getattr(
                race_event,
                "distance",
                None,
            )

            planned_elevation_gain = getattr(
                race_event,
                "elevation_gain",
                None,
            )

        else:

            planned_elevation_gain = (
                getattr(
                    strategy_plan,
                    "long_session_elevation_gain",
                    None,
                )
                if (
                    strategy_plan is not None
                    and slot.purpose
                    is SessionPurpose.LONG
                )
                else None
            )

            planned_distance = (
                self._planned_long_distance(
                    purpose=slot.purpose,
                    duration_minutes=duration_minutes,
                    elevation_gain=(
                        planned_elevation_gain
                    ),
                    training_state=(
                        training_reference
                    ),
                )
            )

            if planned_distance is None:

                planned_distance = (
                    self._planned_easy_distance(
                        purpose=slot.purpose,
                        sport=template.sport,
                        duration_minutes=(
                            duration_minutes
                        ),
                        training_state=(
                            training_reference
                        ),
                    )
                )

        prescription_summary = (
            self._prescription_summary(
                purpose=slot.purpose,
                template=template,
                structure=structure,
                distance=planned_distance,
                duration_minutes=duration_minutes,
                coach_context=coach_context,
            )
        )

        return PlannedWorkout(
            scheduled_at=self._scheduled_at(
                scheduled_day
            ),
            sport=template.sport,
            title=self._sport_specific_title(
                template
            ),
            duration=(
                timedelta(
                    minutes=duration_minutes
                )
                if duration_minutes is not None
                else None
            ),
            distance=planned_distance,
            elevation_gain=(
                planned_elevation_gain
            ),
            description=template.description,
            prescription_summary=(
                prescription_summary
            ),
            intensity=template.intensity,
            objective=template.objective,
            structure=structure,
            equipment=template.equipment,
            phase=(
                self._phase_for_slot(
                    phase=(
                        strategy_plan.phase
                    ),
                    purpose=slot.purpose,
                )
                if strategy_plan is not None
                else None
            ),
        )

    # ======================================================
    @staticmethod
    def _template_focus(
        template: WorkoutTemplate,
    ) -> str | None:
        """
        Returns the physiological focus represented by the
        concrete workout template.

        This keeps heart-rate guidance aligned with the
        session that was actually generated.
        """

        title = (
            template.title
            .strip()
            .lower()
        )

        focus_markers = (
            (
                (
                    "lt2",
                    "threshold",
                ),
                "threshold",
            ),
            (
                (
                    "tempo",
                ),
                "tempo",
            ),
            (
                (
                    "hill",
                ),
                "hills",
            ),
            (
                (
                    "vo₂",
                    "vo2",
                ),
                "vo2max",
            ),
            (
                (
                    "speed",
                ),
                "speed",
            ),
        )

        for markers, focus in focus_markers:

            if any(
                marker in title
                for marker in markers
            ):
                return focus

        return None

    # ======================================================

    @staticmethod
    def _tempo_pace(
        coach_context,
    ) -> float | None:
        """
        Returns the athlete's Tempo pace from the
        physiological performance profile.
        """

        performance_profile = getattr(
            coach_context,
            "performance_profile",
            None,
        )

        if performance_profile is None:
            return None

        tempo_pace = getattr(
            performance_profile,
            "tempo_pace",
            None,
        )

        if (
            tempo_pace is None
            or tempo_pace <= 0
        ):
            return None

        return tempo_pace

    # ======================================================

    @staticmethod
    def _format_pace(
        pace: float,
    ) -> str:
        """
        Formats minutes per kilometre as mm:ss/km.
        """

        total_seconds = round(
            pace * 60
        )

        minutes, seconds = divmod(
            total_seconds,
            60,
        )

        return (
            f"{minutes}:{seconds:02d}/km"
        )

    # ======================================================
    @staticmethod
    def _should_reduce_threshold_dose(
        coach_context: CoachContext,
    ) -> bool:
        """
        Returns whether recent physiological load requires
        a reduced threshold dose.
        """

        training_state = getattr(
            coach_context,
            "training_state",
            None,
        )

        if training_state is None:
            return False

        return bool(
            getattr(
                training_state,
                "should_reduce_volume",
                False,
            )
        )

    # ======================================================

    @classmethod
    def _threshold_work_minutes(
        cls,
        *,
        template: WorkoutTemplate,
        coach_context: CoachContext,
    ) -> int | None:
        """
        Selects the LT2 work dose from the template.

        A reduced dose uses 21 minutes, producing 3×7 min
        for the current threshold template.
        """

        dose = template.dose

        if dose is None:
            return None

        if cls._should_reduce_threshold_dose(
            coach_context
        ):
            reduced_target = (
                dose.target_work_minutes
                - 3
            )

            return max(
                dose.minimum_work_minutes,
                reduced_target,
            )

        return dose.target_work_minutes

    # ======================================================

    @classmethod
    def _threshold_session_duration_minutes(
        cls,
        *,
        template: WorkoutTemplate,
        coach_context: CoachContext,
    ) -> int | None:
        """
        Calculates the complete LT2 session duration.

        The duration includes warm-up, LT2 repetitions,
        recoveries and cool-down.
        """

        work_minutes = (
            cls._threshold_work_minutes(
                template=template,
                coach_context=coach_context,
            )
        )

        if work_minutes is None:
            return None

        dose = template.dose

        if dose is None:
            return None

        repetitions = 3

        recovery_minutes = (
            dose.recovery_minutes
            or 2
        )

        recovery_total = (
            recovery_minutes
            * (repetitions - 1)
        )

        warm_up_minutes = 10

        cool_down_minutes = (
            3
            if cls._should_reduce_threshold_dose(
                coach_context
            )
            else 5
        )

        return (
            warm_up_minutes
            + work_minutes
            + recovery_total
            + cool_down_minutes
        )

    # ======================================================
    @classmethod
    def _vo2max_work_minutes(
        cls,
        *,
        template: WorkoutTemplate,
    ) -> int | None:
        """
        Selects the VO2max work dose from the template.
        """

        dose = template.dose

        if dose is None:
            return None

        return dose.target_work_minutes

    # ======================================================

    @classmethod
    def _prescribed_session_duration_minutes(
        cls,
        *,
        template: WorkoutTemplate,
        requested_duration_minutes: int | None,
        coach_context: CoachContext,
    ) -> int | None:
        """
        Caps duration-based planning with the workout's
        physiological dose.

        Sessions without a quantitative dose retain their
        requested duration.
        """

        if requested_duration_minutes is None:
            return None

        normalized_title = (
            template.title
            .strip()
            .lower()
        )

        is_threshold = (
            template.purpose
            is SessionPurpose.INTENSITY
            and (
                "lt2" in normalized_title
                or "threshold" in normalized_title
            )
        )

        is_vo2max = (
            template.purpose
            is SessionPurpose.INTENSITY
            and (
                "vo₂" in normalized_title
                or "vo2" in normalized_title
            )
        )

        if not (
            is_threshold
            or is_vo2max
        ):
            return requested_duration_minutes

        if is_threshold:

            prescribed_duration = (
                cls._threshold_session_duration_minutes(
                    template=template,
                    coach_context=coach_context,
                )
            )

        else:

            work_minutes = (
                cls._vo2max_work_minutes(
                    template=template,
                )
            )

            if work_minutes is None:
                prescribed_duration = None

            else:

                repetition_minutes = min(
                    3,
                    template.dose.maximum_repetition_minutes
                    if template.dose is not None
                    and template.dose.maximum_repetition_minutes
                    is not None
                    else 3,
                )

                repetitions = max(
                    1,
                    work_minutes // repetition_minutes,
                )

                recovery_minutes = (
                    template.dose.recovery_minutes
                    if template.dose is not None
                    and template.dose.recovery_minutes
                    is not None
                    else 2
                )

                recovery_total = (
                    (repetitions - 1)
                    * recovery_minutes
                )

                prescribed_duration = (
                    12
                    + repetitions * repetition_minutes
                    + recovery_total
                    + 8
                )

        if prescribed_duration is None:
            return requested_duration_minutes

        return min(
            requested_duration_minutes,
            prescribed_duration,
        )

    # ======================================================

    @staticmethod
    def _intensity_timing(
        duration_minutes: int,
    ) -> tuple[int, int, int]:
        """
        Returns warm-up, cool-down and main-work
        durations for an intensity session.
        """

        warm_up_minutes = (
            15
            if duration_minutes >= 45
            else 10
        )

        cool_down_minutes = (
            10
            if duration_minutes >= 45
            else 5
        )

        available_minutes = max(
            8,
            duration_minutes
            - warm_up_minutes
            - cool_down_minutes,
        )

        return (
            warm_up_minutes,
            cool_down_minutes,
            available_minutes,
        )

    # ======================================================
    @staticmethod
    def _heart_rate_summary(
        structure: tuple[str, ...],
    ) -> str | None:
        """
        Extracts the numeric heart-rate reference already
        calculated for the workout structure.

        Semantic zone labels remain in the detailed
        prescription; the compact summary uses only the
        actionable bpm reference.
        """

        prefix = "Heart rate target: "

        guidance = next(
            (
                step
                for step in structure
                if step.startswith(
                    prefix
                )
            ),
            None,
        )

        if guidance is None:
            return None

        resolved_target = guidance[
            len(prefix):
        ]

        separator = " · "

        if separator not in resolved_target:
            return None

        _, bpm_reference = (
            resolved_target.split(
                separator,
                maxsplit=1,
            )
        )

        bpm_reference = (
            bpm_reference.strip()
        )

        if not bpm_reference:
            return None

        return bpm_reference

    # ======================================================

    @classmethod
    def _prescription_summary(
        cls,
        *,
        purpose: SessionPurpose,
        template: WorkoutTemplate,
        structure: tuple[str, ...],
        distance: float | None,
        duration_minutes: int | None,
        coach_context: CoachContext,
    ) -> str | None:
        """
        Returns the essential workout prescription.

        The summary is prepared by the domain so that
        presentation components do not need to interpret
        workout titles or structures.
        """

        normalized_sport = str(
            template.sport or ""
        ).strip().lower()

        if (
            purpose is SessionPurpose.EASY
            and cls._is_running(
                normalized_sport
            )
            and distance is not None
            and distance > 0
        ):
            return (
                f"{round(distance)} km · Z2"
            )
        if (
            purpose is SessionPurpose.LONG
            and cls._is_running(
                normalized_sport
            )
            and distance is not None
            and distance > 0
        ):
            return (
                f"≈{round(distance)} km"
            )
        normalized_title = (
            template.title.strip().lower()
        )
        if (
            purpose is SessionPurpose.INTENSITY
            and "tempo" in normalized_title
            and duration_minutes is not None
            and duration_minutes >= 30
        ):
            (
                _,
                _,
                main_minutes,
            ) = cls._intensity_timing(
                duration_minutes
            )

            if "trail" in normalized_sport:

                heart_rate_reference = (
                    cls._heart_rate_summary(
                        structure
                    )
                )

                if (
                    heart_rate_reference
                    is not None
                ):
                    return (
                        f"{main_minutes} min tempo · "
                        f"{heart_rate_reference} · "
                        "RPE 6–7/10"
                    )

                return (
                    f"{main_minutes} min tempo · "
                    "RPE 6–7/10"
                )

            tempo_pace = cls._tempo_pace(
                coach_context
            )

            if tempo_pace is None:
                return (
                    f"{main_minutes} min tempo · "
                    "RPE 6–7/10"
                )

            main_distance = round(
                main_minutes / tempo_pace
            )

            return (
                f"{main_distance} km at "
                f"{cls._format_pace(tempo_pace)}"
            )
        if (
            purpose is SessionPurpose.INTENSITY
            and (
                "lt2" in normalized_title
                or "threshold" in normalized_title
            )
        ):
            return next(
                (
                    step
                    for step in structure
                    if "at lt2" in step.lower()
                ),
                None,
            )

        if "hill" not in normalized_title:
            return None

        main_step = next(
            (
                step
                for step in structure
                if (
                    "uphill" in step.lower()
                    and not step.lower().startswith(
                        "recover"
                    )
                )
            ),
            None,
        )

        if main_step is None:
            return None

        return main_step.replace(
            "×1 min uphill",
            "×60 sec uphill",
        )

    # ======================================================
    @classmethod
    def _planned_easy_distance(
        cls,
        *,
        purpose: SessionPurpose,
        sport: str | None,
        duration_minutes: int | None,
        training_state,
    ) -> float | None:
        """
        Estimates the distance of an easy running session
        from the athlete's recent physiological easy pace.

        The reference pace is effort-adjusted. Because an
        easy planned session does not prescribe elevation,
        the resulting distance represents a flat route.
        """

        normalized_sport = str(
            sport or ""
        ).strip().lower()

        if (
            purpose is not SessionPurpose.EASY
            or not cls._is_running(
                normalized_sport
            )
            or duration_minutes is None
            or duration_minutes <= 0
            or training_state is None
        ):
            return None

        easy_pace = getattr(
            training_state,
            "typical_easy_running_pace",
            0.0,
        )

        if easy_pace <= 0:
            return None

        planned_distance = (
            duration_minutes
            / easy_pace
        )
        if planned_distance <= 0:
            return None

        return round(
            planned_distance
        )

    # ======================================================
    
    @staticmethod
    def _planned_long_distance(
        *,
        purpose: SessionPurpose,
        duration_minutes: int | None,
        elevation_gain: float | None,
        training_state,
    ) -> float | None:
        """
        Estimates Long Run distance from duration,
        elevation and stable historical pace references.

        Reference priority:
        1. recent long-session effort pace;
        2. recent easy-running effort pace;
        3. recent general running pace with a conservative
           15 percent duration cost.

        Distance remains an estimate. Duration, intensity
        and elevation define the prescribed training dose.
        """

        if (
            purpose is not SessionPurpose.LONG
            or duration_minutes is None
            or duration_minutes <= 0
            or training_state is None
        ):
            return None

        effort_pace = getattr(
            training_state,
            (
                "typical_running_long_session_"
                "effort_pace"
            ),
            0.0,
        )

        if effort_pace <= 0:

            effort_pace = getattr(
                training_state,
                "typical_easy_running_pace",
                0.0,
            )

        if effort_pace <= 0:

            typical_running_pace = getattr(
                training_state,
                "typical_running_pace",
                0.0,
            )

            if typical_running_pace > 0:

                effort_pace = (
                    typical_running_pace
                    * LONG_RUN_FALLBACK_PACE_FACTOR
                )

        if effort_pace <= 0:
            return None

        effort_distance = (
            duration_minutes
            / effort_pace
        )

        elevation_distance = (
            max(
                elevation_gain or 0.0,
                0.0,
            )
            / ELEVATION_METRES_PER_EFFORT_KILOMETRE
        )

        planned_distance = (
            effort_distance
            - elevation_distance
        )

        if planned_distance <= 0:
            return None

        return round(
            planned_distance
        )
    # ======================================================
    @staticmethod
    def _format_heart_rate_range(
        *,
        lower_bpm: int,
        upper_bpm: int,
    ) -> str:
        """
        Formats a resolved heart-rate range for presentation.

        Zone definitions may use one bpm as an internal lower
        sentinel. That value is presented as an upper limit
        rather than as a physiological target.
        """

        if lower_bpm <= 1:
            return f"≤{upper_bpm} bpm"

        return (
            f"{lower_bpm}–{upper_bpm} bpm"
        )

    # ======================================================

    @classmethod
    def _heart_rate_guidance(
        cls,
        *,
        purpose: SessionPurpose,
        strategy_plan: StrategyPlan | None,
        coach_context: CoachContext,
        focus: str | None = None,
    ) -> str | None:
        """
        Resolves a semantic session target against the
        athlete's current heart-rate profile.
        """

        if (
            focus is None
            and strategy_plan is not None
        ):

            focus = cls._focus_for_slot(
                purpose=purpose,
                strategy_plan=strategy_plan,
            )

        target = heart_rate_target_for(
            purpose,
            focus=focus,
        )

        if target is None:
            return None

        profile = getattr(
            coach_context,
            "heart_rate_profile",
            None,
        )

        if profile is None:

            return (
                "Heart rate target: "
                f"{target.label}"
            )

        threshold_hr = getattr(
            profile,
            "threshold_hr",
            None,
        )

        if (
            target.threshold_range
            is not None
            and threshold_hr is not None
        ):

            lower_ratio, upper_ratio = (
                target.threshold_range
            )

            lower_bpm = round(
                threshold_hr
                * lower_ratio
            )

            upper_bpm = round(
                threshold_hr
                * upper_ratio
            )

            resolved_range = (
                cls._format_heart_rate_range(
                    lower_bpm=lower_bpm,
                    upper_bpm=upper_bpm,
                )
            )

            return (
                "Heart rate target: "
                f"{target.label} · "
                f"{resolved_range}"
            )

        resolved_zones = []

        for zone_name in target.zone_names:

            zone = profile.zone(
                zone_name
            )

            if zone is None:

                return (
                    "Heart rate target: "
                    f"{target.label}"
                )

            resolved_zones.append(
                zone
            )

        lower_bpm = min(
            zone.lower_bpm
            for zone in resolved_zones
        )

        upper_bpm = max(
            zone.upper_bpm
            for zone in resolved_zones
        )

        resolved_range = (
            cls._format_heart_rate_range(
                lower_bpm=lower_bpm,
                upper_bpm=upper_bpm,
            )
        )

        return (
            "Heart rate target: "
            f"{target.label} · "
            f"{resolved_range}"
        )

    # ======================================================

    @classmethod
    def _prescribed_structure(
        cls,
        *,
        template: WorkoutTemplate,
        duration_minutes: int | None,
        coach_context: CoachContext,
        strategy_plan: StrategyPlan | None = None,
    ) -> tuple[str, ...]:
        """
        Builds a concise, quantitative execution structure.

        The returned steps are intended for calendars, dashboards
        and workout-device exports.
        """

        if duration_minutes is None:
            return template.structure

        purpose = template.purpose

        if purpose is SessionPurpose.RECOVERY:
            return cls._continuous_structure(
                duration_minutes=duration_minutes,
                main_label=cls._sport_label(
                    template.sport,
                    running="Recovery run",
                    cycling="Recovery ride",
                    swimming="Recovery swim",
                    fallback="Recovery training",
                ),
                warm_up_minutes=5,
                cool_down_minutes=5,
            )

        if purpose is SessionPurpose.EASY:
            return cls._continuous_structure(
                duration_minutes=duration_minutes,
                main_label=cls._sport_label(
                    template.sport,
                    running="Easy aerobic run",
                    cycling="Easy aerobic ride",
                    swimming="Easy aerobic swim",
                    fallback="Easy aerobic training",
                ),
                warm_up_minutes=10,
                cool_down_minutes=5,
                split_sections=not cls._is_running(
                    str(template.sport or "").strip().lower()
                ),
            )

        if purpose is SessionPurpose.PRE_RACE:
            return cls._pre_race_structure(
                duration_minutes=duration_minutes,
                sport=template.sport,
            )

        if purpose is SessionPurpose.TECHNIQUE:
            return cls._technique_structure(
                duration_minutes=duration_minutes,
                sport=template.sport,
            )

        if purpose is SessionPurpose.LONG:
            return cls._long_structure(
                duration_minutes=duration_minutes,
                sport=template.sport,
                elevation_demand=getattr(
                    strategy_plan,
                    "elevation_demand",
                    None,
                ),
                target_elevation_gain=getattr(
                    strategy_plan,
                    "long_session_elevation_gain",
                    None,
                ),
                nutrition_profile=getattr(
                    coach_context,
                    "nutrition_profile",
                    None,
                ),
            )

        if purpose is SessionPurpose.CROSS_TRAINING:
            return cls._continuous_structure(
                duration_minutes=duration_minutes,
                main_label="Aerobic cross-training",
                warm_up_minutes=10,
                cool_down_minutes=5,
            )

        if purpose is SessionPurpose.INTENSITY:
            return cls._intensity_structure(
                template=template,
                duration_minutes=duration_minutes,
                coach_context=coach_context,
                elevation_demand=getattr(
                    strategy_plan,
                    "elevation_demand",
                    None,
                ),
            )

        if purpose is SessionPurpose.RACE:
            return cls._race_structure(
                duration_minutes=duration_minutes,
            )

        return template.structure

    # ======================================================

    @staticmethod
    def _apply_sport(
        *,
        template: WorkoutTemplate,
        sport: str | None,
    ) -> WorkoutTemplate:

        if template.sport is not None:

            return template

        if sport is None:

            return template

        return template.for_sport(
            sport
        )

    # ======================================================

    @staticmethod
    def _select_sport(
        context: CoachContext,
    ) -> str | None:
        """
        Selects the sport of the event that currently determines
        the training phase.

        The primary event, next chronological event and athlete's
        recorded sports are retained as fallbacks.
        """

        target_event = (
            getattr(
                context,
                "phase_event",
                None,
            )
            or getattr(
                context,
                "primary_event",
                None,
            )
            or getattr(
                context,
                "next_event",
                None,
            )
        )

        event = getattr(
            target_event,
            "event",
            None,
        )

        event_sport = getattr(
            event,
            "sport",
            "",
        )

        if (
            isinstance(event_sport, str)
            and event_sport.strip()
        ):
            return event_sport.strip()

        if not context.sports:
            return None

        return context.sports[0]

    # ======================================================

    @staticmethod
    def _scheduled_at(
        day: date,
    ) -> datetime:

        return datetime.combine(
            day,
            time.min,
        )

    # ======================================================

    @staticmethod
    def _validate_strategy_plan(
        strategy_plan: StrategyPlan,
    ) -> None:

        if not isinstance(
            strategy_plan,
            StrategyPlan,
        ):

            raise TypeError(
                "strategy_plan must be a StrategyPlan"
            )

    # ======================================================

    @staticmethod
    def _validate_training_week(
        training_week: TrainingWeek,
    ) -> None:

        if not isinstance(
            training_week,
            TrainingWeek,
        ):

            raise TypeError(
                "training_week must be a TrainingWeek"
            )

    # ======================================================

    @staticmethod
    def _validate_context(
        coach_context: CoachContext,
    ) -> None:

        if not isinstance(
            coach_context,
            CoachContext,
        ):

            raise TypeError(
                "coach_context must be a CoachContext"
            )

    # ======================================================

    def __repr__(self) -> str:

        return (
            "WorkoutGenerator("
            f"include_rest_days="
            f"{self.include_rest_days})"
        )

    # ======================================================

    @staticmethod
    def _continuous_structure(
        *,
        duration_minutes: int,
        main_label: str,
        warm_up_minutes: int,
        cool_down_minutes: int,
        split_sections: bool = True,
    ) -> tuple[str, ...]:
        """
        Splits a continuous workout into warm-up, main work
        and cool-down.
        """

        if (
            duration_minutes <= 15
            or not split_sections
        ):
            return (
                f"{main_label} {duration_minutes} min",
            )

        reserved_minutes = (
            warm_up_minutes
            + cool_down_minutes
        )

        if reserved_minutes >= duration_minutes:
            warm_up_minutes = max(
                5,
                duration_minutes // 4,
            )
            cool_down_minutes = max(
                3,
                duration_minutes // 6,
            )

        main_minutes = max(
            1,
            duration_minutes
            - warm_up_minutes
            - cool_down_minutes,
        )

        return (
            f"Warm up {warm_up_minutes} min",
            f"{main_label} {main_minutes} min",
            f"Cool down {cool_down_minutes} min",
        )

    # ======================================================

    @staticmethod
    def _add_continuous_guidance(
        structure: tuple[str, ...],
        *guidance: str,
    ) -> tuple[str, ...]:
        """
        Adds guidance without turning it into timed work.

        Split sessions keep the cool-down last. A continuous
        run keeps its single timed block first.
        """

        if (
            structure
            and structure[-1].lower().startswith(
                "cool down"
            )
        ):
            return (
                *structure[:-1],
                *guidance,
                structure[-1],
            )

        return (
            *structure,
            *guidance,
        )

    # ======================================================

    @classmethod
    def _pre_race_structure(
        cls,
        *,
        duration_minutes: int,
        sport: str | None,
    ) -> tuple[str, ...]:
        """
        Builds a pre-race session whose prescribed steps
        match its total duration.
        """

        if duration_minutes <= 20:
            return (
                f"Easy pre-race training {duration_minutes} min",
            )

        warm_up_minutes = (
            10
            if duration_minutes >= 30
            else 5
        )
        cool_down_minutes = 5
        activation_minutes = 5

        aerobic_minutes = max(
            1,
            duration_minutes
            - warm_up_minutes
            - activation_minutes
            - cool_down_minutes,
        )

        aerobic_label = cls._sport_label(
            sport,
            running="Easy aerobic run",
            cycling="Easy aerobic ride",
            swimming="Easy aerobic swim",
            fallback="Easy aerobic training",
        )

        activation_label = cls._sport_label(
            sport,
            running=(
                "4×20 sec relaxed strides with "
                "full easy recovery"
            ),
            cycling=(
                "4×20 sec relaxed high-cadence "
                "accelerations with easy recovery"
            ),
            swimming=(
                "4×20 sec relaxed pickups with "
                "easy recovery"
            ),
            fallback=(
                "4×20 sec relaxed accelerations "
                "with easy recovery"
            ),
        )

        return (
            f"Warm up {warm_up_minutes} min",
            f"{aerobic_label} {aerobic_minutes} min",
            (
                f"{activation_label} "
                f"({activation_minutes} min block)"
            ),
            f"Cool down {cool_down_minutes} min",
        )

    # ======================================================

    @classmethod
    def _technique_structure(
        cls,
        *,
        duration_minutes: int,
        sport: str | None,
    ) -> tuple[str, ...]:
        """
        Builds a low-intensity technique session whose
        prescribed steps match its total duration.
        """

        if duration_minutes <= 20:
            return (
                f"Easy technique training {duration_minutes} min",
            )

        warm_up_minutes = (
            10
            if duration_minutes >= 30
            else 5
        )
        cool_down_minutes = 5
        technique_minutes = min(
            10,
            max(
                5,
                duration_minutes // 4,
            ),
        )
        aerobic_minutes = max(
            1,
            duration_minutes
            - warm_up_minutes
            - technique_minutes
            - cool_down_minutes,
        )

        aerobic_label = cls._sport_label(
            sport,
            running="Easy aerobic run on varied terrain",
            cycling="Easy aerobic ride",
            swimming="Easy aerobic swim",
            fallback="Easy aerobic training",
        )

        technique_label = cls._sport_label(
            sport,
            running=(
                "Controlled climbing and relaxed "
                "descending technique"
            ),
            cycling=(
                "Controlled cadence and cornering "
                "technique"
            ),
            swimming="Relaxed swimming technique",
            fallback="Controlled movement technique",
        )

        return (
            f"Warm up {warm_up_minutes} min",
            f"{aerobic_label} {aerobic_minutes} min",
            f"{technique_label} {technique_minutes} min",
            f"Cool down {cool_down_minutes} min",
        )
    
    # ======================================================

    @classmethod
    def _long_structure(
        cls,
        *,
        duration_minutes: int,
        sport: str | None,
        elevation_demand: str | None = None,
        target_elevation_gain: int | None = None,
        nutrition_profile=None,
    ) -> tuple[str, ...]:
        """
        Builds a long aerobic session appropriate to the
        elevation demand of the target event.
        """

        main_label = cls._sport_label(
            sport,
            running="Long aerobic run",
            cycling="Long aerobic ride",
            swimming="Long aerobic swim",
            fallback="Long aerobic training",
        )

        if elevation_demand == "mountainous":
            main_label += (
                " on mountainous terrain"
            )

        elif elevation_demand == "hilly":
            main_label += (
                " on hilly terrain"
            )

        elif elevation_demand == "rolling":
            main_label += (
                " on rolling terrain"
            )

        structure = cls._continuous_structure(
            duration_minutes=duration_minutes,
            main_label=main_label,
            warm_up_minutes=10,
            cool_down_minutes=5,
            split_sections=not cls._is_running(
                str(sport or "").strip().lower()
            ),
        )
        
        if target_elevation_gain is not None:
            structure = cls._add_continuous_guidance(
                structure,
                (
                    "Target elevation gain: "
                    f"{target_elevation_gain} m D+"
                ),
            )

        nutrition_guidance = (
            cls._long_nutrition_guidance(
                duration_minutes=(
                    duration_minutes
                ),
                nutrition_profile=(
                    nutrition_profile
                ),
            )
        )

        if nutrition_guidance is not None:
            structure = cls._add_continuous_guidance(
                structure,
                nutrition_guidance,
            )

        if elevation_demand == "mountainous":
            return cls._add_continuous_guidance(
                structure,
                (
                    "Keep climbs aerobic and use "
                    "purposeful hiking on steep gradients"
                ),
                (
                    "Practise controlled downhill "
                    "technique without racing descents"
                ),
            )

        if elevation_demand == "hilly":
            return cls._add_continuous_guidance(
                structure,
                (
                    "Keep sustained climbs aerobic and "
                    "descend with controlled technique"
                ),
            )

        return structure
    # ======================================================

    @staticmethod
    def _long_nutrition_guidance(
        *,
        duration_minutes: int,
        nutrition_profile,
    ) -> str | None:
        """
        Adds nutrition practice only to sessions long enough
        to provide a useful tolerance test.
        """

        if (
            duration_minutes < 90
            or nutrition_profile is None
        ):
            return None

        if getattr(
            nutrition_profile,
            "is_athlete_tested",
            False,
        ):
            carbohydrate_per_hour = getattr(
                nutrition_profile,
                "carbohydrate_per_hour",
                None,
            )

            if (
                isinstance(
                    carbohydrate_per_hour,
                    int,
                )
                and not isinstance(
                    carbohydrate_per_hour,
                    bool,
                )
                and carbohydrate_per_hour > 0
            ):
                return (
                    "Practise the athlete-tested race "
                    "nutrition plan at approximately "
                    f"{carbohydrate_per_hour} g of "
                    "carbohydrate per hour"
                )

        return (
            "Practise a provisional carbohydrate intake "
            "of 30–45 g/h using familiar products; record "
            "tolerance before increasing the amount"
        )

    # ======================================================

    @classmethod
    def _sport_specific_title(
        cls,
        template: WorkoutTemplate,
    ) -> str:
        """
        Replaces a generic session title with a sport-specific title.
        """

        if template.purpose is SessionPurpose.CROSS_TRAINING:
            return template.title

        normalized_sport = str(
            template.sport or ""
        ).strip().lower()

        if cls._is_running(normalized_sport):
            activity_name = "Run"

        elif cls._is_cycling(normalized_sport):
            activity_name = "Ride"

        elif "swim" in normalized_sport:
            activity_name = "Swim"

        else:
            return template.title

        suffix = " Session"

        if not template.title.endswith(suffix):
            return template.title

        return (
            template.title[:-len(suffix)]
            + f" {activity_name}"
        )

    # ======================================================

    @staticmethod
    def _sport_label(
        sport: str | None,
        *,
        running: str,
        cycling: str,
        swimming: str,
        fallback: str,
    ) -> str:
        """
        Selects sport-specific execution wording.
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
            return running

        if any(
            token in normalized
            for token in (
                "cycl",
                "cycling",
                "bike",
                "bicycle",
            )
        ):
            return cycling

        if "swim" in normalized:
            return swimming

        return fallback

    # ======================================================

    @staticmethod
    def _split_complementary_minutes(
        minutes: int,
    ) -> tuple[int, int]:
        """
        Distributes unused interval-session time between
        warm-up and cool-down.

        Warm-up receives 60% because demanding sessions
        benefit from more preparation.
        """

        if minutes <= 0:
            return 0, 0

        warm_up_minutes = round(
            minutes * 0.60
        )

        cool_down_minutes = (
            minutes - warm_up_minutes
        )

        return (
            warm_up_minutes,
            cool_down_minutes,
        )

    # ======================================================

    @classmethod
    def _intensity_structure(
        cls,
        *,
        template: WorkoutTemplate,
        duration_minutes: int,
        coach_context: CoachContext,
        elevation_demand: str | None = None,
    ) -> tuple[str, ...]:
        """
        Builds an executable intensity session.
        """

        if duration_minutes < 30:
            return cls._continuous_structure(
                duration_minutes=duration_minutes,
                main_label="Controlled quality effort",
                warm_up_minutes=5,
                cool_down_minutes=5,
            )

        normalized_title = (
            template.title.lower()
        )

        is_threshold = (
            "lt2" in normalized_title
            or "threshold" in normalized_title
        )

        is_vo2max = (
            "vo₂" in normalized_title
            or "vo2" in normalized_title
        )

        if is_threshold:

            warm_up_minutes = 10

            cool_down_minutes = (
                3
                if cls._should_reduce_threshold_dose(
                    coach_context
                )
                else 5
            )

            available_minutes = max(
                1,
                duration_minutes
                - warm_up_minutes
                - cool_down_minutes,
            )

        elif (
            is_vo2max
            and template.dose is not None
        ):

            warm_up_minutes = 12
            cool_down_minutes = 8

            available_minutes = max(
                1,
                duration_minutes
                - warm_up_minutes
                - cool_down_minutes,
            )

        else:

            (
                warm_up_minutes,
                cool_down_minutes,
                available_minutes,
            ) = cls._intensity_timing(
                duration_minutes
            )

        complementary_minutes = 0

        if (
            "lt2" in normalized_title
            or "threshold" in normalized_title
        ):
            (
                main_steps,
                complementary_minutes,
            ) = cls._threshold_steps(
                available_minutes=available_minutes,
                sport=template.sport,
                coach_context=coach_context,
                template=template,
            )

        elif (
            "vo₂" in normalized_title
            or "vo2" in normalized_title
        ):
            (
                main_steps,
                complementary_minutes,
            ) = cls._vo2max_steps(
                available_minutes=available_minutes,
                template=template,
            )

        elif "tempo" in normalized_title:

            normalized_sport = str(
                template.sport or ""
            ).strip().lower()

            is_trail = (
                "trail" in normalized_sport
            )

            if is_trail:

                main_steps = (
                    (
                        f"Tempo effort "
                        f"{available_minutes} min at "
                        "RPE 6–7/10; keep the effort "
                        "controlled and regulate pace "
                        "by terrain"
                    ),
                )

            else:

                tempo_pace = cls._tempo_pace(
                    coach_context
                )

                pace_text = (
                    (
                        " at "
                        f"{cls._format_pace(tempo_pace)}"
                    )
                    if tempo_pace is not None
                    else " at RPE 6–7/10"
                )

                main_steps = (
                    (
                        f"Tempo effort "
                        f"{available_minutes} min"
                        f"{pace_text}"
                    ),
                )

        elif "hill" in normalized_title:
            (
                main_steps,
                complementary_minutes,
            ) = cls._hill_steps(
                available_minutes,
                elevation_demand=(
                    elevation_demand
                ),
            )

        elif "speed" in normalized_title:
            (
                main_steps,
                complementary_minutes,
            ) = cls._speed_steps(
                available_minutes
            )

        else:
            (
                main_steps,
                complementary_minutes,
            ) = cls._threshold_steps(
                available_minutes=available_minutes,
                sport=template.sport,
                coach_context=coach_context,
                template=template,
            )

        if (
            not (
                is_threshold
                or is_vo2max
            )
            or template.dose is None
        ):

            (
                warm_up_extension,
                cool_down_extension,
            ) = cls._split_complementary_minutes(
                complementary_minutes
            )

            warm_up_minutes += warm_up_extension
            cool_down_minutes += cool_down_extension

        return (
            f"Warm up {warm_up_minutes} min",
            *main_steps,
            f"Cool down {cool_down_minutes} min",
        )

    # ======================================================

    @classmethod
    def _threshold_steps(
        cls,
        *,
        available_minutes: int,
        sport: str | None,
        coach_context: CoachContext,
        template: WorkoutTemplate,
    ) -> tuple[tuple[str, ...], int]:
        """
        Builds threshold repetitions within the template's
        quantitative physiological dose.
        """

        repetitions = 3

        dose = template.dose

        recovery_minutes = (
            dose.recovery_minutes
            if (
                dose is not None
                and dose.recovery_minutes
                is not None
            )
            else 2
        )

        recovery_total = (
            recovery_minutes
            * (repetitions - 1)
        )

        available_work_minutes = max(
            0,
            available_minutes
            - recovery_total,
        )

        selected_work_minutes = (
            cls._threshold_work_minutes(
                template=template,
                coach_context=coach_context,
            )
        )

        if selected_work_minutes is None:

            selected_work_minutes = (
                available_work_minutes
            )

        selected_work_minutes = min(
            selected_work_minutes,
            available_work_minutes,
        )

        if dose is not None:

            selected_work_minutes = min(
                selected_work_minutes,
                dose.maximum_work_minutes,
            )

        work_minutes = max(
            1,
            selected_work_minutes
            // repetitions,
        )

        if (
            dose is not None
            and dose.maximum_repetition_minutes
            is not None
        ):
            work_minutes = min(
                work_minutes,
                dose.maximum_repetition_minutes,
            )

        prescribed_minutes = (
            repetitions * work_minutes
            + recovery_total
        )

        unused_minutes = max(
            0,
            available_minutes
            - prescribed_minutes,
        )

        threshold_target = cls._threshold_target(
            sport=sport,
            coach_context=coach_context,
        )

        steps = (
            (
                f"{repetitions}×{work_minutes} min "
                f"at LT2 ({threshold_target})"
            ),
            (
                f"Recover {recovery_minutes} min easy "
                "between repetitions"
            ),
        )

        return (
            steps,
            unused_minutes,
        )

    # ======================================================

    @staticmethod
    def _vo2max_steps(
        *,
        available_minutes: int,
        template: WorkoutTemplate,
    ) -> tuple[tuple[str, ...], int]:
        """
        Builds VO2max repetitions within the template dose.
        """

        dose = template.dose

        effort_minutes = 3
        recovery_minutes = (
            dose.recovery_minutes
            if (
                dose is not None
                and dose.recovery_minutes is not None
            )
            else 2
        )

        if (
            dose is not None
            and dose.maximum_repetition_minutes
            is not None
        ):
            effort_minutes = min(
                effort_minutes,
                dose.maximum_repetition_minutes,
            )

        target_work_minutes = (
            dose.target_work_minutes
            if dose is not None
            else 18
        )

        maximum_work_minutes = (
            dose.maximum_work_minutes
            if dose is not None
            else target_work_minutes
        )

        selected_work_minutes = min(
            target_work_minutes,
            maximum_work_minutes,
        )

        repetitions = max(
            1,
            selected_work_minutes
            // effort_minutes,
        )

        recovery_total = (
            max(0, repetitions - 1)
            * recovery_minutes
        )

        prescribed_minutes = (
            repetitions * effort_minutes
            + recovery_total
        )

        if prescribed_minutes > available_minutes:
            repetitions = max(
                1,
                (
                    available_minutes
                    + recovery_minutes
                )
                // (
                    effort_minutes
                    + recovery_minutes
                ),
            )

            recovery_total = (
                max(0, repetitions - 1)
                * recovery_minutes
            )

            prescribed_minutes = (
                repetitions * effort_minutes
                + recovery_total
            )

        complementary_minutes = max(
            0,
            available_minutes
            - prescribed_minutes,
        )

        steps = (
            (
                f"{repetitions}×"
                f"{effort_minutes} min "
                "at VO₂max effort"
            ),
            (
                f"Recover {recovery_minutes} min "
                "easy between repetitions"
            ),
        )

        return (
            steps,
            complementary_minutes,
        )


    @classmethod
    def _hill_steps(
        cls,
        available_minutes: int,
        *,
        elevation_demand: str | None = None,
    ) -> tuple[tuple[str, ...], int]:
        """
        Builds hill repetitions appropriate to the target event
        and reports the remaining preparation time.
        """

        if elevation_demand == "mountainous":
            repetition_minutes = max(
                3,
                min(
                    5,
                    available_minutes // 6,
                ),
            )
            recovery_minutes = 2

            repetitions = max(
                3,
                min(
                    5,
                    available_minutes
                    // (
                        repetition_minutes
                        + recovery_minutes
                    ),
                ),
            )

        elif elevation_demand == "hilly":
            repetition_minutes = 3
            recovery_minutes = 2

            repetitions = max(
                3,
                min(
                    6,
                    available_minutes // 5,
                ),
            )

        elif elevation_demand == "rolling":
            repetition_minutes = 1
            recovery_minutes = 1

            repetitions = max(
                6,
                min(
                    10,
                    available_minutes // 2,
                ),
            )

        else:
            repetition_minutes = 1
            recovery_minutes = 2

            repetitions = max(
                6,
                min(
                    10,
                    available_minutes // 3,
                ),
            )

        recovery_blocks = max(
            0,
            repetitions - 1,
        )

        prescribed_minutes = (
            repetitions * repetition_minutes
            + recovery_blocks * recovery_minutes
        )

        complementary_minutes = max(
            0,
            available_minutes
            - prescribed_minutes,
        )

        steps = (
            (
                f"{repetitions}×"
                f"{repetition_minutes} min uphill"
            ),
            (
                f"Recover {recovery_minutes} min "
                "easy downhill between repetitions"
            ),
        )

        return (
            steps,
            complementary_minutes,
        )

    @staticmethod
    def _speed_steps(
        available_minutes: int,
    ) -> tuple[tuple[str, ...], int]:
        """
        Builds short speed repetitions and reports the
        remaining preparation time.

        Each repetition occupies two complete minutes:
        30 seconds fast followed by 90 seconds easy.
        """

        block_minutes = 2

        repetitions = max(
            6,
            min(
                10,
                available_minutes
                // block_minutes,
            ),
        )

        prescribed_minutes = (
            repetitions * block_minutes
        )

        complementary_minutes = max(
            0,
            available_minutes
            - prescribed_minutes,
        )

        steps = (
            f"{repetitions}×30 sec fast",
            (
                "Recover 90 sec easy "
                "after each repetition"
            ),
        )

        return (
            steps,
            complementary_minutes,
        )
    # ======================================================

    @staticmethod
    def _race_structure(
        *,
        duration_minutes: int,
    ) -> tuple[str, ...]:
        """
        Builds the race-day structure.

        ``duration_minutes`` represents the estimated
        competition time. Warm-up and cool-down are
        additional preparation and recovery activities.
        """

        if duration_minutes <= 15:
            return (
                f"Race effort {duration_minutes} min",
            )

        warm_up_minutes = min(
            15,
            max(
                5,
                duration_minutes // 6,
            ),
        )

        cool_down_minutes = min(
            10,
            max(
                5,
                duration_minutes // 10,
            ),
        )

        return (
            f"Warm up {warm_up_minutes} min",
            f"Race effort {duration_minutes} min",
            f"Cool down {cool_down_minutes} min",
        )

    @classmethod
    def _threshold_target(
        cls,
        *,
        sport: str | None,
        coach_context: CoachContext,
    ) -> str:
        """
        Returns an athlete-specific threshold target.

        Cycling prioritises FTP power. Running prioritises
        threshold heart rate. Other sports use perceived effort
        until a sport-specific threshold is available.
        """

        athlete = coach_context.athlete
        normalized_sport = str(
            sport or ""
        ).strip().lower()

        if cls._is_cycling(
            normalized_sport
        ):
            ftp = getattr(
                athlete,
                "ftp",
                None,
            )

            if ftp is not None and ftp > 0:
                return cls._cycling_threshold_target(
                    ftp
                )

            threshold_hr = cls._athlete_threshold_hr(
                athlete
            )

            if threshold_hr is not None:
                return (
                    f"{round(threshold_hr)} bpm"
                )

            return "RPE 7–8/10"

        if cls._is_running(
            normalized_sport
        ):
            threshold_hr = cls._athlete_threshold_hr(
                athlete
            )

            if threshold_hr is not None:
                return (
                    f"{round(threshold_hr)} bpm"
                )

            return "RPE 7–8/10"

        return "RPE 7–8/10"


    @staticmethod
    def _cycling_threshold_target(
        ftp: float,
    ) -> str:
        """
        Returns a controlled threshold-power range.

        A range is preferable to one exact wattage because outdoor
        conditions and normal physiological variation make an exact
        value unnecessarily rigid.
        """

        lower = round(
            ftp * 0.95
        )
        upper = round(
            ftp * 1.00
        )

        return (
            f"{lower}–{upper} W "
            f"(95–100% FTP; FTP {round(ftp)} W)"
        )


    @staticmethod
    def _athlete_threshold_hr(
        athlete,
    ) -> float | None:
        """
        Returns a recorded threshold HR when available, otherwise
        estimates it from maximum heart rate.
        """

        recorded_threshold = getattr(
            athlete,
            "threshold_hr",
            None,
        )

        if (
            recorded_threshold is not None
            and recorded_threshold > 0
        ):
            return float(
                recorded_threshold
            )

        return lthr(
            getattr(
                athlete,
                "max_hr",
                None,
            )
        )


    @staticmethod
    def _is_running(
        normalized_sport: str,
    ) -> bool:
        return any(
            token in normalized_sport
            for token in (
                "run",
                "running",
                "trail",
                "jog",
            )
        )


    @staticmethod
    def _is_cycling(
        normalized_sport: str,
    ) -> bool:
        return any(
            token in normalized_sport
            for token in (
                "cycl",
                "cycling",
                "bike",
                "bicycle",
            )
        )
