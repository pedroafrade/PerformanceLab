"""
PerformanceLab

Integration tests for AthleteAnalytics.
"""

from datetime import date
from datetime import timedelta

from performancelab import Athlete
from performancelab import Workout
from performancelab import Goal
from performancelab import Event
from performancelab import EventEntry


# ======================================================

def create_workout():

    workout = Workout()

    workout.info.date = date.today()

    workout.info.duration = timedelta(hours=1)

    workout.info.distance = 10.0

    workout.info.elevation_gain = 250

    workout.info.sport = "Running"

    return workout


# ======================================================

def create_goal():

    return Goal(

        name="Spring Marathon",

        date=date.today() + timedelta(days=30),

    )


# ======================================================

def create_event():

    event = Event(

        name="Spring Marathon",

        date=date.today() + timedelta(days=30),

    )

    return EventEntry(event=event)


# ======================================================

def test_athlete_analytics():

    athlete = Athlete(name="Pedro")

    athlete.history.add(create_workout())

    athlete.goals.add(create_goal())

    athlete.events.add(create_event())

    analytics = athlete.analytics

    assert analytics.total_distance == 10.0

    assert analytics.total_duration == timedelta(hours=1)

    assert analytics.total_elevation == 250

    assert analytics.training_days == 1

    assert analytics.current_streak == 1

    assert analytics.longest_streak == 1

    assert analytics.next_goal is not None

    assert analytics.next_event is not None

    assert len(analytics.active_goals) == 1

    assert len(analytics.upcoming_events) == 1


# ======================================================

def test_empty_athlete():

    athlete = Athlete()

    analytics = athlete.analytics

    assert analytics.total_duration == timedelta()

    assert analytics.training_days == 0

    assert analytics.current_streak == 0

    assert analytics.longest_streak == 0

    assert analytics.next_goal is None

    assert analytics.next_event is None

    assert analytics.active_goals == []

    assert analytics.upcoming_events == []


# ======================================================

def test_repr():

    athlete = Athlete(name="Pedro")

    assert "AthleteAnalytics" in repr(athlete.analytics)