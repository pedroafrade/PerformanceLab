"""
PerformanceLab

AthleteAnalytics

Public analytics interface for an athlete.
"""

from datetime import date, datetime, timedelta

from statistics import pstdev

from performancelab.analysis.performance import (
    PerformanceManagementChart,
)
from performancelab.physiology import (
    acute_chronic_ratio as calculate_acute_chronic_ratio,
    monotony as calculate_training_monotony,
    strain as calculate_training_strain,
)
from performancelab.training import DailyLoadBuilder

from .performance_profile import PerformanceProfile
from .heart_rate_profile import (
    HeartRateProfile,
    build_heart_rate_profile,
)
from .training_state import TrainingState

from . import consistency
from . import time
from . import volume

ROAD_10K_LOOKBACK_DAYS = 365
ROAD_10K_MIN_DISTANCE = 8.0
ROAD_10K_MAX_DISTANCE = 12.0
ROAD_10K_MIN_RPE = 7.5
ROAD_10K_MIN_HEART_RATE_RATIO = 0.85
ROAD_10K_MAX_ELEVATION_PER_KILOMETRE = 25.0
EFFORT_ELEVATION_METRES_PER_KILOMETRE = 100.0

class AthleteAnalytics:

    # ======================================================

    def __init__(self, athlete):

        self.athlete = athlete

        self._training_state = None

        self._performance_profile = None

        self._heart_rate_profile = None

    def invalidate_training_state(
        self,
    ) -> None:
        """
        Discards the cached state after training history changes.
        """

        self._training_state = None

    # ======================================================

    def invalidate_performance_profile(
        self,
    ) -> None:
        """
        Discards cached physiological profile data after
        the athlete's settings change.
        """

        self._heart_rate_profile = None
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

            workout.feedback.effective_rpe

            for workout in self.history

            if (
                workout.feedback.effective_rpe
                is not None
            )

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
    def typical_weekly_minutes(self) -> float:
        """
        Returns the average weekly training duration
        across the latest rolling 28 days.
        """

        today = date.today()
        start_date = today - timedelta(
            days=27
        )

        total_minutes = 0.0

        for workout in self.history:

            workout_day = workout.date

            if isinstance(
                workout_day,
                datetime,
            ):
                workout_day = workout_day.date()

            if (
                workout_day is None
                or workout_day < start_date
                or workout_day > today
                or workout.duration is None
            ):
                continue

            total_minutes += (
                workout.duration.total_seconds()
                / 60
            )

        return total_minutes / 4

    @property
    def typical_weekly_sessions(self) -> float:
        """
        Returns the average number of weekly sessions
        across the latest rolling 28 days.
        """

        today = date.today()
        start_date = today - timedelta(
            days=27
        )

        session_count = 0

        for workout in self.history:

            workout_day = workout.date

            if isinstance(
                workout_day,
                datetime,
            ):
                workout_day = workout_day.date()

            if (
                workout_day is None
                or workout_day < start_date
                or workout_day > today
            ):
                continue

            session_count += 1

        return session_count / 4

    # ======================================================
    
    @staticmethod
    def _heart_rate_values(
        workout,
    ) -> tuple[float, ...]:
        """
        Returns valid heart-rate samples recorded during
        a workout.
        """

        heart_rate = workout.sensors.get(
            "heart_rate"
        )

        if not isinstance(
            heart_rate,
            (list, tuple),
        ):
            return ()

        values = []

        for sample in heart_rate:

            value = (
                sample.get("value")
                if isinstance(sample, dict)
                else sample
            )

            if (
                isinstance(
                    value,
                    (int, float),
                )
                and not isinstance(value, bool)
                and value > 0
            ):
                values.append(
                    float(value)
                )

        return tuple(values)

    # ======================================================

    @property
    def observed_max_heart_rate(
        self,
    ) -> float | None:
        """
        Returns the highest configured or observed
        heart rate.
        """

        candidates = []

        configured_max = getattr(
            self.athlete,
            "max_hr",
            None,
        )

        if (
            isinstance(
                configured_max,
                (int, float),
            )
            and configured_max > 0
        ):
            candidates.append(
                float(configured_max)
            )

        for workout in self.history:

            values = self._heart_rate_values(
                workout
            )

            if values:
                candidates.append(
                    max(values)
                )

        if not candidates:
            return None

        return max(candidates)

    # ======================================================

    @property
    def typical_running_pace(
        self,
    ) -> float | None:
        """
        Returns the distance-weighted average running pace
        across the latest rolling 28 days.

        Pace is expressed in minutes per kilometre.
        Cycling, walking and workouts without valid distance
        or duration are ignored.
        """

        today = date.today()
        start_date = today - timedelta(
            days=27
        )

        total_distance = 0.0
        total_minutes = 0.0

        for workout in self.history:

            workout_day = workout.date

            if isinstance(
                workout_day,
                datetime,
            ):
                workout_day = (
                    workout_day.date()
                )

            normalized_sport = str(
                workout.sport or ""
            ).strip().lower()

            is_running = any(
                token in normalized_sport
                for token in (
                    "run",
                    "running",
                    "trail",
                    "jog",
                )
            )

            if (
                not is_running
                or workout_day is None
                or workout_day < start_date
                or workout_day > today
                or workout.distance is None
                or workout.distance <= 0
                or workout.duration is None
                or workout.duration.total_seconds()
                <= 0
            ):
                continue

            total_distance += (
                workout.distance
            )

            total_minutes += (
                workout.duration.total_seconds()
                / 60
            )

        if total_distance <= 0:
            return None

        return (
            total_minutes
            / total_distance
        )

    # ======================================================
    @property
    def road_10k_performance_pace(
        self,
    ) -> float | None:
        """
        Returns the best effort-adjusted pace from recent,
        physiologically demanding road-running workouts
        comparable to a 10 km event.

        Pace is expressed in minutes per effort kilometre.
        """

        maximum_heart_rate = (
            self.observed_max_heart_rate
        )

        if maximum_heart_rate is None:
            return None

        today = date.today()

        start_date = (
            today
            - timedelta(
                days=(
                    ROAD_10K_LOOKBACK_DAYS
                    - 1
                )
            )
        )

        minimum_average_heart_rate = (
            maximum_heart_rate
            * ROAD_10K_MIN_HEART_RATE_RATIO
        )

        candidate_paces = []

        for workout in self.history:

            workout_day = workout.date

            if isinstance(
                workout_day,
                datetime,
            ):
                workout_day = (
                    workout_day.date()
                )

            sport = str(
                workout.sport or ""
            ).strip().lower()

            title = str(
                workout.info.title or ""
            ).strip().lower()

            excluded_text = (
                f"{sport} {title}"
            )

            distance = workout.distance
            duration = workout.duration

            if (
                "run" not in sport
                or any(
                    token in excluded_text
                    for token in (
                        "trail",
                        "hill",
                        "sky",
                    )
                )
                or workout_day is None
                or workout_day < start_date
                or workout_day > today
                or distance is None
                or not (
                    ROAD_10K_MIN_DISTANCE
                    <= distance
                    <= ROAD_10K_MAX_DISTANCE
                )
                or duration is None
                or duration.total_seconds() <= 0
            ):
                continue

            elevation_gain = max(
                workout.elevation_gain or 0.0,
                0.0,
            )

            elevation_per_kilometre = (
                elevation_gain / distance
            )

            if (
                elevation_per_kilometre
                >= ROAD_10K_MAX_ELEVATION_PER_KILOMETRE
            ):
                continue

            rpe = (
                workout.feedback.effective_rpe
            )

            if (
                rpe is None
                or rpe < ROAD_10K_MIN_RPE
            ):
                continue

            heart_rate_values = (
                self._heart_rate_values(
                    workout
                )
            )

            if not heart_rate_values:
                continue

            average_heart_rate = (
                sum(heart_rate_values)
                / len(heart_rate_values)
            )

            if (
                average_heart_rate
                < minimum_average_heart_rate
            ):
                continue

            effort_distance = (
                distance
                + (
                    elevation_gain
                    / EFFORT_ELEVATION_METRES_PER_KILOMETRE
                )
            )

            duration_minutes = (
                duration.total_seconds()
                / 60
            )

            candidate_paces.append(
                duration_minutes
                / effort_distance
            )

        if not candidate_paces:
            return None

        return min(candidate_paces)

    # ======================================================
    
    @property
    def typical_running_long_session_minutes(
        self,
    ) -> float:
        """
        Returns the average longest running session from
        each active week within the latest rolling 28 days.

        Cycling and other sports do not define running
        long-session capacity.
        """

        today = date.today()
        start_date = today - timedelta(
            days=27
        )

        weekly_longest = [
            0.0,
            0.0,
            0.0,
            0.0,
        ]

        for workout in self.history:

            workout_day = workout.date

            if isinstance(
                workout_day,
                datetime,
            ):
                workout_day = workout_day.date()

            normalized_sport = str(
                workout.sport or ""
            ).strip().lower()

            is_running = any(
                token in normalized_sport
                for token in (
                    "run",
                    "running",
                    "trail",
                    "jog",
                )
            )

            if (
                not is_running
                or workout_day is None
                or workout_day < start_date
                or workout_day > today
                or workout.duration is None
            ):
                continue

            days_ago = (
                today - workout_day
            ).days

            week_index = min(
                days_ago // 7,
                3,
            )

            duration_minutes = (
                workout.duration.total_seconds()
                / 60
            )

            weekly_longest[week_index] = max(
                weekly_longest[week_index],
                duration_minutes,
            )

        active_weeks = [
            duration
            for duration in weekly_longest
            if duration > 0
        ]

        if not active_weeks:
            return 0.0

        return (
            sum(active_weeks)
            / len(active_weeks)
        )

    @property
    def typical_running_long_session_elevation_gain(
        self,
    ) -> float:
        """
        Returns the average elevation gain of the longest
        running session from each active week within the
        latest rolling 28 days.
        """

        today = date.today()
        start_date = today - timedelta(
            days=27
        )

        weekly_longest = [
            (0.0, 0.0),
            (0.0, 0.0),
            (0.0, 0.0),
            (0.0, 0.0),
        ]

        for workout in self.history:

            workout_day = workout.date

            if isinstance(
                workout_day,
                datetime,
            ):
                workout_day = (
                    workout_day.date()
                )

            normalized_sport = str(
                workout.sport or ""
            ).strip().lower()

            is_running = any(
                token in normalized_sport
                for token in (
                    "run",
                    "running",
                    "trail",
                    "jog",
                )
            )

            if (
                not is_running
                or workout_day is None
                or workout_day < start_date
                or workout_day > today
                or workout.duration is None
            ):
                continue

            days_ago = (
                today - workout_day
            ).days

            week_index = min(
                days_ago // 7,
                3,
            )

            duration_minutes = (
                workout.duration.total_seconds()
                / 60
            )

            previous_duration, _ = (
                weekly_longest[
                    week_index
                ]
            )

            if (
                duration_minutes
                <= previous_duration
            ):
                continue

            elevation_gain = max(
                workout.elevation_gain
                or 0.0,
                0.0,
            )

            weekly_longest[
                week_index
            ] = (
                duration_minutes,
                elevation_gain,
            )

        active_elevations = [
            elevation_gain
            for (
                duration_minutes,
                elevation_gain,
            ) in weekly_longest
            if duration_minutes > 0
        ]

        if not active_elevations:
            return 0.0

        return (
            sum(active_elevations)
            / len(active_elevations)
        )

    @property
    def typical_running_long_session_effort_pace(
        self,
    ) -> float:
        """
        Returns the average effort pace of the longest
        running session from each active week within the
        latest rolling 28 days.

        Effort pace is expressed in minutes per
        effort kilometre.
        """

        today = date.today()
        start_date = today - timedelta(
            days=27
        )

        weekly_longest = [
            (0.0, 0.0),
            (0.0, 0.0),
            (0.0, 0.0),
            (0.0, 0.0),
        ]

        for workout in self.history:

            workout_day = workout.date

            if isinstance(
                workout_day,
                datetime,
            ):
                workout_day = (
                    workout_day.date()
                )

            normalized_sport = str(
                workout.sport or ""
            ).strip().lower()

            is_running = any(
                token in normalized_sport
                for token in (
                    "run",
                    "running",
                    "trail",
                    "jog",
                )
            )

            if (
                not is_running
                or workout_day is None
                or workout_day < start_date
                or workout_day > today
                or workout.duration is None
                or workout.distance is None
                or workout.distance <= 0
            ):
                continue

            duration_minutes = (
                workout.duration.total_seconds()
                / 60
            )

            if duration_minutes <= 0:
                continue

            days_ago = (
                today - workout_day
            ).days

            week_index = min(
                days_ago // 7,
                3,
            )

            previous_duration, _ = (
                weekly_longest[
                    week_index
                ]
            )

            if (
                duration_minutes
                <= previous_duration
            ):
                continue

            elevation_gain = max(
                workout.elevation_gain
                or 0.0,
                0.0,
            )

            effort_distance = (
                workout.distance
                + (
                    elevation_gain
                    / EFFORT_ELEVATION_METRES_PER_KILOMETRE
                )
            )

            if effort_distance <= 0:
                continue

            effort_pace = (
                duration_minutes
                / effort_distance
            )

            weekly_longest[
                week_index
            ] = (
                duration_minutes,
                effort_pace,
            )

        active_paces = [
            effort_pace
            for (
                duration_minutes,
                effort_pace,
            ) in weekly_longest
            if duration_minutes > 0
        ]

        if not active_paces:
            return 0.0

        return (
            sum(active_paces)
            / len(active_paces)
        )

    @property
    def training_monotony(self) -> float | None:

        loads = self.current_training_loads[-7:]

        return calculate_training_monotony(
            self.acute_training_load,
            pstdev(loads),
        )

    @property
    def training_strain(self) -> float | None:

        return calculate_training_strain(
            self.recent_training_load,
            self.training_monotony,
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

    def estimated_event_duration(
        self,
        event,
    ) -> timedelta | None:
        """
        Estimates a running event's duration from the
        athlete's recent running performance.

        Road events comparable to 10 km use the athlete's
        high-effort road-running pace when available.
        Other events retain the recent typical running pace.
        """

        estimator = getattr(
            event,
            "estimated_duration_at_pace",
            None,
        )

        if not callable(estimator):
            return None

        sport = str(
            getattr(
                event,
                "sport",
                "",
            )
            or ""
        ).strip().lower()

        distance = getattr(
            event,
            "distance",
            None,
        )

        is_road_10k_event = (
            sport == "road running"
            and isinstance(
                distance,
                (int, float),
            )
            and not isinstance(
                distance,
                bool,
            )
            and 8 <= distance <= 12
        )

        performance_pace = None

        if is_road_10k_event:
            performance_pace = (
                self.road_10k_performance_pace
            )

        reference_pace = (
            performance_pace
            if performance_pace is not None
            else self.typical_running_pace
        )

        return estimator(
            reference_pace
        )

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

                monotony=self.training_monotony,

                strain=self.training_strain,

                consistency=self.consistency_score,

                weekly_frequency=self.weekly_frequency,

                days_since_last_workout=self.days_since_last_workout,

                recent_training_load=self.recent_training_load,

                typical_weekly_minutes=self.typical_weekly_minutes,

                typical_weekly_sessions=self.typical_weekly_sessions,

                typical_running_long_session_minutes=(
                    self.typical_running_long_session_minutes
                ),
                typical_running_long_session_elevation_gain=(
                    self
                    .typical_running_long_session_elevation_gain
                ),
                typical_running_long_session_effort_pace=(
                    self
                    .typical_running_long_session_effort_pace
                ),
            )

        return self._training_state

    @property
    def heart_rate_profile(
        self,
    ) -> HeartRateProfile | None:
        """
        Returns the athlete's heart-rate profile.

        Manually configured zones take precedence over
        automatically calculated Karvonen zones.
        """

        if self._heart_rate_profile is None:

            self._heart_rate_profile = (
                build_heart_rate_profile(

                    max_hr=self.athlete.max_hr,

                    resting_hr=(
                        self.athlete.resting_hr
                    ),

                    threshold_hr=(
                        self.athlete.threshold_hr
                    ),

                    manual_zones=(
                        self.athlete
                        .manual_heart_rate_zones
                    ),

                )
            )

        return self._heart_rate_profile

    # ======================================================

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

                threshold_power=(
                    self.athlete.ftp
                ),

                threshold_hr=(
                    self.athlete.threshold_hr
                ),

                threshold_pace=None,

                max_hr=self.athlete.max_hr,

                resting_hr=self.athlete.resting_hr,

                running_economy=None,

                heart_rate_profile=(
                    self.heart_rate_profile
                ),

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