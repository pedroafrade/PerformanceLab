from datetime import timedelta
from types import SimpleNamespace

from app.components.dashboard.cards.planning_card import (
    _day_details,
)


def test_long_run_displays_distance_and_elevation():

    day = SimpleNamespace(
        completed=False,
        completed_title=None,
        completed_sport=None,
        title="Long Aerobic Run",
        sport="Trail Running",
        distance=11.5,
        elevation_gain=450,
        duration=timedelta(
            minutes=120
        ),
        intensity="Easy to moderate",
    )

    assert (
        _day_details(day)
        == "12 km · 450 D+"
    )

def test_uses_workout_prescription_summary():

    day = SimpleNamespace(
        completed=False,
        completed_title=None,
        completed_sport=None,
        title="Hill Run",
        sport="Trail Running",
        prescription_summary=(
            "10×60 sec uphill"
        ),
        distance=None,
        elevation_gain=None,
        duration=timedelta(
            minutes=60
        ),
        intensity="Hard",
    )

    assert (
        _day_details(day)
        == "10×60 sec uphill"
    )
def test_displays_equivalent_outcome():

    day = SimpleNamespace(
        completed=True,
        completed_title="Easy Run",
        completed_sport="Running",
        outcome_status="equivalent",
        title="Easy Run",
        sport="Running",
        prescription_summary=None,
        distance=None,
        elevation_gain=None,
        duration=timedelta(
            minutes=60
        ),
        intensity="Easy",
    )

    assert (
        _day_details(day)
        == "Equivalent · 1h · Easy"
    )


def test_displays_substitute_activity():

    day = SimpleNamespace(
        completed=True,
        completed_title="Endurance Ride",
        completed_sport="Cycling",
        outcome_status="substitute",
        title="Easy Run",
        sport="Running",
        prescription_summary=None,
        distance=None,
        elevation_gain=None,
        duration=timedelta(
            minutes=60
        ),
        intensity="Easy",
    )

    assert (
        _day_details(day)
        == (
            "Substitute · "
            "Feito: Endurance Ride"
        )
    )


def test_displays_missed_outcome():

    day = SimpleNamespace(
        completed=False,
        completed_title=None,
        completed_sport=None,
        outcome_status="missed",
        title="Tempo Run",
        sport="Running",
        prescription_summary=None,
        distance=None,
        elevation_gain=None,
        duration=timedelta(
            minutes=50
        ),
        intensity="Hard",
    )

    assert (
        _day_details(day)
        == "Missed · 50 min · Hard"
    )