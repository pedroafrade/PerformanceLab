"""
PerformanceLab

Training Coach context presenter.
"""

from .activity_coach_models import (
    ActivityCoachContextData,
    ActivityCoachSensorData,
)
from .activity_models import (
    ActivityListItemData,
)
from .chart import (
    sensor_summary,
)


class ActivityCoachPresenter:
    """
    Builds immutable factual context for one activity.
    """

    def __init__(
        self,
        *,
        activity: ActivityListItemData,
        workout,
    ) -> None:

        self.activity = activity
        self.workout = workout

    def _sensor_data(
        self,
        sensor_name: str,
    ) -> ActivityCoachSensorData:

        summary = sensor_summary(
            self.workout,
            sensor_name,
        )

        average = summary[
            "average"
        ]
        maximum = summary[
            "maximum"
        ]

        return ActivityCoachSensorData(
            average=(
                float(average)
                if average is not None
                else None
            ),
            maximum=(
                float(maximum)
                if maximum is not None
                else None
            ),
        )

    def build(
        self,
    ) -> ActivityCoachContextData:
        """
        Returns measured and calculated activity facts.
        """

        environment = (
            self.workout.environment
        )

        terrain = str(
            environment.terrain
            or ""
        ).strip()

        return ActivityCoachContextData(
            activity=self.activity,
            heart_rate=self._sensor_data(
                "heart_rate"
            ),
            power=self._sensor_data(
                "power"
            ),
            cadence=self._sensor_data(
                "cadence"
            ),
            temperature=(
                float(
                    environment.temperature
                )
                if environment.temperature
                is not None
                else None
            ),
            humidity=(
                float(
                    environment.humidity
                )
                if environment.humidity
                is not None
                else None
            ),
            terrain=(
                terrain
                if terrain
                else None
            ),
        )