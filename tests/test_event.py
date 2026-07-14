"""
Tests for Event and EventEntry.
"""

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