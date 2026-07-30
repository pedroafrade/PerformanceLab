"""
Tests for Planner.

Place this file at:
    tests/coaching/test_planner.py

It reuses the fixtures defined in tests/coaching/conftest.py.
"""

from datetime import date, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from performancelab.training.load import (
    planned_weekly_load,
)

from performancelab.athlete import Athlete
from performancelab.race import (
    Event,
    EventEntry,
)

from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
    WeeklyPlan,
)
from performancelab.training.planning.planner import Planner

from performancelab.training.config import (
    Weekday,
)

@pytest.fixture
def athlete() -> Athlete:
    return Athlete(name="John")


def test_uses_injected_generators(
    athlete,
    full_availability,
    default_preferences,
    default_constraints,
):
    structure_generator = Mock()
    workout_generator = Mock()

    structure_generator.generate.return_value = ()
    workout_generator.generate.return_value = ()

    planner = Planner(
        structure_generator=structure_generator,
        workout_generator=workout_generator,
    )

    planner.build(
        athlete=athlete,
        availability=full_availability,
        preferences=default_preferences,
        constraints=default_constraints,
    )

    structure_generator.generate.assert_called_once()
    workout_generator.generate.assert_called_once()


@pytest.mark.parametrize(
    "field,value,error",
    [
        ("athlete", object(), "Athlete"),
        ("availability", object(), "AthleteAvailability"),
        ("preferences", object(), "AthletePreferences"),
        ("constraints", object(), "TrainingConstraints"),
    ],
)
def test_rejects_invalid_inputs(
    athlete,
    full_availability,
    default_preferences,
    default_constraints,
    field,
    value,
    error,
):
    planner = Planner()

    kwargs = {
        "athlete": athlete,
        "availability": full_availability,
        "preferences": default_preferences,
        "constraints": default_constraints,
    }
    kwargs[field] = value

    with pytest.raises(TypeError, match=error):
        planner.build(**kwargs)


def test_rejects_invalid_today(
    athlete,
    full_availability,
    default_preferences,
    default_constraints,
):
    planner = Planner()

    with pytest.raises(TypeError, match="today"):
        planner.build(
            athlete=athlete,
            availability=full_availability,
            preferences=default_preferences,
            constraints=default_constraints,
            today="today",
        )


def test_rejects_invalid_week_start(
    athlete,
    full_availability,
    default_preferences,
    default_constraints,
):
    planner = Planner()

    with pytest.raises(TypeError, match="week_start"):
        planner.build(
            athlete=athlete,
            availability=full_availability,
            preferences=default_preferences,
            constraints=default_constraints,
            week_start="monday",
        )


def test_normalizes_week_start():
    planner = Planner()

    monday = planner._week_start(date(2026, 7, 22))

    assert monday == date(2026, 7, 20)


def test_repr():
    planner = Planner()

    representation = repr(planner)

    assert "Planner" in representation
    assert "structure_generator" in representation
    assert "workout_generator" in representation

def test_blocks_weekdays_before_today(
    athlete,
    full_availability,
    default_preferences,
    default_constraints,
):
    structure_generator = Mock()
    workout_generator = Mock()

    structure_generator.generate.return_value = ()
    workout_generator.generate.return_value = ()

    planner = Planner(
        structure_generator=structure_generator,
        workout_generator=workout_generator,
    )

    planner.build(
        athlete=athlete,
        availability=full_availability,
        preferences=default_preferences,
        constraints=default_constraints,
        today=date(2026, 7, 29),
    )

    used_constraints = (
        structure_generator
        .generate
        .call_args
        .kwargs["constraints"]
    )

    assert used_constraints.is_blocked(
        Weekday.MONDAY
    )
    assert used_constraints.is_blocked(
        Weekday.TUESDAY
    )
    assert not used_constraints.is_blocked(
        Weekday.WEDNESDAY
    )
