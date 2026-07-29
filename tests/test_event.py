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

def test_event_has_stable_identity():

    event = Event(
        name="Trail Serra da Estrela",
    )

    assert isinstance(
        event.event_id,
        str,
    )

    assert event.event_id


def test_events_have_different_identities():

    first_event = Event(
        name="First Event",
    )

    second_event = Event(
        name="Second Event",
    )

    assert (
        first_event.event_id
        != second_event.event_id
    )


def test_event_accepts_existing_identity():

    event = Event(
        name="Sealand",
        event_id="event-sealand-2026",
    )

    assert (
        event.event_id
        == "event-sealand-2026"
    )


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

def test_event_elevation_metres_per_kilometre():

    event = Event(
        sport="Trail Running",
        distance=23,
        elevation_gain=950,
    )

    assert (
        event.elevation_metres_per_kilometre
        == pytest.approx(950 / 23)
    )


@pytest.mark.parametrize(
    (
        "distance",
        "elevation_gain",
        "expected_demand",
    ),
    (
        (10, 50, "flat"),
        (10, 113, "rolling"),
        (20, 600, "hilly"),
        (23, 950, "mountainous"),
    ),
)
def test_running_event_elevation_demand(
    distance,
    elevation_gain,
    expected_demand,
):

    event = Event(
        sport="Trail Running",
        distance=distance,
        elevation_gain=elevation_gain,
    )

    assert (
        event.elevation_demand
        == expected_demand
    )


def test_non_running_event_has_no_elevation_demand():

    event = Event(
        sport="Cycling",
        distance=100,
        elevation_gain=1500,
    )

    assert event.elevation_demand is None


def test_event_without_distance_has_no_elevation_demand():

    event = Event(
        sport="Trail Running",
        distance=None,
        elevation_gain=950,
    )

    assert event.elevation_demand is None