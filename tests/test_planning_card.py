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
        == "12 km · 450 m D+"
    )