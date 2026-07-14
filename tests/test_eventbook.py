from performancelab.race import Event
from performancelab.race import EventEntry
from performancelab.race import EventBook


def test_eventbook_creation():

    calendar = EventBook()

    assert len(calendar) == 0


def test_add_event():

    calendar = EventBook()

    event = Event(name="Trail")

    entry = EventEntry(event=event)

    calendar.add(entry)

    assert len(calendar) == 1

    assert calendar[0] == entry


def test_remove_event():

    calendar = EventBook()

    event = Event(name="Trail")

    entry = EventEntry(event=event)

    calendar.add(entry)

    calendar.remove(entry)

    assert len(calendar) == 0


def test_clear_eventbook():

    calendar = EventBook()

    calendar.add(EventEntry(event=Event(name="A")))

    calendar.add(EventEntry(event=Event(name="B")))

    calendar.clear()

    assert len(calendar) == 0