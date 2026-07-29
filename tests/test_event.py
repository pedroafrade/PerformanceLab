"""
Tests for Event and EventEntry.
"""

import pytest

from datetime import timedelta

from performancelab.race import Event
from performancelab.race import EventEntry


def test_event_creation():

    event = Event(

        name="Trail Serra da Estrela",

        sport="Trail Running",

        distance=22,

        elevation_gain=1200

    )

    assert event.name == "Trail Serra da Estrela"

    assert event.distance == 22

    assert event.elevation_gain == 1200


def test_event_entry_creation():

    event = Event(

        name="Trail Serra da Estrela"

    )

    entry = EventEntry(

        event=event,

        priority="A",

        target_time=timedelta(hours=2)

    )

    assert entry.priority == "A"

    assert entry.completed is False

    assert entry.pending is True

    assert entry.event.name == "Trail Serra da Estrela"

def test_running_event_effort_distance():

    event = Event(
        name="Sealand",
        sport="Road Running",
        distance=10,    
        elevation_gain=113,
    )

    assert event.effort_distance == pytest.approx(
        11.13
    )


def test_trail_event_has_greater_effort_distance():

    road_event = Event(
        name="Sealand",
        sport="Road Running",
        distance=10,
        elevation_gain=113,
    )

    trail_event = Event(
        name="III Trail Pé Firme",
        sport="Trail Running",
        distance=23,
        elevation_gain=950,
    )

    assert (
        trail_event.effort_distance
        > road_event.effort_distance
    )

    assert trail_event.effort_distance == pytest.approx(
        32.5
    )


def test_non_running_event_has_no_effort_distance():

    event = Event(
        name="Cycling Event",
        sport="Cycling",
        distance=100,
        elevation_gain=1500,
    )

    assert event.effort_distance is None