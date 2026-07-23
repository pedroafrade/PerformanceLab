"""
PerformanceLab

Planner

Orchestrates the generation of a concrete weekly training plan.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

from performancelab.coaching.analyzer import CoachAnalyzer
from performancelab.coaching.context import CoachContext
from performancelab.coaching.selector import StrategySelector
from performancelab.coaching.structure_generator import (
    WeekStructureGenerator,
)
from performancelab.coaching.training_week import TrainingWeek
from performancelab.coaching.workout_generator import WorkoutGenerator
from performancelab.training.config import (
    AthleteAvailability,
    AthletePreferences,
    TrainingConstraints,
)

from .weekly_plan import WeeklyPlan
from .weekly_plan_builder import WeeklyPlanBuilder

if TYPE_CHECKING:
    from performancelab.athlete import Athlete


class Planner:
    """
    Builds a concrete weekly training plan for an athlete.

    By default, planning configuration is read directly from the athlete:

    - ``athlete.availability``
    - ``athlete.preferences``
    - ``athlete.training_constraints``

    Explicit values may still be supplied as temporary overrides.
    """

    def __init__(
        self,
        *,
        structure_generator: WeekStructureGenerator | None = None,
        workout_generator: WorkoutGenerator | None = None,
    ) -> None:
        self.structure_generator = (
            structure_generator or WeekStructureGenerator()
        )
        self.workout_generator = (
            workout_generator or WorkoutGenerator()
        )

    def build(
        self,
        *,
        athlete: Athlete,
        availability: AthleteAvailability | None = None,
        preferences: AthletePreferences | None = None,
        constraints: TrainingConstraints | None = None,
        week_start: date | None = None,
        today: date | None = None,
    ) -> WeeklyPlan:
        """
        Builds the athlete's weekly training plan.

        ``availability``, ``preferences`` and ``constraints`` are optional
        overrides. When omitted, the values stored on ``athlete`` are used.
        """

        self._validate_athlete(athlete)
        self._validate_optional_date(
            week_start,
            field="week_start",
        )
        self._validate_optional_date(
            today,
            field="today",
        )

        resolved_availability = (
            availability
            if availability is not None
            else athlete.availability
        )
        resolved_preferences = (
            preferences
            if preferences is not None
            else athlete.preferences
        )
        resolved_constraints = (
            constraints
            if constraints is not None
            else athlete.training_constraints
        )

        self._validate_training_config(
            availability=resolved_availability,
            preferences=resolved_preferences,
            constraints=resolved_constraints,
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
            context,
        ).analyze()

        strategy = StrategySelector().select(
            analysis,
        )

        strategy_plan = strategy.build(
            context,
        )

        slots = self.structure_generator.generate(
            strategy_plan=strategy_plan,
            availability=resolved_availability,
            preferences=resolved_preferences,
            constraints=resolved_constraints,
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
            workouts,
        ).week(
            start_date,
        )

    @staticmethod
    def _week_start(
        day: date,
    ) -> date:
        """Returns the Monday containing ``day``."""

        return day - timedelta(
            days=day.weekday(),
        )

    @staticmethod
    def _validate_athlete(
        athlete: Athlete,
    ) -> None:
        # Local import avoids Athlete -> planning -> Planner
        # during package initialization.
        from performancelab.athlete import Athlete

        if not isinstance(
            athlete,
            Athlete,
        ):
            raise TypeError(
                "athlete must be an Athlete"
            )

    @staticmethod
    def _validate_training_config(
        *,
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> None:
        if not isinstance(
            availability,
            AthleteAvailability,
        ):
            raise TypeError(
                "availability must be an AthleteAvailability"
            )

        if not isinstance(
            preferences,
            AthletePreferences,
        ):
            raise TypeError(
                "preferences must be an AthletePreferences"
            )

        if not isinstance(
            constraints,
            TrainingConstraints,
        ):
            raise TypeError(
                "constraints must be TrainingConstraints"
            )

    @staticmethod
    def _validate_optional_date(
        value: date | None,
        *,
        field: str,
    ) -> None:
        if (
            value is not None
            and not isinstance(value, date)
        ):
            raise TypeError(
                f"{field} must be a date or None"
            )

    def __repr__(self) -> str:
        return (
            "Planner("
            f"structure_generator={self.structure_generator!r}, "
            f"workout_generator={self.workout_generator!r})"
        )