def test_builds_training_plan_for_competition_block(
    full_availability,
    default_preferences,
    default_constraints,
):

    athlete = Athlete(
        name="Pedro",
    )

    athlete.events.add(
        EventEntry(
            event=Event(
                event_id="event-sealand",
                name="Sealand",
                date=date(
                    2026,
                    9,
                    13,
                ),
                sport="Road Running",
                distance=10,
                elevation_gain=113,
            ),
            priority="A",
        )
    )

    athlete.events.add(
        EventEntry(
            event=Event(
                event_id="event-trail-pe-firme",
                name="III Trail Pé Firme",
                date=date(
                    2026,
                    9,
                    27,
                ),
                sport="Trail Running",
                distance=23,
                elevation_gain=950,
            ),
            priority="A",
        )
    )

    structure_generator = Mock()
    workout_generator = Mock()

    structure_generator.generate.return_value = ()

    first_workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            7,
            29,
            18,
            0,
        ),
        sport="Trail Running",
        title="Hill Run",
    )

    workout_generator.generate.return_value = (
        first_workout,
    )

    planner = Planner(
        structure_generator=structure_generator,
        workout_generator=workout_generator,
    )

    plan = planner.build_training_plan(
        athlete=athlete,
        availability=full_availability,
        preferences=default_preferences,
        constraints=default_constraints,
        today=date(
            2026,
            7,
            29,
        ),
    )

    assert isinstance(
        plan,
        TrainingPlan,
    )

    assert plan.start_date == date(
        2026,
        7,
        29,
    )

    assert plan.end_date == date(
        2026,
        10,
        4,
    )

    assert (
        plan.primary_event_id
        == "event-trail-pe-firme"
    )

    assert plan.competition_event_ids == (
        "event-sealand",
        "event-trail-pe-firme",
    )

    assert len(plan) == 1
    assert plan[0] is first_workout

def test_training_plan_without_event_uses_week_horizon(
    athlete,
    full_availability,
    default_preferences,
    default_constraints,
):

    structure_generator = Mock()
    workout_generator = Mock()

    structure_generator.generate.return_value = ()
    workout_generator.generate.return_value = ()

    planner = Planner(
        structure_generator=structure_generator,
        workout_generator=workout_generator,
    )

    plan = planner.build_training_plan(
        athlete=athlete,
        availability=full_availability,
        preferences=default_preferences,
        constraints=default_constraints,
        today=date(
            2026,
            7,
            29,
        ),
    )

    assert plan.start_date == date(
        2026,
        7,
        29,
    )

    assert plan.end_date == date(
        2026,
        8,
        2,
    )

    assert plan.primary_event_id is None
    assert plan.competition_event_ids == ()

def test_training_plan_includes_post_event_recovery_week(
    full_availability,
    default_preferences,
    default_constraints,
):

    athlete = Athlete(
        name="Pedro",
    )

    athlete.events.add(
        EventEntry(
            event=Event(
                event_id="event-primary",
                name="Primary Trail",
                date=date(
                    2026,
                    9,
                    27,
                ),
                sport="Trail Running",
                distance=23,
                elevation_gain=950,
            ),
            priority="A",
        )
    )

    structure_generator = Mock()
    workout_generator = Mock()

    structure_generator.generate.return_value = ()

    def generate_week_workout(
        *,
        strategy_plan,
        training_week,
        coach_context,
    ):

        workout_day = (
            training_week.start_date
            + timedelta(days=2)
        )

        return (
            PlannedWorkout(
                scheduled_at=datetime.combine(
                    workout_day,
                    datetime.min.time(),
                ),
                sport="Trail Running",
                title="Weekly Run",
            ),
        )

    workout_generator.generate.side_effect = (
        generate_week_workout
    )

    planner = Planner(
        structure_generator=structure_generator,
        workout_generator=workout_generator,
    )

    plan = planner.build_training_plan(
        athlete=athlete,
        availability=full_availability,
        preferences=default_preferences,
        constraints=default_constraints,
        today=date(
            2026,
            7,
            29,
        ),
    )

    assert plan.start_date == date(
        2026,
        7,
        29,
    )

    assert plan.end_date == date(
        2026,
        10,
        4,
    )

    assert len(plan) == 10

    assert plan.first.day == date(
        2026,
        7,
        29,
    )

    assert plan.last.day == date(
        2026,
        9,
        30,
    )

    assert all(
        plan.covers(workout.day)
        for workout in plan
    )

