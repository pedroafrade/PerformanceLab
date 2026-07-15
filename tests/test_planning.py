"""
PerformanceLab

Tests for planning analytics.
"""

from datetime import date, timedelta

from performancelab.goals import Goal
from performancelab.goals import GoalBook

from performancelab.race import Event, EventEntry
from performancelab.race import EventBook

from performancelab.analysis.planning.planning import (
    next_goal,
    days_until_next_goal,
    active_goals,
    next_event,
    days_until_next_event,
    upcoming_events,
)


# ======================================================
# Helpers
# ======================================================

def create_goal(goal_date):

    goal = Goal()

    goal.date = goal_date

    return goal


def create_event(event_date):

    event = Event(

        date=event_date,

    )

    return EventEntry(

        event=event,

    )


# ======================================================
# Goal tests
# ======================================================

def test_next_goal():

    goals = GoalBook()

    goals.add(create_goal(date.today() + timedelta(days=20)))
    goals.add(create_goal(date.today() + timedelta(days=10)))

    assert next_goal(goals).date == date.today() + timedelta(days=10)


def test_days_until_next_goal():

    goals = GoalBook()

    goals.add(create_goal(date.today() + timedelta(days=15)))

    assert days_until_next_goal(goals) == 15


def test_active_goals():

    goals = GoalBook()

    goals.add(create_goal(date.today() + timedelta(days=10)))
    goals.add(create_goal(date.today() - timedelta(days=5)))

    assert len(active_goals(goals)) == 1


def test_empty_goalbook():

    goals = GoalBook()

    assert next_goal(goals) is None
    assert days_until_next_goal(goals) is None
    assert active_goals(goals) == []


# ======================================================
# Event tests
# ======================================================

def test_next_event():

    events = EventBook()

    events.add(create_event(date.today() + timedelta(days=30)))
    events.add(create_event(date.today() + timedelta(days=5)))

    assert next_event(events).event.date == date.today() + timedelta(days=5)


def test_days_until_next_event():

    events = EventBook()

    events.add(create_event(date.today() + timedelta(days=8)))

    assert days_until_next_event(events) == 8


def test_upcoming_events():

    events = EventBook()

    events.add(create_event(date.today() + timedelta(days=5)))
    events.add(create_event(date.today() - timedelta(days=5)))
    events.add(create_event(date.today() + timedelta(days=20)))

    assert len(upcoming_events(events)) == 2


def test_empty_eventbook():

    events = EventBook()

    assert next_event(events) is None
    assert days_until_next_event(events) is None
    assert upcoming_events(events) == []