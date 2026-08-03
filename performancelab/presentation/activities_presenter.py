"""
PerformanceLab

Activities Presenter.

Transforms completed workouts into immutable,
presentation-ready activity summaries.
"""

from datetime import date, datetime, time

from .activity_models import (
    ActivityFilters,
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
    def _activity_day(
        value: date | datetime | None,
    ) -> date | None:
        """
        Returns the calendar day of an activity.
        """

        if isinstance(
            value,
            datetime,
        ):
            return value.date()

        return value

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

    @classmethod
    def _matches_filters(
        cls,
        activity: ActivityListItemData,
        filters: ActivityFilters,
    ) -> bool:
        """
        Checks whether an activity satisfies all filters.
        """

        query = filters.query.strip().casefold()

        if (
            query
            and query
            not in activity.title.casefold()
        ):
            return False

        if (
            filters.sport is not None
            and activity.sport.casefold()
            != filters.sport.casefold()
        ):
            return False

        activity_day = cls._activity_day(
            activity.workout_date
        )

        if filters.start_date is not None:

            if (
                activity_day is None
                or activity_day
                < filters.start_date
            ):
                return False

        if filters.end_date is not None:

            if (
                activity_day is None
                or activity_day
                > filters.end_date
            ):
                return False

        return True

    def build(
        self,
        *,
        filters: ActivityFilters | None = None,
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

        activities = tuple(
            self._item_from_workout(
                workout
            )
            for workout in workouts
        )

        if filters is None:
            return activities

        return tuple(
            activity
            for activity in activities
            if self._matches_filters(
                activity,
                filters,
            )
        )