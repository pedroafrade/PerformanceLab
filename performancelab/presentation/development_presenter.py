"""
PerformanceLab

Development presenter.
"""

from performancelab.athlete import Athlete

from performancelab.analysis import (
    heart_rate_zone_durations,
)

from .dashboard import DashboardData

from .development_models import (
    DevelopmentData,
    DevelopmentHeartRateZoneData,
    DevelopmentIntensityData,
    DevelopmentPaceZoneData,
    DevelopmentPerformanceReferencesData,
    DevelopmentSportVolumeData,
)

from performancelab.physiology import (
    pace_zones,
)


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

    def build(self) -> DevelopmentData:

        dashboard = DashboardData(
            self.athlete
        )

        performance = (
            dashboard.performance
        )
        summary = dashboard.summary
        recovery = dashboard.recovery
        training_load = (
            dashboard.training_load
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
                summary.ctl
            ),
            current_fatigue=(
                summary.atl
            ),
            current_form=(
                summary.tsb
            ),
            recovery_score=(
                recovery.score
            ),
            recovery_status=(
                recovery.status
            ),
            recovery_recommendation=(
                recovery.recommendation
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
            sport_volume=(
                self._sport_volume()
            ),
            intensity=(
                self._intensity_summary()
            ),
            performance_references=(
                self._performance_references()
            ),
        )