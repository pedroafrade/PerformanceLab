"""
PerformanceLab

AthleteAnalytics

Public analytics interface for an athlete.
"""

from datetime import date, timedelta

from performancelab.analysis.performance import (
    PerformanceManagementChart,
)
from performancelab.physiology import (
    acute_chronic_ratio as calculate_acute_chronic_ratio,
)
from performancelab.training import DailyLoadBuilder

from .performance_profile import PerformanceProfile
from .training_state import TrainingState

from . import consistency
from . import time
from . import volume


class AthleteAnalytics:

    # ======================================================

    def __init__(self, athlete):

        self.athlete = athlete

        self._training_state = None

        self._performance_profile = None

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

    @property
    def days_since_last_workout(self) -> int | None:

        if self.last_training_date is None:

            return None

        from datetime import date

        return (
            date.today()
            - self.last_training_date
        ).days

    @property
    def weekly_frequency(self) -> float:

        if not self.history:

            return 0.0

        first = self.first_training_date

        last = self.last_training_date

        if (
            first is None
            or last is None
        ):

            return 0.0

        total_days = max(
            (last - first).days + 1,
            1,
        )

        total_weeks = total_days / 7

        return (
            len(self.history)
            / total_weeks
        )

    @property
    def current_training_loads(self) -> list[float]:

        today = date.today()

        start_date = today - timedelta(days=27)

        return DailyLoadBuilder(
            self.history
        ).build(
            start_date=start_date,
            end_date=today,
        ).loads

    @property
    def acute_training_load(self) -> float:

        loads = self.current_training_loads[-7:]

        return sum(loads) / 7

    @property
    def chronic_training_load(self) -> float:

        loads = self.current_training_loads

        return sum(loads) / 28

    @property
    def acute_chronic_ratio(self) -> float | None:

        return calculate_acute_chronic_ratio(
            self.acute_training_load,
            self.chronic_training_load,
        )

    @property
    def recent_training_load(self) -> float:

        return sum(
            self.current_training_loads[-7:]
        )

    @property
    def age(self) -> int | None:

        if self.athlete.birth_date is None:

            return None

        from datetime import date

        today = date.today()

        return (
            today.year
            - self.athlete.birth_date.year
            - (
                (
                    today.month,
                    today.day,
                )
                < (
                    self.athlete.birth_date.month,
                    self.athlete.birth_date.day,
                )
            )
        )

    # ======================================================
    # Consistency
    # ======================================================

    @property
    def consistency_score(self) -> float:

        workouts = len(self.history)

        if workouts == 0:

            return 0.0

        frequency = self.weekly_frequency

        return min(
            frequency / 7.0,
            1.0,
        )

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
    
    @property
    def training_plan(self):

        return self.athlete.training_plan

    @property
    def training_state(self) -> TrainingState:

        if self._training_state is None:

            self._training_state = TrainingState(

                ctl=self.ctl,

                atl=self.atl,

                tsb=self.tsb,

                acute_chronic_ratio=self.acute_chronic_ratio,

                monotony=None,

                strain=None,

                consistency=self.consistency_score,

                weekly_frequency=self.weekly_frequency,

                days_since_last_workout=self.days_since_last_workout,

                recent_training_load=self.recent_training_load,

            )

        return self._training_state

    @property
    def performance_profile(self) -> PerformanceProfile:

        if self._performance_profile is None:

            self._performance_profile = PerformanceProfile(

                age=self.age,

                gender=self.athlete.gender or None,

                height=self.athlete.height,

                weight=self.athlete.weight,

                ftp=self.athlete.ftp,

                vo2max=None,

                max_hr=self.athlete.max_hr,

                resting_hr=self.athlete.resting_hr,

                running_economy=None,

            )

        return self._performance_profile

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