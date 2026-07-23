"""
Tests for Planner.

Place this file at:
    tests/coaching/test_planner.py

It reuses the fixtures defined in tests/coaching/conftest.py.
"""

from datetime import date
from unittest.mock import Mock

import pytest

from performancelab.athlete import Athlete
from performancelab.training.planning.planner import Planner


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