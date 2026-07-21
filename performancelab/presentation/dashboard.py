"""
PerformanceLab

Dashboard Data

Presentation-ready data for user interfaces.
"""

from datetime import date, datetime, timedelta

from performancelab.race import entry
from performancelab.training.planning import WeeklyPlanBuilder

from .dashboard_models import (
    AthleteOverviewData,
    DashboardSummaryData,
    LatestActivityCardData,
    MonthlySportSummaryData,
    MonthlySummaryCardData,
    PerformanceChartData,
    PhysiologyCardData,
    RecoveryCardData,
    TrainingLoadCardData,
    NextEventCardData,
)
from .planning_presenter import PlanningPresenter


class DashboardData:

    # ======================================================

    def __init__(self, athlete):

        self.athlete = athlete

    # ======================================================
    # Shortcuts
    # ======================================================

    @property
    def analytics(self):

        return self.athlete.analytics

    # ======================================================
    # Helpers
    # ======================================================

    @staticmethod
    def _average_load(
        loads,
        days: int,
    ) -> float:
        """
        Returns the average of the latest daily loads.
        """

        recent_loads = list(loads)[-days:]

        if not recent_loads:

            return 0.0

        return sum(recent_loads) / len(recent_loads)


    @staticmethod
    def _nested_value(
        source,
        *paths: tuple[str, ...],
    ):
        """
        Return the first available nested attribute.
        """

        for path in paths:

            value = source

            for name in path:

                if value is None:

                    break

                value = getattr(
                    value,
                    name,
                    None,
                )

                if callable(value):

                    value = value()

            if value is not None:

                return value

        return None

    @staticmethod
    def _optional_metric(
        *sources,
        names: tuple[str, ...],
    ) -> float | None:
        """
        Returns the first available numeric metric.
        """

        for source in sources:

            if source is None:

                continue

            for name in names:

                value = getattr(
                    source,
                    name,
                    None,
                )

                if callable(value):

                    value = value()

                if value is None:

                    continue

                try:

                    return float(value)

                except (TypeError, ValueError):

                    continue

        return None


    @staticmethod
    def _workout_value(
        workout,
        *paths: tuple[str, ...],
    ):
        """
        Return the first available workout value.
        """

        for path in paths:

            value = workout

            for name in path:

                if value is None:
                    break

                value = getattr(
                    value,
                    name,
                    None,
                )

                if callable(value):
                    value = value()

            if value is not None:
                return value

        return None

    @staticmethod
    def _sport_group(
        sport,
    ) -> str:
        """
        Normalize a sport into a dashboard group.
        """

        normalized = str(
            sport or "Other"
        ).strip().lower()

        if any(
            token in normalized
            for token in (
                "run",
                "jog",
                "trail",
            )
        ):
            return "Running"

        if any(
            token in normalized
            for token in (
                "cycl",
                "bike",
                "bicycle",
            )
        ):
            return "Cycling"

        if "swim" in normalized:
            return "Swimming"

        return "Other"

    def _monthly_target_progress(
        self,
        sport: str,
        distance: float,
        duration: timedelta,
    ) -> int | None:
        """
        Calculate progress when a monthly target exists.
        """

        normalized = sport.lower()

        distance_names = {
            "running": (
                "monthly_running_distance_target",
                "running_monthly_distance_target",
            ),
            "cycling": (
                "monthly_cycling_distance_target",
                "cycling_monthly_distance_target",
            ),
            "swimming": (
                "monthly_swimming_distance_target",
                "swimming_monthly_distance_target",
            ),
        }

        target = self._optional_metric(
            self.analytics,
            self.athlete,
            names=distance_names.get(
                normalized,
                (),
            ),
        )

        current = distance

        if target is None and sport == "Other":

            target = self._optional_metric(
                self.analytics,
                self.athlete,
                names=(
                    "monthly_other_duration_target",
                    "other_monthly_duration_target",
                ),
            )

            current = duration.total_seconds() / 3600

        if target is None or target <= 0:
            return None

        return round(
            max(
                0,
                min(
                    100,
                    current / target * 100,
                ),
            )
        )

    @staticmethod
    def _training_load_status(
        acute_load: float,
        chronic_load: float,
    ) -> tuple[str, str]:
        """
        Classifies the current training load balance.
        """

        if chronic_load <= 0:

            if acute_load <= 0:

                return (
                    "No load",
                    "Add training data to calculate load balance.",
                )

            return (
                "Building",
                "Training has started, but more history is needed.",
            )

        ratio = acute_load / chronic_load

        if ratio < 0.8:

            return (
                "Detraining",
                "Current load is below the recent training baseline.",
            )

        if ratio < 1.0:

            return (
                "Maintaining",
                "Current load is close to the recent baseline.",
            )

        if ratio <= 1.3:

            return (
                "Optimal",
                "Training load is progressing within a balanced range.",
            )

        if ratio <= 1.5:

            return (
                "High load",
                "Monitor fatigue and prioritise recovery.",
            )

        return (
            "Overreaching",
            "Reduce load or add recovery before the next hard session.",
        )

    # ======================================================
    # Athlete
    # ======================================================

    @property
    def athlete_data(self):

        return AthleteOverviewData(

            name=self.athlete.name,

            sports=sorted(
                self.analytics.sports
            ),

        )


    # ======================================================
    # Latest activity
    # ======================================================

    @property
    def latest_activity(self):

        workout = self.analytics.last_workout

        if workout is None:

            return LatestActivityCardData(
                sport=None,
                title=None,
                workout_date=None,
                distance=None,
                duration=None,
                elevation_gain=None,
                average_heart_rate=None,
                maximum_heart_rate=None,
                average_power=None,
                active_calories=None,
            )

        sport = self._nested_value(
            workout,
            ("info", "sport"),
            ("sport",),
        )

        title = self._nested_value(
            workout,
            ("info", "title"),
            ("title",),
        )

        workout_date = self._nested_value(
            workout,
            ("info", "date"),
            ("date",),
            ("workout_date",),
        )

        distance = self._nested_value(
            workout,
            ("volume", "distance"),
            ("info", "distance"),
            ("distance",),
        )

        duration = self._nested_value(
            workout,
            ("volume", "duration"),
            ("info", "duration"),
            ("duration",),
        )

        elevation_gain = self._nested_value(
            workout,
            ("volume", "elevation_gain"),
            ("info", "elevation_gain"),
            ("elevation_gain",),
            ("ascent",),
            ("total_ascent",),
        )

        average_heart_rate = self._nested_value(
            workout,
            ("heart_rate", "average"),
            ("metrics", "average_heart_rate"),
            ("average_heart_rate",),
            ("avg_heart_rate",),
        )

        maximum_heart_rate = self._nested_value(
            workout,
            ("heart_rate", "maximum"),
            ("heart_rate", "max"),
            ("metrics", "maximum_heart_rate"),
            ("maximum_heart_rate",),
            ("max_heart_rate",),
            ("max_hr",),
        )

        average_power = self._nested_value(
            workout,
            ("power", "average"),
            ("metrics", "average_power"),
            ("average_power",),
            ("avg_power",),
            ("power",),
        )

        active_calories = self._nested_value(
            workout,
            ("energy", "active_calories"),
            ("metrics", "active_calories"),
            ("active_calories",),
            ("calories",),
            ("kilocalories",),
        )

        return LatestActivityCardData(
            sport=(
                str(sport)
                if sport is not None
                else None
            ),
            title=(
                str(title)
                if title is not None
                else None
            ),
            workout_date=workout_date,
            distance=(
                float(distance)
                if distance is not None
                else None
            ),
            duration=duration,
            elevation_gain=(
                float(elevation_gain)
                if elevation_gain is not None
                else None
            ),
            average_heart_rate=(
                float(average_heart_rate)
                if average_heart_rate is not None
                else None
            ),
            maximum_heart_rate=(
                float(maximum_heart_rate)
                if maximum_heart_rate is not None
                else None
            ),
            average_power=(
                float(average_power)
                if average_power is not None
                else None
            ),
            active_calories=(
                float(active_calories)
                if active_calories is not None
                else None
            ),
        )

    # ======================================================
    # Physiology
    # ======================================================

    @property
    def physiology(self):

        return PhysiologyCardData(

            vo2_max=self._optional_metric(
                self.analytics,
                self.athlete,
                names=(
                    "vo2_max",
                    "vo2max",
                    "estimated_vo2_max",
                ),
            ),

            resting_hr_30d=self._optional_metric(
                self.analytics,
                self.athlete,
                names=(
                    "resting_hr_30d",
                    "average_resting_hr_30d",
                    "monthly_resting_hr",
                    "resting_heart_rate",
                ),
            ),

            walking_hr_30d=self._optional_metric(
                self.analytics,
                self.athlete,
                names=(
                    "walking_hr_30d",
                    "average_walking_hr_30d",
                    "monthly_walking_hr",
                    "walking_heart_rate",
                ),
            ),

            hrv_30d=self._optional_metric(
                self.analytics,
                self.athlete,
                names=(
                    "hrv_30d",
                    "average_hrv_30d",
                    "monthly_hrv",
                    "hrv",
                ),
            ),

            estimated_ftp=self._optional_metric(
                self.analytics,
                self.athlete,
                names=(
                    "estimated_ftp",
                    "ftp",
                    "functional_threshold_power",
                ),
            ),

            threshold_hr=self._optional_metric(
                self.analytics,
                self.athlete,
                names=(
                    "threshold_hr",
                    "lthr",
                    "lactate_threshold_hr",
                ),
            ),

        )


    # ======================================================
    # Monthly sport summary
    # ======================================================

    @property
    def monthly_summary(self):

        today = date.today()

        start_date = today.replace(
            day=1
        )

        if today.month == 12:

            next_month = today.replace(
                year=today.year + 1,
                month=1,
                day=1,
            )

        else:

            next_month = today.replace(
                month=today.month + 1,
                day=1,
            )

        end_date = next_month - timedelta(
            days=1
        )

        grouped = {}

        for workout in self.analytics.history:

            workout_date = self._workout_value(
                workout,
                ("info", "date"),
                ("date",),
                ("workout_date",),
            )

            if workout_date is None:
                continue

            if isinstance(
                workout_date,
                datetime,
            ):
                workout_date = workout_date.date()

            if not (
                start_date
                <= workout_date
                <= end_date
            ):
                continue

            sport = self._sport_group(
                self._workout_value(
                    workout,
                    ("info", "sport"),
                    ("sport",),
                )
            )

            distance = self._workout_value(
                workout,
                ("volume", "distance"),
                ("info", "distance"),
                ("distance",),
            )

            duration = self._workout_value(
                workout,
                ("volume", "duration"),
                ("info", "duration"),
                ("duration",),
            )

            elevation = self._workout_value(
                workout,
                ("volume", "elevation_gain"),
                ("info", "elevation_gain"),
                ("elevation_gain",),
                ("ascent",),
                ("total_ascent",),
            )

            if sport not in grouped:

                grouped[sport] = {
                    "sessions": 0,
                    "distance": 0.0,
                    "duration": timedelta(),
                    "elevation_gain": 0.0,
                }

            grouped[sport]["sessions"] += 1

            if distance is not None:

                grouped[sport]["distance"] += float(
                    distance
                )

            if isinstance(
                duration,
                timedelta,
            ):

                grouped[sport]["duration"] += duration

            if elevation is not None:

                grouped[sport]["elevation_gain"] += float(
                    elevation
                )

        order = (
            "Running",
            "Cycling",
            "Swimming",
            "Other",
        )

        summaries = []

        for sport in order:

            values = grouped.get(
                sport
            )

            if values is None:
                continue

            summaries.append(
                MonthlySportSummaryData(
                    sport=sport,
                    sessions=values["sessions"],
                    distance=values["distance"],
                    duration=values["duration"],
                    elevation_gain=(
                        values["elevation_gain"]
                    ),
                    target_progress=(
                        self._monthly_target_progress(
                            sport,
                            values["distance"],
                            values["duration"],
                        )
                    ),
                )
            )

        return MonthlySummaryCardData(
            start_date=start_date,
            end_date=end_date,
            sports=tuple(summaries),
        )

    # ======================================================
    # Summary
    # ======================================================

    @property
    def summary(self):

        return DashboardSummaryData(

            workouts=self.analytics.number_of_workouts,

            sports=len(self.analytics.sports),

            training_days=self.analytics.training_days,

            total_duration=self.analytics.total_duration,

            average_rpe=self.analytics.average_rpe,

            ctl=self.analytics.ctl,

            atl=self.analytics.atl,

            tsb=self.analytics.tsb,

        )

    # ======================================================
    # Performance
    # ======================================================

    @property
    def performance(self):

        daily_loads = self.analytics.daily_loads

        pmc = self.analytics.pmc

        return PerformanceChartData(

            dates=daily_loads.dates,

            load=daily_loads.loads,

            ctl=pmc.ctl,

            atl=pmc.atl,

            tsb=pmc.tsb,

        )

    # ======================================================
    # Next Event
    # ======================================================

    @property
    def next_event(self):

        entry = self.analytics.next_event

        if entry is None:
            return None

        event = entry.event

        return NextEventCardData(

            name=event.name,
            event_date=event.date,
            days_remaining=event.days_remaining,

            sport=event.sport,
            distance=event.distance,

            location=event.location,
            country=event.country,

            priority=entry.priority,
            target_time=entry.target_time,

            elevation_gain=event.elevation_gain,
            website=event.website,
            description=event.description,
        )

    # ======================================================
    # Planning card
    # ======================================================

    @property
    def planning(self):
        """
        Builds the combined weekly plan, next workout and
        virtual coach presentation model.
        """

        from performancelab.training.planning import (
            WeeklyPlanBuilder,
        )

        plan = WeeklyPlanBuilder(
            self.analytics.training_plan,
        ).week()

        return PlanningPresenter(
            plan=plan,
            history=self.analytics.history,
        ).build()

    # ======================================================
    # Recovery
    # ======================================================

    @property
    def recovery(self):

        return RecoveryCardData(

            score=82,

            status="Good",

            recommendation=(
                "Ready for a normal training session."
            ),

            trend="↑ 4%",

        )

    # ======================================================
    # Training load
    # ======================================================

    @property
    def training_load(self):

        loads = self.analytics.daily_loads.loads

        acute_load = self._average_load(
            loads,
            7,
        )

        chronic_load = self._average_load(
            loads,
            42,
        )

        if chronic_load > 0:

            ramp_rate = (
                (acute_load - chronic_load)
                / chronic_load
                * 100
            )

            balance_score = round(
                max(
                    0,
                    min(
                        100,
                        100 - abs(ramp_rate),
                    ),
                )
            )

        else:

            ramp_rate = 0.0
            balance_score = 0

        status, recommendation = (
            self._training_load_status(
                acute_load,
                chronic_load,
            )
        )

        return TrainingLoadCardData(

            acute_load=acute_load,

            chronic_load=chronic_load,

            ramp_rate=ramp_rate,

            score=balance_score,

            status=status,

            recommendation=recommendation,

        )

    # ======================================================
    # Complete Dashboard
    # ======================================================

    def build(self):

        return {

            "athlete": self.athlete_data,

            "latest_activity": self.latest_activity,

            "physiology": self.physiology,

            "monthly_summary": self.monthly_summary,

            "next_event": self.next_event,

            "summary": self.summary,

            "performance": self.performance,

            "planning": self.planning,

            "recovery": self.recovery,

            "training_load": self.training_load,

        }

    # ======================================================

    def __repr__(self):

        return (
            f"DashboardData("
            f"athlete='{self.athlete.name}')"
        )