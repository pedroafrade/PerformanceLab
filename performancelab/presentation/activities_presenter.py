"""
PerformanceLab

Activities Presenter.

Transforms completed workouts into immutable,
presentation-ready activity summaries.
"""

from datetime import date, datetime, time

from .activity_models import (
    ActivityListItemData,
)


class ActivitiesPresenter:
    """
    Builds presentation data for the Activities page.
    """

    def __init__(
        self,
        history,
    ) -> None:

        self.history = history

    @staticmethod
    def _sortable_date(
        value: date | datetime | None,
    ) -> datetime:
        """
        Converts activity dates into comparable datetimes.

        Activities without a date are placed after dated
        activities.
        """

        if value is None:
            return datetime.min

        if isinstance(
            value,
            datetime,
        ):
            return value.replace(
                tzinfo=None
            )

        return datetime.combine(
            value,
            time.min,
        )

    @staticmethod
    def _item_from_workout(
        workout,
    ) -> ActivityListItemData:
        """
        Builds one immutable activity list item.
        """

        effective_rpe = (
            workout.feedback.effective_rpe
        )

        return ActivityListItemData(
            workout_id=str(
                workout.workout_id
            ),
            workout_date=workout.date,
            sport=str(
                workout.sport
                or "Other"
            ),
            title=str(
                workout.info.title
                or workout.sport
                or "Activity"
            ),
            distance=(
                float(workout.distance)
                if workout.distance is not None
                else None
            ),
            duration=workout.duration,
            elevation_gain=(
                float(workout.elevation_gain)
                if workout.elevation_gain
                is not None
                else None
            ),
            rpe=(
                float(effective_rpe)
                if effective_rpe is not None
                else None
            ),
        )

    def build(
        self,
    ) -> tuple[ActivityListItemData, ...]:
        """
        Returns completed activities from newest to oldest.
        """

        workouts = sorted(
            self.history,
            key=lambda workout: (
                self._sortable_date(
                    workout.date
                )
            ),
            reverse=True,
        )

        return tuple(
            self._item_from_workout(
                workout
            )
            for workout in workouts
        )