"""
PerformanceLab

Training Coach context presenter.
"""

from datetime import (
    date,
    datetime,
    timedelta,
)

from performancelab.training.load import (
    workout_load,
)

from .activity_coach_models import (
    ActivityCoachContextData,
    ActivityCoachRecentTrainingData,
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
        athlete=None,
    ) -> None:

        self.activity = activity
        self.workout = workout
        self.athlete = athlete

    @staticmethod
    def _calendar_day(
        value,
    ) -> date | None:

        if isinstance(
            value,
            datetime,
        ):
            return value.date()

        if isinstance(
            value,
            date,
        ):
            return value

        return None

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

    def _recent_training(
        self,
    ) -> ActivityCoachRecentTrainingData:
        """
        Summarises the seven-day window ending on the
        selected activity day.
        """

        activity_day = self._calendar_day(
            self.activity.workout_date
        )

        if (
            self.athlete is None
            or activity_day is None
        ):
            return (
                ActivityCoachRecentTrainingData()
            )

        start_day = (
            activity_day
            - timedelta(
                days=6
            )
        )

        recent_workouts = []

        for workout in self.athlete.history:

            workout_day = self._calendar_day(
                workout.date
            )

            if (
                workout_day is None
                or workout_day < start_day
                or workout_day > activity_day
            ):
                continue

            recent_workouts.append(
                workout
            )

        total_duration_minutes = sum(
            (
                workout.duration
                .total_seconds()
                / 60
            )
            for workout in recent_workouts
            if workout.duration is not None
        )

        total_load = sum(
            float(
                workout_load(
                    workout
                )
            )
            for workout in recent_workouts
        )

        previous_candidates = [
            workout
            for workout in self.athlete.history
            if (
                self._calendar_day(
                    workout.date
                )
                is not None
                and self._calendar_day(
                    workout.date
                )
                < activity_day
            )
        ]

        previous_workout = (
            max(
                previous_candidates,
                key=lambda workout: (
                    self._calendar_day(
                        workout.date
                    )
                ),
            )
            if previous_candidates
            else None
        )

        previous_title = None
        previous_days_before = None
        previous_load = None

        if previous_workout is not None:

            previous_day = (
                self._calendar_day(
                    previous_workout.date
                )
            )

            previous_title = str(
                previous_workout.info.title
                or previous_workout.sport
                or "Activity"
            )

            previous_days_before = (
                activity_day
                - previous_day
            ).days

            previous_load = float(
                workout_load(
                    previous_workout
                )
            )

        return ActivityCoachRecentTrainingData(
            session_count=len(
                recent_workouts
            ),
            total_duration_minutes=(
                float(
                    total_duration_minutes
                )
            ),
            total_load=float(
                total_load
            ),
            previous_title=previous_title,
            previous_days_before=(
                previous_days_before
            ),
            previous_load=previous_load,
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
            recent_training=(
                self._recent_training()
            ),
        )