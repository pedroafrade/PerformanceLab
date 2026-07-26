"""
PerformanceLab

Workout Generator

Converts a concrete TrainingWeek into planned workouts.
"""

from datetime import date, datetime, time, timedelta

from performancelab.training.planning.planned_workout import PlannedWorkout

from performancelab.physiology.thresholds import lthr

from .context import CoachContext
from .draft_slot import DraftTrainingSlot
from .session_purpose import SessionPurpose
from .strategy import StrategyPlan
from .training_week import TrainingWeek
from .workout_template import WorkoutTemplate
from .workout_templates import template_for


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
            )

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
    ) -> PlannedWorkout | None:

        if slot.purpose is SessionPurpose.REST:

            return self._generate_rest(
                scheduled_day
            )

        focus = self._focus_for_slot(
            purpose=slot.purpose,
            strategy_plan=strategy_plan,
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
        )

    # ======================================================

    @staticmethod
    def _focus_for_slot(
        *,
        purpose: SessionPurpose,
        strategy_plan: StrategyPlan,
    ) -> str | None:
        """
        Selects the most appropriate strategic focus for a slot.

        Demanding and race sessions use the primary key-session
        focus. Long and easy sessions use the secondary focus when
        available. Other session purposes retain the general focus.
        """

        if purpose in {
            SessionPurpose.INTENSITY,
            SessionPurpose.RACE,
        }:
            return (
                strategy_plan.key_session_focus
                or strategy_plan.focus
            )

        if purpose in {
            SessionPurpose.LONG,
            SessionPurpose.EASY,
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

        return PlannedWorkout(
            scheduled_at=self._scheduled_at(
                scheduled_day
            ),
            sport=template.sport,
            title=template.title,
            duration=(
                timedelta(
                    minutes=duration_minutes
                )
                if duration_minutes is not None
                else None
            ),
            description=template.description,
            intensity=template.intensity,
            objective=template.objective,
            structure=self._prescribed_structure(
                template=template,
                duration_minutes=duration_minutes,
                coach_context=coach_context,
            ),
            equipment=template.equipment,
        )

    # ======================================================

    @classmethod
    def _prescribed_structure(
        cls,
        *,
        template: WorkoutTemplate,
        duration_minutes: int | None,
        coach_context: CoachContext,
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
            )

        if purpose is SessionPurpose.LONG:
            return cls._continuous_structure(
                duration_minutes=duration_minutes,
                main_label=cls._sport_label(
                    template.sport,
                    running="Long aerobic run",
                    cycling="Long aerobic ride",
                    swimming="Long aerobic swim",
                    fallback="Long aerobic training",
                ),
                warm_up_minutes=10,
                cool_down_minutes=5,
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
        Selects the athlete's primary available sport.

        CoachContext currently exposes a tuple of sports without
        an explicit primary-sport field. Therefore, the first
        recorded sport is used.
        """

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
    ) -> tuple[str, ...]:
        """
        Splits a continuous workout into warm-up, main work
        and cool-down.
        """

        if duration_minutes <= 15:
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

    @classmethod
    def _intensity_structure(
        cls,
        *,
        template: WorkoutTemplate,
        duration_minutes: int,
        coach_context: CoachContext,
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

        normalized_title = template.title.lower()

        if "threshold" in normalized_title:
            main_steps = cls._threshold_steps(
                available_minutes=available_minutes,
                sport=template.sport,
                coach_context=coach_context,
            )

        elif "vo₂" in normalized_title or "vo2" in normalized_title:
            main_steps = cls._vo2max_steps(
                available_minutes
            )

        elif "tempo" in normalized_title:
            main_steps = (
                f"Tempo effort {available_minutes} min",
            )

        elif "hill" in normalized_title:
            main_steps = cls._hill_steps(
                available_minutes
            )

        elif "speed" in normalized_title:
            main_steps = cls._speed_steps(
                available_minutes
            )

        else:
            main_steps = cls._threshold_steps(
                available_minutes=available_minutes,
                sport=template.sport,
                coach_context=coach_context,
            )

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
    ) -> tuple[str, ...]:
        repetitions = 3
        recovery_minutes = 2

        work_minutes = max(
            4,
            (
                available_minutes
                - recovery_minutes * (repetitions - 1)
            )
            // repetitions,
        )

        threshold_target = cls._threshold_target(
            sport=sport,
            coach_context=coach_context,
        )

        return (
            (
                f"{repetitions}×{work_minutes} min "
                f"at threshold ({threshold_target})"
            ),
            (
                f"Recover {recovery_minutes} min easy "
                "between repetitions"
            ),
        )

    @staticmethod
    def _vo2max_steps(
        available_minutes: int,
    ) -> tuple[str, ...]:
        repetitions = max(
            4,
            min(
                6,
                available_minutes // 5,
            ),
        )

        return (
            f"{repetitions}×3 min at VO₂max effort",
            "Recover 2 min easy",
        )


    @staticmethod
    def _hill_steps(
        available_minutes: int,
    ) -> tuple[str, ...]:
        repetitions = max(
            6,
            min(
                10,
                available_minutes // 3,
            ),
        )

        return (
            f"{repetitions}×1 min uphill",
            "Recover easy downhill",
        )


    @staticmethod
    def _speed_steps(
        available_minutes: int,
    ) -> tuple[str, ...]:
        repetitions = max(
            6,
            min(
                10,
                available_minutes // 3,
            ),
        )

        return (
            f"{repetitions}×30 sec fast",
            "Recover 90 sec easy",
        )

    # ======================================================

    @staticmethod
    def _race_structure(
        *,
        duration_minutes: int,
    ) -> tuple[str, ...]:
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

        race_minutes = max(
            1,
            duration_minutes
            - warm_up_minutes
            - cool_down_minutes,
        )

        return (
            f"Warm up {warm_up_minutes} min",
            f"Race effort {race_minutes} min",
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