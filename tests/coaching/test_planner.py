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

from dataclasses import replace

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
from performancelab.coaching.strategy import (
    StrategyPlan,
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

def test_blocks_monday_after_previous_sunday_long(
    athlete,
    full_availability,
    default_preferences,
    default_constraints,
):
    structure_generator = Mock()
    workout_generator = Mock()

    structure_generator.generate.return_value = ()
    workout_generator.generate.return_value = ()

    previous_long = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            9,
        ),
        sport="Trail Running",
        title="Long Aerobic Run",
        duration=timedelta(
            minutes=110,
        ),
        intensity="Easy to moderate",
    )

    planner = Planner(
        structure_generator=structure_generator,
        workout_generator=workout_generator,
    )

    planner.build(
        athlete=athlete,
        availability=full_availability,
        preferences=default_preferences,
        constraints=default_constraints,
        week_start=date(
            2026,
            8,
            10,
        ),
        today=date(
            2026,
            8,
            10,
        ),
        previous_planned_workout=(
            previous_long
        ),
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

    assert not used_constraints.is_blocked(
        Weekday.TUESDAY
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

    assert titles == (
        "Monday Quality",
        "Wednesday Quality",
        "Easy Aerobic Run",
        "Long Aerobic Run",
    )

    original_durations = {
        workout.title: workout.duration
        for workout in weekly_plan.workouts
    }

    result_durations = {
        workout.title: workout.duration
        for workout in result.workouts
    }

    assert (
        result_durations[
            "Monday Quality"
        ]
        < original_durations[
            "Monday Quality"
        ]
    )

    assert (
        result_durations[
            "Wednesday Quality"
        ]
        < original_durations[
            "Wednesday Quality"
        ]
    )

    assert (
        result_durations[
            "Easy Aerobic Run"
        ]
        < original_durations[
            "Easy Aerobic Run"
        ]
    )

    assert (
        result_durations[
            "Long Aerobic Run"
        ]
        == original_durations[
            "Long Aerobic Run"
        ]
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

def test_progresses_long_session_during_build():

    strategy_plan = StrategyPlan(
        strategy="BuildStrategy",
        phase="Build",
        volume_factor=1.0,
        target_sessions=4,
        intensity_sessions=1,
        long_sessions=1,
        recovery_days=2,
        target_weekly_minutes=300,
        long_session_minutes=105,
    )

    progressed = (
        Planner._progress_long_session_target(
            strategy_plan=strategy_plan,
            previous_long_minutes=105,
        )
    )

    assert (
        progressed.long_session_minutes
        == 110
    )


def test_peak_continues_long_session_progression():

    strategy_plan = StrategyPlan(
        strategy="PeakStrategy",
        phase="Peak",
        volume_factor=0.9,
        target_sessions=4,
        intensity_sessions=1,
        long_sessions=1,
        recovery_days=2,
        target_weekly_minutes=300,
        long_session_minutes=90,
    )

    progressed = (
        Planner._progress_long_session_target(
            strategy_plan=strategy_plan,
            previous_long_minutes=115,
        )
    )

    assert (
        progressed.long_session_minutes
        == 120
    )


def test_taper_does_not_progress_long_session():

    strategy_plan = StrategyPlan(
        strategy="TaperStrategy",
        phase="Taper",
        volume_factor=0.7,
        target_sessions=3,
        intensity_sessions=1,
        long_sessions=1,
        recovery_days=3,
        target_weekly_minutes=240,
        long_session_minutes=80,
    )

    result = (
        Planner._progress_long_session_target(
            strategy_plan=strategy_plan,
            previous_long_minutes=120,
        )
    )

    assert result is strategy_plan
    assert result.long_session_minutes == 80

def test_event_duration_caps_long_progression():

    strategy_plan = StrategyPlan(
        strategy="PeakStrategy",
        phase="Peak",
        volume_factor=0.9,
        target_sessions=4,
        intensity_sessions=1,
        long_sessions=1,
        recovery_days=2,
        target_weekly_minutes=300,
        long_session_minutes=120,
    )

    result = (
        Planner._progress_long_session_target(
            strategy_plan=strategy_plan,
            previous_long_minutes=145,
            event_duration=timedelta(
                hours=3,
                minutes=15,
            ),
        )
    )

    assert (
        result.long_session_minutes
        == 145
    )


def test_short_event_does_not_reduce_existing_long():

    strategy_plan = StrategyPlan(
        strategy="BuildStrategy",
        phase="Build",
        volume_factor=1.0,
        target_sessions=4,
        intensity_sessions=1,
        long_sessions=1,
        recovery_days=2,
        target_weekly_minutes=300,
        long_session_minutes=105,
    )

    result = (
        Planner._progress_long_session_target(
            strategy_plan=strategy_plan,
            previous_long_minutes=105,
            event_duration=timedelta(
                minutes=60,
            ),
        )
    )

    assert (
        result.long_session_minutes
        == 105
    )


def test_event_based_long_ceiling_uses_five_minutes():

    assert (
        Planner
        ._event_based_long_session_ceiling(
            timedelta(
                hours=3,
                minutes=15,
            )
        )
        == 145
    )

def test_automatic_planning_limits_consecutive_days(
    default_constraints,
):

    permissive_constraints = replace(
        default_constraints,
        max_consecutive_training_days=6,
    )

    result = (
        Planner
        ._limit_automatic_consecutive_days(
            permissive_constraints
        )
    )

    assert (
        result.max_consecutive_training_days
        == 2
    )

    assert (
        permissive_constraints
        .max_consecutive_training_days
        == 6
    )


def test_automatic_planning_preserves_stricter_limit(
    default_constraints,
):

    strict_constraints = replace(
        default_constraints,
        max_consecutive_training_days=1,
    )

    result = (
        Planner
        ._limit_automatic_consecutive_days(
            strict_constraints
        )
    )

    assert result is strict_constraints

    assert (
        result.max_consecutive_training_days
        == 1
    )

def test_removes_boundary_intensity_without_safe_day():

    previous_long = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            2,
        ),
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
        title="Hill Run",
        duration=timedelta(
            minutes=50,
        ),
        intensity="Hard",
    )

    wednesday_hills = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            5,
        ),
        title="Hill Run",
        duration=timedelta(
            minutes=50,
        ),
        intensity="Hard",
    )

    friday_easy = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            7,
        ),
        title="Easy Aerobic Run",
        duration=timedelta(
            minutes=50,
        ),
        intensity="Easy",
    )

    sunday_long = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            9,
        ),
        title="Long Aerobic Run",
        duration=timedelta(
            minutes=110,
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
            wednesday_hills,
            friday_easy,
            sunday_long,
        ],
    )

    result = Planner._protect_week_boundary(
        weekly_plan=weekly_plan,
        previous_workout=previous_long,
    )

    hill_days = [
        workout.day
        for workout in result.workouts
        if workout.title == "Hill Run"
    ]

    assert hill_days == [
        date(
            2026,
            8,
            5,
        )
    ]

    assert monday_hills not in result.workouts
    assert friday_easy in result.workouts
    assert sunday_long in result.workouts

