"""
PerformanceLab

Development presenter.
"""

from performancelab.athlete import Athlete

from .dashboard import DashboardData
from .development_models import (
    DevelopmentData,
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
        )