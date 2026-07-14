"""
Tests for Environment.
"""

from performancelab.workout import Environment


def test_environment_creation():

    env = Environment(

        temperature=18,

        terrain="Trail"

    )

    assert env.temperature == 18

    assert env.terrain == "Trail"