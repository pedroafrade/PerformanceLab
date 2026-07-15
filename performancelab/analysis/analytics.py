"""
PerformanceLab

AthleteAnalytics

Public analytics interface for an athlete.
"""

from performancelab.analysis.performance import (
    PerformanceManagementChart,
)
from performancelab.training import DailyLoadBuilder

from . import consistency
from . import time
from . import volume


class AthleteAnalytics:

    # ======================================================

    def __init__(self, athlete):

        self.athlete = athlete

    # ======================================================
    # Shortcuts
    # ======================================================

    @property
    def history(self):

        return self.athlete.history

    @property
    def goals(self):

        return self.athlete.goals

    @property
    def events(self):

        return self.athlete.events

    # ======================================================
    # Daily Training Load
    # ======================================================

    @property
    def daily_loads(self):

        return DailyLoadBuilder(

            self.history

        ).build()

    # ======================================================
    # Performance Management
    # ======================================================

    @property
    def pmc(self):

        return PerformanceManagementChart(

            daily_loads=self.daily_loads.loads,

        )

    # ======================================================

    @property
    def ctl(self):

        return self.pmc.current_ctl

    # ======================================================

    @property
    def atl(self):

        return self.pmc.current_atl

    # ======================================================

    @property
    def tsb(self):

        return self.pmc.current_tsb

    # ======================================================
    # Basic information
    # ======================================================

    @property
    def number_of_workouts(self):

        return len(self.history)

    @property
    def sports(self):

        return self.history.sports

    @property
    def first_workout(self):

        return self.history.first

    @property
    def last_workout(self):

        return self.history.last

    @property
    def average_rpe(self):

        values = [

            workout.feedback.rpe

            for workout in self.history

            if workout.feedback.rpe is not None

        ]

        if not values:

            return None

        return sum(values) / len(values)

    # ======================================================
    # Volume
    # ======================================================

    @property
    def total_distance(self):

        return volume.total_distance(self.history)

    @property
    def total_duration(self):

        return volume.total_duration(self.history)

    @property
    def total_elevation(self):

        return volume.total_elevation(self.history)

    @property
    def average_distance(self):

        return volume.average_distance(self.history)

    @property
    def average_duration(self):

        return volume.average_duration(self.history)

    @property
    def average_elevation(self):

        return volume.average_elevation(self.history)

    # ======================================================
    # Time
    # ======================================================

    @property
    def training_days(self):

        return time.training_days(self.history)

    @property
    def first_training_date(self):

        return time.first_training_date(self.history)

    @property
    def last_training_date(self):

        return time.last_training_date(self.history)

    # ======================================================
    # Consistency
    # ======================================================

    @property
    def current_streak(self):

        return consistency.current_streak(self.history)

    @property
    def longest_streak(self):

        return consistency.longest_streak(self.history)

    # ======================================================
    # Planning
    # ======================================================

    @property
    def next_goal(self):

        return self.goals.next

    @property
    def days_until_next_goal(self):

        if self.next_goal is None:

            return None

        return self.next_goal.days_remaining

    @property
    def active_goals(self):

        return self.goals.active

    @property
    def next_event(self):

        return self.events.next

    @property
    def days_until_next_event(self):

        if self.next_event is None:

            return None

        return self.next_event.event.days_remaining

    @property
    def upcoming_events(self):

        return self.events.upcoming

    # ======================================================
    # Summary
    # ======================================================

    def summary(self):

        return {

            "workouts": self.number_of_workouts,

            "sports": self.sports,

            "training_days": self.training_days,

            "total_distance": self.total_distance,

            "total_duration": self.total_duration,

            "total_elevation": self.total_elevation,

            "average_distance": self.average_distance,

            "average_duration": self.average_duration,

            "average_elevation": self.average_elevation,

            "average_rpe": self.average_rpe,

            "current_streak": self.current_streak,

            "longest_streak": self.longest_streak,

            "next_goal": self.next_goal,

            "days_until_next_goal": self.days_until_next_goal,

            "next_event": self.next_event,

            "days_until_next_event": self.days_until_next_event,

            "active_goals": self.active_goals,

            "upcoming_events": self.upcoming_events,

        }

    # ======================================================

    def __repr__(self):

        return (

            f"AthleteAnalytics("

            f"athlete='{self.athlete.name}')"

        )