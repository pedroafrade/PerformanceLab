"""
PerformanceLab

Planning Analytics

Utilities for analysing future goals and events.
"""

from datetime import date


# ======================================================
# Next goal
# ======================================================

def next_goal(goals):

    upcoming = [

        goal

        for goal in goals

        if (
            getattr(goal, "date", None) is not None
            and goal.date >= date.today()
        )

    ]

    if not upcoming:

        return None

    return min(upcoming, key=lambda goal: goal.date)


# ======================================================
# Days until next goal
# ======================================================

def days_until_next_goal(goals):

    goal = next_goal(goals)

    if goal is None:

        return None

    return (goal.date - date.today()).days


# ======================================================
# Active goals
# ======================================================

def active_goals(goals):

    return [

        goal

        for goal in goals

        if (
            getattr(goal, "completed", False) is False
            and getattr(goal, "date", None) is not None
            and goal.date >= date.today()
        )

    ]


# ======================================================
# Next event
# ======================================================

def next_event(events):

    upcoming = []

    for item in events:

        event = getattr(item, "event", item)

        if (
            getattr(event, "date", None) is not None
            and event.date >= date.today()
        ):
            upcoming.append(item)

    if not upcoming:
        return None

    return min(
        upcoming,
        key=lambda item: getattr(item, "event", item).date,
    )


# ======================================================
# Days until next event
# ======================================================

def days_until_next_event(events):

    item = next_event(events)

    if item is None:
        return None

    event = getattr(item, "event", item)

    return (event.date - date.today()).days


# ======================================================
# Upcoming events
# ======================================================

def upcoming_events(events):

    result = []

    for item in events:

        event = getattr(item, "event", item)

        if (
            getattr(event, "date", None) is not None
            and event.date >= date.today()
        ):
            result.append(item)

    return result