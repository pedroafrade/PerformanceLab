"""
PerformanceLab

Planning Analytics

Utilities for analysing future goals and events.
"""


# ======================================================
# Next goal
# ======================================================

def next_goal(goals):

    return goals.next


# ======================================================
# Days until next goal
# ======================================================

def days_until_next_goal(goals):

    goal = next_goal(goals)

    if goal is None:

        return None

    return goal.days_remaining


# ======================================================
# Active goals
# ======================================================

def active_goals(goals):

    return goals.active


# ======================================================
# Next event
# ======================================================

def next_event(events):

    return events.next


# ======================================================
# Days until next event
# ======================================================

def days_until_next_event(events):

    entry = next_event(events)

    if entry is None:

        return None

    return entry.event.days_remaining


# ======================================================
# Upcoming events
# ======================================================

def upcoming_events(events):

    return events.upcoming