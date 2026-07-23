"""
PerformanceLab

Workout Generator

Converts a concrete TrainingWeek into planned workouts.
"""

from datetime import date, datetime, time, timedelta

from performancelab.training.planning import PlannedWorkout

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
    ) -> PlannedWorkout | None:

        if slot.purpose is SessionPurpose.REST:

            return self._generate_rest(
                scheduled_day
            )

        template = template_for(
            slot.purpose
        )

        template = self._apply_sport(
            template=template,
            sport=sport,
        )

        return self._build_workout(
            slot=slot,
            scheduled_day=scheduled_day,
            template=template,
            strategy_plan=strategy_plan,
        )

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
        strategy_plan: StrategyPlan,
    ) -> PlannedWorkout:

        duration_minutes = slot.duration_minutes

        if duration_minutes is None:

            raise ValueError(
                "training slots must have a duration"
            )

        if duration_minutes <= 0:

            raise ValueError(
                "training slots must have a positive duration"
            )

        return PlannedWorkout(
            scheduled_at=self._scheduled_at(
                scheduled_day
            ),
            sport=template.sport,
            title=template.title,
            duration=timedelta(
                minutes=duration_minutes
            ),
            description=template.description,
            intensity=template.intensity,
            objective=self._objective(
                template=template,
                strategy_plan=strategy_plan,
            ),
            structure=template.structure,
            equipment=template.equipment,
        )

    # ======================================================

    @staticmethod
    def _objective(
        *,
        template: WorkoutTemplate,
        strategy_plan: StrategyPlan,
    ) -> str:

        if not strategy_plan.objectives:

            return template.objective

        weekly_objective = "; ".join(
            strategy_plan.objectives
        )

        return (
            f"{template.objective} "
            f"Weekly focus: {weekly_objective}"
        )

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