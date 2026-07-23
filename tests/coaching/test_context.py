"""
Tests for CoachContext.
"""

from datetime import date
from types import SimpleNamespace

from performancelab.coaching import CoachContext


def make_athlete(
    *,
    ctl=50.0,
    atl=45.0,
    tsb=5.0,
    next_event=None,
    days_until_event=None,
    sports=("Running",),
    average_rpe=5.5,
    training_plan=None,
):
    """
    Creates a minimal athlete-like object containing the
    analytics interface required by CoachContext.
    """

    if training_plan is None:
        training_plan = object()

    analytics = SimpleNamespace(
        ctl=ctl,
        atl=atl,
        tsb=tsb,
        next_event=next_event,
        days_until_next_event=days_until_event,
        sports=sports,
        average_rpe=average_rpe,
        training_plan=training_plan,
    )

    return SimpleNamespace(
        name="Test Athlete",
        analytics=analytics,
    )


def test_context_uses_athlete_analytics():

    athlete = make_athlete(
        ctl=52.3,
        atl=48.1,
        tsb=4.2,
        sports=("Running", "Cycling"),
        average_rpe=6.0,
    )

    reference_date = date(2026, 3, 10)

    context = CoachContext.from_athlete(
        athlete,
        today=reference_date,
    )

    assert context.athlete is athlete
    assert context.today == reference_date

    assert context.ctl == 52.3
    assert context.atl == 48.1
    assert context.tsb == 4.2

    assert context.sports == (
        "Running",
        "Cycling",
    )

    assert context.average_rpe == 6.0


def test_context_without_events():

    athlete = make_athlete(
        next_event=None,
        days_until_event=None,
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date(2026, 3, 10),
    )

    assert context.next_event is None
    assert context.days_until_event is None


def test_context_with_next_event():

    event_entry = SimpleNamespace(
        event=SimpleNamespace(
            name="Lisbon Half Marathon",
        ),
        priority="A",
    )

    athlete = make_athlete(
        next_event=event_entry,
        days_until_event=84,
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date(2026, 3, 10),
    )

    assert context.next_event is event_entry
    assert context.days_until_event == 84

    assert (
        context.next_event.event.name
        == "Lisbon Half Marathon"
    )


def test_context_preserves_training_plan():

    training_plan = object()

    athlete = make_athlete(
        training_plan=training_plan,
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date(2026, 3, 10),
    )

    assert context.training_plan is training_plan


def test_context_converts_sports_to_tuple():

    athlete = make_athlete(
        sports=[
            "Running",
            "Swimming",
        ],
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date(2026, 3, 10),
    )

    assert isinstance(
        context.sports,
        tuple,
    )

    assert context.sports == (
        "Running",
        "Swimming",
    )


def test_context_accepts_missing_average_rpe():

    athlete = make_athlete(
        average_rpe=None,
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date(2026, 3, 10),
    )

    assert context.average_rpe is None