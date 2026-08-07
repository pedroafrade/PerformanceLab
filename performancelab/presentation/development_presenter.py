"""
PerformanceLab

Development presenter.
"""

from performancelab.athlete import Athlete

from .dashboard import DashboardData
from .development_models import (
    DevelopmentData,
    DevelopmentSportVolumeData,
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
        )