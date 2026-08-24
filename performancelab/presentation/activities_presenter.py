"""
PerformanceLab

Activities Presenter.

Transforms completed workouts into immutable,
presentation-ready activity summaries.
"""

from datetime import date, datetime, time

from performancelab.text import (
    repair_mojibake,
)
from performancelab.training.load import (
    workout_load,
)
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
        *,
        training_plan=None,
        reference_day: date | None = None,
    ) -> None:

        self.history = history
        self.training_plan = training_plan
        self.reference_day = (
            reference_day
            if reference_day is not None
            else date.today()
        )

    @staticmethod
    def _sortable_date(
        value: date | datetime | None,
    ) -> datetime:
        """
        Converts activity dates into comparable datetimes.
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
    def _presented_sport(
        workout,
    ) -> str:
        """
        Returns a factual presentation label for the sport.

        Running disciplines are distinguished only when the
        workout contains an explicit terrain value. Missing
        terrain remains generic Running.
        """

        sport = str(
            workout.sport
            or "Other"
        ).strip()

        if sport.casefold() != "running":
            return sport

        terrain = str(
            workout.environment.terrain
            or ""
        ).strip().casefold()

        running_disciplines = {
            "trail": "Trail Running",
            "road": "Road Running",
            "track": "Track Running",
            "indoor": "Indoor Running",
        }

        return running_disciplines.get(
            terrain,
            "Running",
        )

    def _outcomes_by_workout_id(
        self,
    ) -> dict[str, object]:
        """
        Indexes plan outcomes by completed workout ID.
        """

        if self.training_plan is None:
            return {}

        outcomes = (
            self.training_plan
            .assess_outcomes(
                history=self.history,
                reference_day=(
                    self.reference_day
                ),
            )
        )

        return {
            str(
                outcome
                .completed_workout
                .workout_id
            ): outcome
            for outcome in outcomes
            if (
                outcome.completed_workout
                is not None
            )
        }
    def _status_without_outcome(
        self,
        workout,
    ) -> str | None:
        """
        Classifies an activity without an associated
        planned workout.
        """

        if self.training_plan is None:
            return None

        workout_day = self._activity_day(
            workout.date
        )

        if workout_day is None:
            return None

        if self.training_plan.covers(
            workout_day
        ):
            return "unplanned"

        return "outside_plan"
    
    @staticmethod
    def _item_from_workout(
        workout,
        *,
        outcome=None,
        status_without_outcome: str | None = None,
    ) -> ActivityListItemData:
        """
        Builds one immutable activity list item.
        """

        effective_rpe = (
            workout.feedback.effective_rpe
        )

        outcome_status = (
            status_without_outcome
        )
        planned_title = None
        planned_load = None
        completed_load = (
            workout_load(
                workout
            )
        )
        load_difference = None

        if outcome is not None:

            outcome_status = (
                outcome.status.value
            )

            planned_title = (
                outcome
                .planned_workout
                .title
            )

            planned_load = (
                outcome.planned_load
            )

            completed_load = (
                outcome.completed_load
            )

            load_difference = (
                outcome.load_difference
            )

        return ActivityListItemData(
            workout_id=str(
                workout.workout_id
            ),
            workout_date=workout.date,
            sport=(
                ActivitiesPresenter
                ._presented_sport(
                    workout
                )
            ),
            title=repair_mojibake(
                str(
                    workout.info.title
                    or workout.sport
                    or "Activity"
                )
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
            outcome_status=outcome_status,
            planned_title=planned_title,
            planned_load=(
                float(planned_load)
                if planned_load is not None
                else None
            ),
            completed_load=(
                float(completed_load)
                if completed_load is not None
                else None
            ),
            load_difference=(
                float(load_difference)
                if load_difference is not None
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
        if (
            filters.outcome_status
            is not None
        ):

            expected_status = (
                filters
                .outcome_status
                .casefold()
            )

            if (
                activity.outcome_status
                is None
                or activity
                .outcome_status
                .casefold()
                != expected_status
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

        outcomes_by_id = (
            self._outcomes_by_workout_id()
        )

        activities = tuple(
            self._item_from_workout(
                workout,
                outcome=outcomes_by_id.get(
                    str(workout.workout_id)
                ),
                status_without_outcome=(
                    self._status_without_outcome(
                        workout
                    )
                ),
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