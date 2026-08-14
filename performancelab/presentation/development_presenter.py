"""
PerformanceLab

Development presenter.
"""
from datetime import (
    date,
    datetime,
    timedelta,
)

from performancelab.athlete import Athlete

from performancelab.analysis import (
    heart_rate_zone_durations,
)

from .dashboard import DashboardData

from .development_summary_presenter import (
    DevelopmentSummaryPresenter,
)

from .development_models import (
    DevelopmentData,
    DevelopmentHeartRateZoneData,
    DevelopmentIntensityData,
    DevelopmentPaceZoneData,
    DevelopmentPerformanceReferencesData,
    DevelopmentSportVolumeData,
    DevelopmentTrendMetricData,
    DevelopmentTrendsData,
    DevelopmentVO2MaxObservationData,
)

from performancelab.physiology import (
    pace_zones,
)

from .chart import sensor_summary

class DevelopmentPresenter:
    """
    Builds the presentation data used by the
    Development page.

    The UI receives prepared domain information and
    does not calculate physiological metrics itself.
    """

    def __init__(
        self,
        athlete: Athlete,
    ) -> None:

        self.athlete = athlete

    @staticmethod
    def _workout_day(
        workout,
    ) -> date | None:
        """
        Returns the calendar day of one completed workout.
        """

        workout_day = workout.date

        if isinstance(
            workout_day,
            datetime,
        ):
            return workout_day.date()

        if isinstance(
            workout_day,
            date,
        ):
            return workout_day

        return None

    @staticmethod
    def _observation_day(
        observation,
    ) -> date | None:
        """
        Returns the calendar day of one factual VO2max
        observation.
        """

        observed_at = (
            observation.observed_at
        )

        if isinstance(
            observed_at,
            datetime,
        ):
            return observed_at.date()

        if isinstance(
            observed_at,
            date,
        ):
            return observed_at

        return None

    @staticmethod
    def _trend_metric(
        *,
        current_total: float,
        previous_total: float,
        current_samples: int,
        previous_samples: int,
        window_days: int,
    ) -> DevelopmentTrendMetricData:
        """
        Converts two window totals into comparable
        per-day values and changes.
        """

        current_value = (
            current_total
            / window_days
            if current_samples > 0
            else None
        )

        previous_value = (
            previous_total
            / window_days
            if previous_samples > 0
            else None
        )

        comparison_available = (
            current_value is not None
            and previous_value is not None
        )

        absolute_change = (
            current_value
            - previous_value
            if comparison_available
            else None
        )

        percentage_change = None

        if (
            comparison_available
            and previous_value > 0
        ):
            percentage_change = (
                (
                    current_value
                    - previous_value
                )
                / previous_value
                * 100
            )

        return DevelopmentTrendMetricData(
            current_value=current_value,
            previous_value=previous_value,
            absolute_change=absolute_change,
            percentage_change=(
                percentage_change
            ),
            improvement_percentage=(
                percentage_change
            ),
            current_samples=current_samples,
            previous_samples=previous_samples,
            window_days=window_days,
        )

    @staticmethod
    def _average_trend_metric(
        *,
        current_total: float,
        previous_total: float,
        current_samples: int,
        previous_samples: int,
        window_days: int,
    ) -> DevelopmentTrendMetricData:
        """
        Compares the mean of factual observations in two
        consecutive windows.

        Unlike exercise volume, VO2max is not divided by the
        number of calendar days.
        """

        current_value = (
            current_total
            / current_samples
            if current_samples > 0
            else None
        )

        previous_value = (
            previous_total
            / previous_samples
            if previous_samples > 0
            else None
        )

        comparison_available = (
            current_value is not None
            and previous_value is not None
        )

        absolute_change = (
            current_value
            - previous_value
            if comparison_available
            else None
        )

        percentage_change = None

        if (
            comparison_available
            and previous_value > 0
        ):
            percentage_change = (
                (
                    current_value
                    - previous_value
                )
                / previous_value
                * 100
            )

        return DevelopmentTrendMetricData(
            current_value=current_value,
            previous_value=previous_value,
            absolute_change=absolute_change,
            percentage_change=(
                percentage_change
            ),
            improvement_percentage=(
                percentage_change
            ),
            current_samples=current_samples,
            previous_samples=previous_samples,
            window_days=window_days,
        )

    @staticmethod
    def _is_running_sport(
        sport,
    ) -> bool:
        """
        Returns whether the sport represents running.
        """

        normalized_sport = str(
            sport or ""
        ).strip().lower()

        return any(
            token in normalized_sport
            for token in (
                "run",
                "running",
                "trail",
                "jog",
            )
        )

    @staticmethod
    def _running_pace_metric(
        *,
        current_minutes: float,
        current_distance: float,
        previous_minutes: float,
        previous_distance: float,
        current_samples: int,
        previous_samples: int,
        window_days: int,
    ) -> DevelopmentTrendMetricData:
        """
        Builds distance-weighted running pace comparison.

        Pace is expressed in minutes per kilometre.
        A reduction in pace value is represented as a
        positive improvement percentage.
        """

        current_value = (
            current_minutes
            / current_distance
            if (
                current_samples > 0
                and current_distance > 0
            )
            else None
        )

        previous_value = (
            previous_minutes
            / previous_distance
            if (
                previous_samples > 0
                and previous_distance > 0
            )
            else None
        )

        comparison_available = (
            current_value is not None
            and previous_value is not None
        )

        absolute_change = (
            current_value
            - previous_value
            if comparison_available
            else None
        )

        percentage_change = None
        improvement_percentage = None

        if (
            comparison_available
            and previous_value > 0
        ):
            percentage_change = (
                (
                    current_value
                    - previous_value
                )
                / previous_value
                * 100
            )

            improvement_percentage = (
                (
                    previous_value
                    - current_value
                )
                / previous_value
                * 100
            )

        return DevelopmentTrendMetricData(
            current_value=current_value,
            previous_value=previous_value,
            absolute_change=absolute_change,
            percentage_change=(
                percentage_change
            ),
            improvement_percentage=(
                improvement_percentage
            ),
            current_samples=current_samples,
            previous_samples=previous_samples,
            window_days=window_days,
        )

    @staticmethod
    def _active_calories(
        workout: object,
    ) -> float | None:

        summary = sensor_summary(
            workout,
            "active_calories",
        )

        value = summary[
            "average"
        ]

        if (
            isinstance(
                value,
                bool,
            )
            or not isinstance(
                value,
                (
                    int,
                    float,
                ),
            )
        ):
            return None

        calories = float(
            value
        )

        if calories < 0:
            return None

        return calories

    def _historical_trends(
        self,
        *,
        reference_day: date,
    ) -> DevelopmentTrendsData:
        """
        Compares the latest 28 complete calendar days
        with the immediately preceding 28 days.

        Missing duration or distance is ignored rather
        than replaced by an invented value.
        """

        window_days = 28

        current_start = (
            reference_day
            - timedelta(
                days=window_days - 1
            )
        )

        previous_end = (
            current_start
            - timedelta(days=1)
        )

        previous_start = (
            previous_end
            - timedelta(
                days=window_days - 1
            )
        )

        current_minutes = 0.0
        previous_minutes = 0.0

        current_distance = 0.0
        previous_distance = 0.0

        current_running_minutes = 0.0
        previous_running_minutes = 0.0

        current_running_distance = 0.0
        previous_running_distance = 0.0

        current_duration_samples = 0
        previous_duration_samples = 0

        current_distance_samples = 0
        previous_distance_samples = 0

        current_running_samples = 0
        previous_running_samples = 0

        current_active_calories = 0.0
        current_calorie_samples = 0

        previous_active_calories = 0.0
        previous_calorie_samples = 0

        current_vo2max = 0.0
        current_vo2max_samples = 0

        previous_vo2max = 0.0
        previous_vo2max_samples = 0

        for workout in self.athlete.history:

            workout_day = (
                self._workout_day(
                    workout
                )
            )

            if workout_day is None:
                continue

            in_current_window = (
                current_start
                <= workout_day
                <= reference_day
            )

            in_previous_window = (
                previous_start
                <= workout_day
                <= previous_end
            )

            if not (
                in_current_window
                or in_previous_window
            ):
                continue

            duration = workout.duration

            if (
                duration is not None
                and duration.total_seconds()
                >= 0
            ):
                duration_minutes = (
                    duration.total_seconds()
                    / 60
                )

                if in_current_window:
                    current_minutes += (
                        duration_minutes
                    )
                    current_duration_samples += 1
                else:
                    previous_minutes += (
                        duration_minutes
                    )
                    previous_duration_samples += 1

            distance = workout.distance

            if (
                distance is not None
                and float(distance) >= 0
            ):
                if in_current_window:
                    current_distance += float(
                        distance
                    )
                    current_distance_samples += 1
                else:
                    previous_distance += float(
                        distance
                    )
                    previous_distance_samples += 1

            is_running = (
                self._is_running_sport(
                    workout.sport
                )
            )

            valid_running_duration = (
                duration is not None
                and duration.total_seconds() > 0
            )

            valid_running_distance = (
                distance is not None
                and float(distance) > 0
            )

            if (
                is_running
                and valid_running_duration
                and valid_running_distance
            ):
                running_minutes = (
                    duration.total_seconds()
                    / 60
                )

                running_distance = float(
                    distance
                )

                if in_current_window:
                    current_running_minutes += (
                        running_minutes
                    )
                    current_running_distance += (
                        running_distance
                    )
                    current_running_samples += 1
                else:
                    previous_running_minutes += (
                        running_minutes
                    )
                    previous_running_distance += (
                        running_distance
                    )
                    previous_running_samples += 1

            active_calories = (
                self._active_calories(
                    workout
                )
            )

            if active_calories is None:
                continue

            if in_current_window:
                current_active_calories += (
                    active_calories
                )
                current_calorie_samples += 1

            else:
                previous_active_calories += (
                    active_calories
                )
                previous_calorie_samples += 1

        vo2max_observations = []

        for observation in (
            self.athlete
            .vo2max_observations
        ):

            observation_day = (
                self._observation_day(
                    observation
                )
            )

            if observation_day is None:
                continue

            vo2max_observations.append(
                DevelopmentVO2MaxObservationData(
                    observed_at=(
                        observation.observed_at
                    ),
                    value=float(
                        observation.value
                    ),
                    source=observation.source,
                    method=observation.method,
                )
            )

            if (
                current_start
                <= observation_day
                <= reference_day
            ):
                current_vo2max += float(
                    observation.value
                )
                current_vo2max_samples += 1

            elif (
                previous_start
                <= observation_day
                <= previous_end
            ):
                previous_vo2max += float(
                    observation.value
                )
                previous_vo2max_samples += 1

        return DevelopmentTrendsData(
            exercise_minutes_per_day=(
                self._trend_metric(
                    current_total=(
                        current_minutes
                    ),
                    previous_total=(
                        previous_minutes
                    ),
                    current_samples=(
                        current_duration_samples
                    ),
                    previous_samples=(
                        previous_duration_samples
                    ),
                    window_days=window_days,
                )
            ),
            exercise_distance_per_day=(
                self._trend_metric(
                    current_total=(
                        current_distance
                    ),
                    previous_total=(
                        previous_distance
                    ),
                    current_samples=(
                        current_distance_samples
                    ),
                    previous_samples=(
                        previous_distance_samples
                    ),
                    window_days=window_days,
                )
            ),
            running_pace_per_kilometre=(
                self._running_pace_metric(
                    current_minutes=(
                        current_running_minutes
                    ),
                    current_distance=(
                        current_running_distance
                    ),
                    previous_minutes=(
                        previous_running_minutes
                    ),
                    previous_distance=(
                        previous_running_distance
                    ),
                    current_samples=(
                        current_running_samples
                    ),
                    previous_samples=(
                        previous_running_samples
                    ),
                    window_days=window_days,
                )
            ),
            active_calories_per_day=(
                self._trend_metric(
                    current_total=(
                        current_active_calories
                    ),
                    previous_total=(
                        previous_active_calories
                    ),
                    current_samples=(
                        current_calorie_samples
                    ),
                    previous_samples=(
                        previous_calorie_samples
                    ),
                    window_days=window_days,
                )
            ),
            vo2max=(
                self._average_trend_metric(
                    current_total=(
                        current_vo2max
                    ),
                    previous_total=(
                        previous_vo2max
                    ),
                    current_samples=(
                        current_vo2max_samples
                    ),
                    previous_samples=(
                        previous_vo2max_samples
                    ),
                    window_days=window_days,
                )
            ),
            vo2max_observations=tuple(
                vo2max_observations
            ),
        )

    def _sport_volume(
        self,
    ) -> tuple[
        DevelopmentSportVolumeData,
        ...,
    ]:
        """
        Aggregates completed volume by sport.
        """

        totals = {}

        for workout in self.athlete.history:

            sport = str(
                workout.sport
                or "Other"
            )

            if sport not in totals:

                totals[sport] = {
                    "duration_seconds": 0.0,
                    "distance": 0.0,
                    "sessions": 0,
                }

            totals[sport][
                "sessions"
            ] += 1

            if workout.duration is not None:

                totals[sport][
                    "duration_seconds"
                ] += (
                    workout.duration
                    .total_seconds()
                )

            if workout.distance is not None:

                totals[sport][
                    "distance"
                ] += float(
                    workout.distance
                )

        rows = [
            DevelopmentSportVolumeData(
                sport=sport,
                duration_seconds=(
                    values[
                        "duration_seconds"
                    ]
                ),
                distance=(
                    values[
                        "distance"
                    ]
                ),
                sessions=(
                    values[
                        "sessions"
                    ]
                ),
            )
            for sport, values
            in totals.items()
        ]

        rows.sort(
            key=lambda row: (
                row.duration_seconds,
                row.distance,
            ),
            reverse=True,
        )

        return tuple(
            rows
        )

    def _intensity_summary(
        self,
    ) -> DevelopmentIntensityData:
        """
        Aggregates heart-rate zone time and RPE
        across completed activity history.
        """

        profile = (
            self.athlete
            .analytics
            .heart_rate_profile
        )

        rpe_values = [
            float(
                workout.feedback
                .effective_rpe
            )
            for workout in self.athlete.history
            if (
                workout.feedback
                .effective_rpe
                is not None
            )
        ]

        if profile is None:

            return (
                DevelopmentIntensityData(
                    zones=(),
                    zone_source=None,
                    heart_rate_seconds=0.0,
                    average_rpe=(
                        (
                            sum(rpe_values)
                            / len(rpe_values)
                        )
                        if rpe_values
                        else None
                    ),
                    sessions_with_rpe=(
                        len(rpe_values)
                    ),
                    high_rpe_sessions=sum(
                        1
                        for value
                        in rpe_values
                        if value > 8
                    ),
                )
            )

        totals = {
            zone.name: 0.0
            for zone in profile.zones
        }

        for workout in self.athlete.history:

            workout_totals = (
                heart_rate_zone_durations(
                    workout,
                    profile,
                )
            )

            for (
                zone_name,
                seconds,
            ) in workout_totals.items():

                totals[
                    zone_name
                ] = (
                    totals.get(
                        zone_name,
                        0.0,
                    )
                    + seconds
                )

        total_seconds = sum(
            totals.values()
        )

        zones = tuple(
            DevelopmentHeartRateZoneData(
                name=zone.name,
                lower_bpm=(
                    zone.lower_bpm
                ),
                upper_bpm=(
                    zone.upper_bpm
                ),
                duration_seconds=(
                    totals.get(
                        zone.name,
                        0.0,
                    )
                ),
                percentage=(
                    (
                        totals.get(
                            zone.name,
                            0.0,
                        )
                        / total_seconds
                        * 100
                    )
                    if total_seconds > 0
                    else 0.0
                ),
            )
            for zone in profile.zones
        )

        return (
            DevelopmentIntensityData(
                zones=zones,
                zone_source=(
                    profile.source
                ),
                heart_rate_seconds=(
                    total_seconds
                ),
                average_rpe=(
                    (
                        sum(rpe_values)
                        / len(rpe_values)
                    )
                    if rpe_values
                    else None
                ),
                sessions_with_rpe=(
                    len(rpe_values)
                ),
                high_rpe_sessions=sum(
                    1
                    for value in rpe_values
                    if value > 8
                ),
            )
        )

    def _performance_references(
        self,
    ) -> DevelopmentPerformanceReferencesData:
        """
        Builds pace zones and physiological
        performance references.
        """

        analytics = (
            self.athlete.analytics
        )

        profile = (
            analytics.performance_profile
        )

        threshold_pace = (
            profile.threshold_pace
        )

        zone_map = (
            pace_zones(
                threshold_pace
            )
            if threshold_pace is not None
            else None
        )

        pace_zone_rows = []

        if zone_map is not None:

            for (
                zone_name,
                limits,
            ) in zone_map.items():

                faster_pace = min(
                    limits
                )

                slower_pace = max(
                    limits
                )

                pace_zone_rows.append(
                    DevelopmentPaceZoneData(
                        name=zone_name,
                        faster_pace=(
                            faster_pace
                        ),
                        slower_pace=(
                            slower_pace
                        ),
                    )
                )

        return (
            DevelopmentPerformanceReferencesData(
                pace_zones=tuple(
                    pace_zone_rows
                ),
                easy_pace=(
                    analytics
                    .typical_easy_running_pace
                ),
                tempo_pace=(
                    profile.tempo_pace
                ),
                lt2_pace=(
                    profile.threshold_pace
                ),
                threshold_hr=(
                    profile.threshold_hr
                ),
                ftp=(
                    profile.ftp
                ),
            )
        )

    def build(
        self,
        *,
        reference_time: (
            datetime | None
        ) = None,
    ) -> DevelopmentData:

        dashboard = DashboardData(
            self.athlete
        )

        performance = (
            dashboard.performance
        )

        training_load = (
            dashboard.training_load
        )

        training_state = (
            self.athlete.analytics
            .training_state_at(
                reference_time=(
                    reference_time
                )
            )
            if reference_time
            is not None
            else self.athlete.analytics
            .training_state
        )

        reference_day = (
            reference_time.date()
            if reference_time is not None
            else date.today()
        )

        historical_trends = (
            self._historical_trends(
                reference_day=reference_day
            )
        )

        summary_cards = (
            DevelopmentSummaryPresenter(
                historical_trends
            ).build()
        )
        return DevelopmentData(
            dates=tuple(
                performance.dates
            ),
            daily_load=tuple(
                performance.load
            ),
            fitness=tuple(
                performance.ctl
            ),
            fatigue=tuple(
                performance.atl
            ),
            form=tuple(
                performance.tsb
            ),
            current_fitness=(
                training_state.ctl
            ),
            current_fatigue=(
                training_state.atl
            ),
            current_form=(
                training_state.tsb
            ),
            recovery_score=(
                training_state
                .recovery_score
            ),
            recovery_balance=(
                training_state
                .recovery_balance
            ),
            recovery_status=(
                training_state
                .recovery_status
            ),
            recovery_recommendation=(
                training_state
                .recovery_recommendation
            ),
            acute_load=(
                training_load.acute_load
            ),
            chronic_load=(
                training_load.chronic_load
            ),
            ramp_rate=(
                training_load.ramp_rate
            ),
            load_status=(
                training_load.status
            ),
            load_recommendation=(
                training_load.recommendation
            ),
            historical_trends=(
                historical_trends
            ),
            summary_cards=(
                summary_cards
            ),
            sport_volume=(
                self._sport_volume()
            ),
            intensity=(
                self._intensity_summary()
            ),
            performance_references=(
                self._performance_references()
            ),
            recovery_reference_time=(
                training_state.reference_time
            ),
            hours_since_last_workout=(
                training_state
                .hours_since_last_workout
            ),
            recovery_is_time_aware=(
                training_state
                .recovery_is_time_aware
            ),
        )