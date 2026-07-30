"""
PerformanceLab

Planner

Orchestrates the generation of a concrete weekly training plan.
"""

from __future__ import annotations

from dataclasses import replace
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
from performancelab.coaching.draft_slot import DraftTrainingSlot
from performancelab.coaching.session_purpose import SessionPurpose

from performancelab.training.config import (
    AthleteAvailability,
    AthletePreferences,
    TrainingConstraints,
    Weekday,
)
from performancelab.training.load import (
    planned_workout_load,
    planned_weekly_load,
)

from .weekly_plan import WeeklyPlan
from .weekly_plan_builder import WeeklyPlanBuilder
from .training_plan import TrainingPlan

if TYPE_CHECKING:
    from performancelab.athlete import Athlete

MAX_PLANNED_WEEKLY_LOAD_GROWTH = 0.10
MIN_DAYS_BETWEEN_LONG_AND_INTENSITY = 2
POST_PRIMARY_EVENT_RECOVERY_DAYS = 7

DEMANDING_EVENT_EFFORT_DISTANCE = 30.0
DEMANDING_EVENT_COMPLETE_REST_DAYS = 2

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

        print(">>> Planner.build() foi chamado")

        self._validate_athlete(athlete)

        self._validate_optional_date(
            week_start,
            field="week_start",
        )
        
        self._validate_optional_date(
            today,
            field="today",
        )

        if availability is not None:
            resolved_availability = availability

        elif athlete.train_any_day:
            resolved_availability = AthleteAvailability.unrestricted()

        else:
            resolved_availability = athlete.availability

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

        resolved_constraints = (
            self._block_past_weekdays(
                constraints=resolved_constraints,
                week_start=start_date,
                today=reference_day,
            )
        )

        context = CoachContext.from_athlete(
            athlete,
            today=reference_day,
        )

        resolved_constraints = (
            self._block_demanding_event_recovery_days(
                constraints=resolved_constraints,
                context=context,
                week_start=start_date,
            )
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

        slots = self._apply_events_to_week(
            slots=slots,
            week_start=start_date,
            event_entries=(
                context.competition_block_events
            ),
        )

        print()
        print("Slots gerados:", len(slots))

        for slot in slots:
            print(slot)

        print()

        training_week = TrainingWeek(
            start_date=start_date,
            slots=slots,
        )

        workouts = self.workout_generator.generate(
            strategy_plan=strategy_plan,
            training_week=training_week,
            coach_context=context,
        )

        self._print_diagnostics(
            strategy_plan=strategy_plan,
            workouts=workouts,
        )

        return WeeklyPlanBuilder(
            workouts,
        ).week(
            start_date,
        )

    def build_training_plan(
        self,
        *,
        athlete: Athlete,
        availability: AthleteAvailability | None = None,
        preferences: AthletePreferences | None = None,
        constraints: TrainingConstraints | None = None,
        today: date | None = None,
    ) -> TrainingPlan:
        """
        Builds the athlete's training plan from the current
        day through the primary event and its following
        recovery period.

        Weekly plans are consecutive windows inside the same
        complete TrainingPlan.
        """

        self._validate_athlete(
            athlete
        )

        self._validate_optional_date(
            today,
            field="today",
        )

        reference_day = (
            today or date.today()
        )

        context = CoachContext.from_athlete(
            athlete,
            today=reference_day,
        )

        first_week_start = self._week_start(
            reference_day
        )

        default_end_date = (
            first_week_start
            + timedelta(days=6)
        )

        if context.planning_end_date is not None:

            plan_end_date = (
                context.planning_end_date
                + timedelta(
                    days=(
                        POST_PRIMARY_EVENT_RECOVERY_DAYS
                    )
                )
            )

        else:

            plan_end_date = default_end_date

        training_plan = TrainingPlan(
            start_date=reference_day,
            end_date=plan_end_date,
            primary_event_id=(
                context.primary_event_id
            ),
            competition_event_ids=(
                context.competition_event_ids
            ),
        )

        week_start = first_week_start
        previous_weekly_load = None
        previous_planned_workout = None

        while week_start <= plan_end_date:

            planning_day = (
                reference_day
                if week_start == first_week_start
                else week_start
            )

            weekly_plan = self.build(
                athlete=athlete,
                availability=availability,
                preferences=preferences,
                constraints=constraints,
                week_start=week_start,
                today=planning_day,
            )

            weekly_plan = (
                self._protect_week_boundary(
                    weekly_plan=weekly_plan,
                    previous_workout=(
                        previous_planned_workout
                    ),
                )
            )

            if (
                previous_weekly_load is not None
                and self._should_limit_weekly_load(
                    previous_planned_workout
                )
            ):

                weekly_plan = (
                    self._limit_weekly_load_growth(
                        weekly_plan=weekly_plan,
                        previous_weekly_load=(
                            previous_weekly_load
                        ),
                    )
                )

            visible_workouts = tuple(
                workout
                for workout in weekly_plan.workouts
                if (
                    workout.day is not None
                    and training_plan.covers(
                        workout.day
                    )
                )
            )

            current_weekly_load = (
                planned_weekly_load(
                    visible_workouts
                )
            )

            if current_weekly_load > 0:

                previous_weekly_load = (
                    current_weekly_load
                )

            for workout in visible_workouts:

                training_plan.add(
                    workout
                )

            if visible_workouts:

                previous_planned_workout = (
                    visible_workouts[-1]
                )

            week_start += timedelta(
                days=7
            )

        return training_plan

    # ======================================================

    @staticmethod
    def _protect_week_boundary(
        *,
        weekly_plan: WeeklyPlan,
        previous_workout,
    ) -> WeeklyPlan:
        """
        Prevents a demanding session from being scheduled
        immediately after a long workout or race belonging
        to the previous week.

        The demanding workout is moved to the first free
        day that provides sufficient recovery.
        """

        if previous_workout is None:
            return weekly_plan

        if not (
            Planner._is_long_workout(
                previous_workout
            )
            or Planner._is_race_workout(
                previous_workout
            )
        ):
            return weekly_plan

        demanding_workout = next(
            (
                workout
                for workout in weekly_plan.workouts
                if Planner._is_demanding_workout(
                    workout
                )
            ),
            None,
        )

        if demanding_workout is None:
            return weekly_plan

        days_since_previous = (
            demanding_workout.day
            - previous_workout.day
        ).days

        if (
            days_since_previous
            >= MIN_DAYS_BETWEEN_LONG_AND_INTENSITY
        ):
            return weekly_plan

        earliest_safe_day = (
            previous_workout.day
            + timedelta(
                days=(
                    MIN_DAYS_BETWEEN_LONG_AND_INTENSITY
                )
            )
        )

        occupied_days = {
            workout.day
            for workout in weekly_plan.workouts
            if workout is not demanding_workout
        }

        replacement_day = (
            earliest_safe_day
        )

        while (
            replacement_day
            <= weekly_plan.end_date
            and replacement_day
            in occupied_days
        ):
            replacement_day += timedelta(
                days=1
            )

        if (
            replacement_day
            > weekly_plan.end_date
        ):
            return weekly_plan

        day_shift = (
            replacement_day
            - demanding_workout.day
        ).days

        shifted_workout = replace(
            demanding_workout,
            scheduled_at=(
                demanding_workout.scheduled_at
                + timedelta(
                    days=day_shift
                )
            ),
        )

        workouts = [
            (
                shifted_workout
                if workout is demanding_workout
                else workout
            )
            for workout in weekly_plan.workouts
        ]

        return WeeklyPlan(
            start_date=weekly_plan.start_date,
            end_date=weekly_plan.end_date,
            workouts=workouts,
        )

    # ======================================================

    @staticmethod
    def _should_limit_weekly_load(
        previous_workout,
    ) -> bool:
        """
        Avoids comparing a recovery week with a race
        week whose competition load may be incomplete.
        """

        if previous_workout is None:
            return True

        return not Planner._is_race_workout(
            previous_workout
        )

    # ======================================================

    @staticmethod
    def _limit_weekly_load_growth(
        *,
        weekly_plan: WeeklyPlan,
        previous_weekly_load: float,
        maximum_growth: float = (
            MAX_PLANNED_WEEKLY_LOAD_GROWTH
        ),
    ) -> WeeklyPlan:
        """
        Prevents an excessive increase over the previous
        planned week's load.

        An additional demanding session is removed first.
        Other ordinary sessions are considered afterwards.
        Race and long sessions are preserved.
        """

        if previous_weekly_load <= 0:
            return weekly_plan

        maximum_load = (
            previous_weekly_load
            * (1 + maximum_growth)
        )

        workouts = list(
            weekly_plan.workouts
        )

        while (
            planned_weekly_load(workouts)
            > maximum_load
        ):

            demanding_workouts = [
                workout
                for workout in workouts
                if Planner._is_demanding_workout(
                    workout
                )
            ]

            if len(demanding_workouts) > 1:

                removable = (
                    demanding_workouts[:-1]
                )

            else:

                removable = [
                    workout
                    for workout in workouts
                    if (
                        not Planner._is_demanding_workout(
                            workout
                        )
                        and not Planner._is_long_workout(
                            workout
                        )
                        and not Planner._is_race_workout(
                            workout
                        )
                        and not Planner._is_shakeout_workout(
                            workout
                        )
                    )
                ]

            if not removable:
                break

            selected = max(
                removable,
                key=lambda workout: (
                    planned_workout_load(
                        workout
                    )
                    or 0.0
                ),
            )

            workouts.remove(
                selected
            )

        return WeeklyPlan(
            start_date=weekly_plan.start_date,
            end_date=weekly_plan.end_date,
            workouts=workouts,
        )

    # ======================================================

    @staticmethod
    def _is_demanding_workout(
        workout,
    ) -> bool:

        intensity = str(
            getattr(
                workout,
                "intensity",
                "",
            )
            or ""
        ).strip().lower()

        return intensity in {
            "moderately hard",
            "hard",
            "very hard",
        }

    # ======================================================

    @staticmethod
    def _is_long_workout(
        workout,
    ) -> bool:

        title = str(
            getattr(
                workout,
                "title",
                "",
            )
            or ""
        ).strip().lower()

        return "long" in title

    # ======================================================

    @staticmethod
    def _is_race_workout(
        workout,
    ) -> bool:

        intensity = str(
            getattr(
                workout,
                "intensity",
                "",
            )
            or ""
        ).strip().lower()

        return intensity == "race effort"
    # ======================================================

    @staticmethod
    def _is_shakeout_workout(
        workout,
    ) -> bool:

        title = str(
            getattr(
                workout,
                "title",
                "",
            )
            or ""
        ).strip().lower()

        return "shakeout" in title
    
    # ======================================================

    @staticmethod
    def _apply_events_to_week(
        *,
        slots: tuple[DraftTrainingSlot, ...],
        week_start: date,
        event_entries: tuple[object, ...],
    ) -> tuple[DraftTrainingSlot, ...]:
        """
        Inserts every competition-block event belonging to
        the requested training week.

        Events outside the requested week leave the training
        structure unchanged.
        """

        updated_slots = slots

        for event_entry in event_entries:

            updated_slots = (
                Planner._apply_shakeout_to_week(
                    slots=updated_slots,
                    week_start=week_start,
                    event_entry=event_entry,
                )
            )

            updated_slots = (
                Planner._apply_event_to_week(
                    slots=updated_slots,
                    week_start=week_start,
                    next_event=event_entry,
                )
            )

        return updated_slots
    
    # ======================================================

    @staticmethod
    def _apply_shakeout_to_week(
        *,
        slots: tuple[DraftTrainingSlot, ...],
        week_start: date,
        event_entry,
    ) -> tuple[DraftTrainingSlot, ...]:
        """
        Places a short activation session on the day before
        a registered competition.

        The shakeout replaces any previously planned session
        on that day.
        """

        event = getattr(
            event_entry,
            "event",
            None,
        )

        event_date = getattr(
            event,
            "date",
            None,
        )

        if event_date is None:
            return slots

        shakeout_date = (
            event_date
            - timedelta(days=1)
        )

        week_end = (
            week_start
            + timedelta(days=6)
        )

        if not (
            week_start
            <= shakeout_date
            <= week_end
        ):
            return slots

        shakeout_weekday = Weekday(
            shakeout_date.weekday()
        )

        updated_slots = list(
            slots
        )

        shakeout_index = next(
            (
                index
                for index, slot in enumerate(
                    updated_slots
                )
                if (
                    slot.weekday
                    == shakeout_weekday
                )
            ),
            None,
        )

        if shakeout_index is None:
            return slots

        event_name = str(
            getattr(
                event,
                "name",
                "",
            )
            or "competition"
        ).strip()

        updated_slots[shakeout_index] = (
            DraftTrainingSlot(
                weekday=shakeout_weekday,
                purpose=(
                    SessionPurpose.SHAKEOUT
                ),
                duration_minutes=20,
                notes=(
                    "Pre-race activation for "
                    f"{event_name}."
                ),
            )
        )

        return tuple(
            sorted(
                updated_slots,
                key=lambda slot: (
                    slot.weekday.value
                ),
            )
        )

    # ======================================================

    @staticmethod
    def _apply_event_to_week(
        *,
        slots: tuple[DraftTrainingSlot, ...],
        week_start: date,
        next_event,
    ) -> tuple[DraftTrainingSlot, ...]:
        """
        Inserts the athlete's next event into the requested training week.

        The event replaces the slot assigned to its weekday. If that day was
        originally a rest day, another training slot is converted to rest so
        that the event does not increase the planned number of sessions.
        """

        if next_event is None:
            return slots

        event = getattr(
            next_event,
            "event",
            None,
        )

        if event is None:
            return slots

        event_date = getattr(
            event,
            "date",
            None,
        )

        if event_date is None:
            return slots

        week_end = week_start + timedelta(
            days=6,
        )

        if not (
            week_start
            <= event_date
            <= week_end
        ):
            return slots

        event_weekday = Weekday(
            event_date.weekday()
        )

        updated_slots = list(slots)

        event_index = next(
            (
                index
                for index, slot in enumerate(
                    updated_slots
                )
                if slot.weekday == event_weekday
            ),
            None,
        )

        if event_index is None:
            return slots

        original_slot = updated_slots[
            event_index
        ]

        race_duration = Planner._event_duration_minutes(
            next_event
        )

        if (
            race_duration is None
            and original_slot.duration_minutes is not None
        ):
            race_duration = (
                original_slot.duration_minutes
            )

        event_name = (
            getattr(
                event,
                "name",
                "",
            ).strip()
            or "Race"
        )

        updated_slots[event_index] = (
            DraftTrainingSlot(
                weekday=event_weekday,
                purpose=SessionPurpose.RACE,
                duration_minutes=race_duration,
                notes=(
                    f"Registered event: {event_name}."
                ),
            )
        )

        if original_slot.is_rest:
            updated_slots = (
                Planner._remove_replaced_training_session(
                    slots=updated_slots,
                    race_weekday=event_weekday,
                )
            )

        return tuple(
            sorted(
                updated_slots,
                key=lambda slot: slot.weekday.value,
            )
        )


    @staticmethod
    def _event_duration_minutes(
        next_event,
    ) -> int | None:
        """
        Returns the event target time in whole minutes, when available.
        """

        target_time = getattr(
            next_event,
            "target_time",
            None,
        )

        if target_time is None:
            return None

        minutes = int(
            target_time.total_seconds()
            // 60
        )

        if minutes <= 0:
            return None

        return minutes


    @staticmethod
    def _remove_replaced_training_session(
        *,
        slots: list[DraftTrainingSlot],
        race_weekday: Weekday,
    ) -> list[DraftTrainingSlot]:
        """
        Removes one ordinary training session when a race replaces a rest day.

        Short easy sessions are removed first. Quality and long sessions are
        only removed when no lower-priority session exists.
        """

        removal_priority = {
            SessionPurpose.EASY: 0,
            SessionPurpose.CROSS_TRAINING: 1,
            SessionPurpose.RECOVERY: 2,
            SessionPurpose.INTENSITY: 3,
            SessionPurpose.LONG: 4,
        }

        candidates = [
            slot
            for slot in slots
            if slot.weekday != race_weekday
            and slot.is_training
            and slot.purpose
            is not SessionPurpose.RACE
            and slot.purpose
            is not SessionPurpose.SHAKEOUT
        ]

        if not candidates:
            return slots

        selected = min(
            candidates,
            key=lambda slot: (
                removal_priority.get(
                    slot.purpose,
                    5,
                ),
                slot.duration_minutes or 0,
                slot.weekday.value,
            ),
        )

        return [
            (
                DraftTrainingSlot.rest(
                    slot.weekday,
                    notes=(
                        "Rest assigned because the registered "
                        "event counts as a weekly session."
                    ),
                )
                if slot.weekday == selected.weekday
                else slot
            )
            for slot in slots
        ]

    # ======================================================

    @staticmethod
    def _block_demanding_event_recovery_days(
        *,
        constraints: TrainingConstraints,
        context: CoachContext,
        week_start: date,
    ) -> TrainingConstraints:
        """
        Protects the first 48 hours after a demanding
        competition from planned running.
        """

        if (
            not context.is_post_race
            or context.days_since_event != 1
        ):
            return constraints

        previous_entry = context.previous_event

        event = getattr(
            previous_entry,
            "event",
            None,
        )

        effort_distance = getattr(
            event,
            "effort_distance",
            None,
        )

        if (
            effort_distance is None
            or effort_distance
            < DEMANDING_EVENT_EFFORT_DISTANCE
        ):
            return constraints

        week_end = (
            week_start
            + timedelta(days=6)
        )

        protected_days = []

        for day_offset in range(
            DEMANDING_EVENT_COMPLETE_REST_DAYS
        ):

            protected_date = (
                context.today
                + timedelta(days=day_offset)
            )

            if (
                week_start
                <= protected_date
                <= week_end
            ):
                protected_days.append(
                    Weekday(
                        protected_date.weekday()
                    )
                )

        return replace(
            constraints,
            blocked_days=tuple(
                dict.fromkeys(
                    (
                        *constraints.blocked_days,
                        *protected_days,
                    )
                )
            ),
        )

    # ======================================================

    @staticmethod
    def _block_past_weekdays(
        *,
        constraints: TrainingConstraints,
        week_start: date,
        today: date,
    ) -> TrainingConstraints:
        """
        Prevents the current plan from prescribing workouts
        on days that have already passed.
        """

        week_end = week_start + timedelta(
            days=6
        )

        if not (
            week_start
            <= today
            <= week_end
        ):
            return constraints

        past_days = tuple(
            Weekday(day_index)
            for day_index in range(
                today.weekday()
            )
        )

        return replace(
            constraints,
            blocked_days=(
                *constraints.blocked_days,
                *past_days,
            ),
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

    @staticmethod
    def _print_diagnostics(
        *,
        strategy_plan,
        workouts,
    ) -> None:
        """
        Temporary console diagnostics for weekly-plan generation.

        Remove this method after validating the coaching pipeline.
        """

        separator = "=" * 72

        print()
        print(separator)
        print("PERFORMANCELAB — GENERATED WEEKLY PLAN")
        print(separator)

        print(
            "Strategy:",
            getattr(
                strategy_plan,
                "strategy",
                None,
            ),
        )

        print(
            "Phase:",
            getattr(
                strategy_plan,
                "phase",
                None,
            ),
        )

        print(
            "Focus:",
            getattr(
                strategy_plan,
                "focus",
                None,
            ),
        )

        print(
            "Target sessions:",
            getattr(
                strategy_plan,
                "target_sessions",
                None,
            ),
        )

        print(
            "Intensity sessions:",
            getattr(
                strategy_plan,
                "intensity_sessions",
                None,
            ),
        )

        print(
            "Long sessions:",
            getattr(
                strategy_plan,
                "long_sessions",
                None,
            ),
        )

        print("-" * 72)

        if not workouts:
            print("No workouts generated.")

        for workout in workouts:
            duration_minutes = None

            if workout.duration is not None:
                duration_minutes = int(
                    workout.duration.total_seconds()
                    // 60
                )

            print(
                f"{workout.day} | "
                f"{workout.sport or 'rest'} | "
                f"{workout.title or 'Rest'} | "
                f"{duration_minutes or '-'} min | "
                f"{workout.intensity or '-'}"
            )

            if workout.objective:
                print(
                    f"  Objective: {workout.objective}"
                )

            if workout.structure:
                print("  Structure:")

                for step in workout.structure:
                    print(f"    - {step}")

        print(separator)
        print()

    def __repr__(self) -> str:
        return (
            "Planner("
            f"structure_generator={self.structure_generator!r}, "
            f"workout_generator={self.workout_generator!r})"
        )