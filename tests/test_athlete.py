"""
Tests for Athlete.
"""

from performancelab import Athlete


def test_athlete_creation():

    athlete = Athlete(name="Pedro")

    assert athlete.name == "Pedro"

    assert len(athlete.history) == 0

    assert len(athlete.goals) == 0

    assert len(athlete.calendar) == 0

    assert athlete.analytics is not None