def test_detects_partial_week():

    assert Planner._is_partial_week(
        week_start=date(
            2026,
            7,
            27,
        ),
        today=date(
            2026,
            7,
            30,
        ),
    )


def test_full_week_is_not_partial():

    assert not Planner._is_partial_week(
        week_start=date(
            2026,
            8,
            3,
        ),
        today=date(
            2026,
            8,
            3,
        ),
    )

def test_adapts_strategy_to_remaining_week():

    strategy_plan = StrategyPlan(
        strategy="BuildStrategy",
        phase="Build",
        volume_factor=1.0,
        target_sessions=4,
        intensity_sessions=2,
        long_sessions=1,
        recovery_days=2,
        target_weekly_minutes=260,
        target_weekly_load=400.0,
        long_session_minutes=105,
    )

    result = (
        Planner
        ._adapt_strategy_to_remaining_week(
            strategy_plan=strategy_plan,
            week_start=date(
                2026,
                7,
                27,
            ),
            today=date(
                2026,
                7,
                30,
            ),
        )
    )

    assert result.target_sessions == 2
    assert result.intensity_sessions == 1
    assert result.long_sessions == 1
    assert result.recovery_days == 5

    assert (
        result.target_weekly_minutes
        == 150
    )

    assert (
        result.target_weekly_load
        == pytest.approx(
            400 * 4 / 7
        )
    )


def test_full_week_keeps_strategy_unchanged():

    strategy_plan = StrategyPlan(
        strategy="BuildStrategy",
        phase="Build",
        volume_factor=1.0,
        target_sessions=4,
        intensity_sessions=2,
        long_sessions=1,
        recovery_days=2,
        target_weekly_minutes=260,
        target_weekly_load=400.0,
        long_session_minutes=105,
    )

    result = (
        Planner
        ._adapt_strategy_to_remaining_week(
            strategy_plan=strategy_plan,
            week_start=date(
                2026,
                8,
                3,
            ),
            today=date(
                2026,
                8,
                3,
            ),
        )
    )

    assert result is strategy_plan

def test_weekly_load_limit_preserves_pre_race_workout():

    weekly_plan = WeeklyPlan(
        start_date=date(
            2026,
            9,
            21,
        ),
        end_date=date(
            2026,
            9,
            27,
        ),
        workouts=[
            PlannedWorkout(
                scheduled_at=datetime(
                    2026,
                    9,
                    23,
                ),
                title=(
                    "Pre-Race Easy Run"
                ),
                duration=timedelta(
                    minutes=40,
                ),
                intensity="Easy",
            ),
            PlannedWorkout(
                scheduled_at=datetime(
                    2026,
                    9,
                    26,
                ),
                title="Shakeout Run",
                duration=timedelta(
                    minutes=20,
                ),
                intensity="Very easy",
            ),
            PlannedWorkout(
                scheduled_at=datetime(
                    2026,
                    9,
                    27,
                ),
                title="Race",
                duration=timedelta(
                    minutes=201,
                ),
                intensity="Race effort",
            ),
        ],
    )

    result = (
        Planner._limit_weekly_load_growth(
            weekly_plan=weekly_plan,
            previous_weekly_load=100.0,
        )
    )

    titles = tuple(
        workout.title
        for workout in result.workouts
    )

    assert titles == (
        "Pre-Race Easy Run",
        "Shakeout Run",
        "Race",
    )