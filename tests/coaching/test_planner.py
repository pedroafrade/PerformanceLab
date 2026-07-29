"""
Tests for Planner.

Place this file at:
    tests/coaching/test_planner.py

It reuses the fixtures defined in tests/coaching/conftest.py.
"""

from datetime import date, datetime
from unittest.mock import Mock

import pytest

from performancelab.athlete import Athlete
from performancelab.race import (
    Event,
    EventEntry,
)

from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
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
        9,
        27,
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