def test_limits_planned_weekly_load_growth():

    weekly_plan = WeeklyPlan(
        start_date=date(
            2026,
            8,
            3,
        ),
        end_date=date(
            2026,
            8,
            9,
        ),
        workouts=[
            PlannedWorkout(
                scheduled_at=datetime(
                    2026,
                    8,
                    3,
                ),
                title="Monday Quality",
                duration=timedelta(
                    minutes=60,
                ),
                intensity="Hard",
            ),
            PlannedWorkout(
                scheduled_at=datetime(
                    2026,
                    8,
                    5,
                ),
                title="Wednesday Quality",
                duration=timedelta(
                    minutes=60,
                ),
                intensity="Hard",
            ),
            PlannedWorkout(
                scheduled_at=datetime(
                    2026,
                    8,
                    7,
                ),
                title="Easy Aerobic Run",
                duration=timedelta(
                    minutes=60,
                ),
                intensity="Easy",
            ),
            PlannedWorkout(
                scheduled_at=datetime(
                    2026,
                    8,
                    9,
                ),
                title="Long Aerobic Run",
                duration=timedelta(
                    minutes=90,
                ),
                intensity="Easy to moderate",
            ),
        ],
    )

    result = Planner._limit_weekly_load_growth(
        weekly_plan=weekly_plan,
        previous_weekly_load=1000,
    )

    titles = tuple(
        workout.title
        for workout in result.workouts
    )

    assert (
        "Monday Quality"
        not in titles
    )

    assert (
        "Wednesday Quality"
        in titles
    )

    assert (
        "Long Aerobic Run"
        in titles
    )

    assert planned_weekly_load(
        result.workouts
    ) <= 1100

def test_moves_intensity_away_from_previous_long_run():

    previous_long = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            2,
        ),
        sport="Trail Running",
        title="Long Aerobic Run",
        duration=timedelta(
            minutes=105,
        ),
        intensity="Easy to moderate",
    )

    monday_hills = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            3,
        ),
        sport="Trail Running",
        title="Hill Run",
        duration=timedelta(
            minutes=70,
        ),
        intensity="Hard",
    )

    wednesday_easy = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            5,
        ),
        sport="Trail Running",
        title="Easy Aerobic Run",
        duration=timedelta(
            minutes=65,
        ),
        intensity="Easy",
    )

    friday_long = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            7,
        ),
        sport="Trail Running",
        title="Long Aerobic Run",
        duration=timedelta(
            minutes=105,
        ),
        intensity="Easy to moderate",
    )

    weekly_plan = WeeklyPlan(
        start_date=date(
            2026,
            8,
            3,
        ),
        end_date=date(
            2026,
            8,
            9,
        ),
        workouts=[
            monday_hills,
            wednesday_easy,
            friday_long,
        ],
    )

    result = Planner._protect_week_boundary(
        weekly_plan=weekly_plan,
        previous_workout=previous_long,
    )

    shifted_hills = next(
        workout
        for workout in result.workouts
        if workout.title == "Hill Run"
    )

    assert shifted_hills.day == date(
        2026,
        8,
        4,
    )

    assert monday_hills.day == date(
        2026,
        8,
        3,
    )

def test_blocks_running_after_demanding_event(
    default_constraints,
):

    context = SimpleNamespace(
        is_post_race=True,
        days_since_event=1,
        today=date(
            2026,
            9,
            28,
        ),
        previous_event=SimpleNamespace(
            event=SimpleNamespace(
                effort_distance=32.5,
            ),
        ),
    )

    result = (
        Planner._block_demanding_event_recovery_days(
            constraints=default_constraints,
            context=context,
            week_start=date(
                2026,
                9,
                28,
            ),
        )
    )

    assert result.is_blocked(
        Weekday.MONDAY
    )
    assert result.is_blocked(
        Weekday.TUESDAY
    )
    assert not result.is_blocked(
        Weekday.WEDNESDAY
    )
def test_keeps_active_recovery_after_short_event(
    default_constraints,
):

    context = SimpleNamespace(
        is_post_race=True,
        days_since_event=1,
        today=date(
            2026,
            9,
            14,
        ),
        previous_event=SimpleNamespace(
            event=SimpleNamespace(
                effort_distance=11.1,
            ),
        ),
    )

    result = (
        Planner._block_demanding_event_recovery_days(
            constraints=default_constraints,
            context=context,
            week_start=date(
                2026,
                9,
                14,
            ),
        )
    )

    assert result == default_constraints

def test_does_not_limit_recovery_week_after_race():

    race = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            9,
            27,
        ),
        title="Race",
        intensity="Race effort",
    )

    assert (
        Planner._should_limit_weekly_load(
            race
        )
        is False
    )
def test_keeps_load_limit_after_normal_training():

    easy_run = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            9,
            20,
        ),
        title="Easy Aerobic Run",
        intensity="Easy",
    )

    assert (
        Planner._should_limit_weekly_load(
            easy_run
        )
        is True
    )