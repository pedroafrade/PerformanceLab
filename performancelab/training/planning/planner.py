"""
PerformanceLab

Planner

Orchestrates the generation of a concrete weekly training plan.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

from performancelab.coaching.analyzer import CoachAnalyzer
from performancelab.coaching.availability import AthleteAvailability
from performancelab.coaching.constraints import TrainingConstraints
from performancelab.coaching.context import CoachContext
from performancelab.coaching.preferences import AthletePreferences
from performancelab.coaching.selector import StrategySelector
from performancelab.coaching.structure_generator import (
    WeekStructureGenerator,
)
from performancelab.coaching.training_week import TrainingWeek
from performancelab.coaching.workout_generator import WorkoutGenerator

from .weekly_plan import WeeklyPlan
from .weekly_plan_builder import WeeklyPlanBuilder

if TYPE_CHECKING:
    from performancelab.athlete import Athlete


class Planner:
    """
    Builds a concrete weekly training plan for an athlete.

    Workflow:

    Athlete
        -> CoachContext
        -> CoachAnalyzer
        -> StrategySelector
        -> StrategyPlan
        -> WeekStructureGenerator
        -> TrainingWeek
        -> WorkoutGenerator
        -> WeeklyPlanBuilder
        -> WeeklyPlan
    """

    # ======================================================

    def __init__(
        self,
        *,
        structure_generator: WeekStructureGenerator | None = None,
        workout_generator: WorkoutGenerator | None = None,
    ) -> None:
        self.structure_generator = (
            structure_generator
            or WeekStructureGenerator()
        )

        self.workout_generator = (
            workout_generator
            or WorkoutGenerator()
        )

    # ======================================================

    def build(
        self,
        *,
        athlete: Athlete,
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
        week_start: date | None = None,
        today: date | None = None,
    ) -> WeeklyPlan:
        """
        Builds the athlete's weekly training plan.

        Parameters
        ----------
        athlete
            Athlete for whom the plan is generated.

        availability
            Time available for training on each weekday.

        preferences
            Athlete scheduling and training preferences.

        constraints
            Limits that the generated week must respect.

        week_start
            Any date in the week to generate. It is normalized
            to Monday. Defaults to ``today``.

        today
            Reference date used to build the coaching context.
            Defaults to the current date.
        """

        self._validate_inputs(
            athlete=athlete,
            availability=availability,
            preferences=preferences,
            constraints=constraints,
            week_start=week_start,
            today=today,
        )

        reference_day = today or date.today()

        start_date = self._week_start(
            week_start or reference_day
        )

        context = CoachContext.from_athlete(
            athlete,
            today=reference_day,
        )

        analysis = CoachAnalyzer(
            context
        ).analyze()

        strategy = StrategySelector().select(
            analysis
        )

        strategy_plan = strategy.build(
            context
        )

        slots = self.structure_generator.generate(
            strategy_plan=strategy_plan,
            availability=availability,
            preferences=preferences,
            constraints=constraints,
        )

        training_week = TrainingWeek(
            start_date=start_date,
            slots=slots,
        )

        workouts = self.workout_generator.generate(
            strategy_plan=strategy_plan,
            training_week=training_week,
            coach_context=context,
        )

        return WeeklyPlanBuilder(
            workouts
        ).week(
            start_date
        )

    # ======================================================

    @staticmethod
    def _week_start(
        day: date,
    ) -> date:
        """
        Returns the Monday containing ``day``.
        """

        return day - timedelta(
            days=day.weekday()
        )

    # ======================================================

    @staticmethod
    def _validate_inputs(
        *,
        athlete: Athlete,
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
        week_start: date | None,
        today: date | None,
    ) -> None:
        # Local import prevents the Athlete -> planning -> Planner
        # circular import during package initialization.
        from performancelab.athlete import Athlete

        if not isinstance(
            athlete,
            Athlete,
        ):
            raise TypeError(
                "athlete must be an Athlete"
            )

        if not isinstance(
            availability,
            AthleteAvailability,
        ):
            raise TypeError(
                "availability must be an "
                "AthleteAvailability"
            )

        if not isinstance(
            preferences,
            AthletePreferences,
        ):
            raise TypeError(
                "preferences must be an "
                "AthletePreferences"
            )

        if not isinstance(
            constraints,
            TrainingConstraints,
        ):
            raise TypeError(
                "constraints must be "
                "TrainingConstraints"
            )

        if (
            week_start is not None
            and not isinstance(week_start, date)
        ):
            raise TypeError(
                "week_start must be a date or None"
            )

        if (
            today is not None
            and not isinstance(today, date)
        ):
            raise TypeError(
                "today must be a date or None"
            )

    # ======================================================

    def __repr__(self) -> str:
        return (
            "Planner("
            f"structure_generator="
            f"{self.structure_generator!r}, "
            f"workout_generator="
            f"{self.workout_generator!r})"
        )