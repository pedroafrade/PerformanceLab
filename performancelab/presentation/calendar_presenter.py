"""
PerformanceLab

Monthly training calendar presenter.
"""

from calendar import Calendar
from datetime import date, datetime

from performancelab.text import (
    repair_mojibake,
)

from .calendar_models import (
    CalendarDayData,
    CalendarItemData,
    CalendarMonthData,
)


class CalendarPresenter:
    """
    Combines plan, history and events into a monthly calendar.
    """

    def __init__(
        self,
        *,
        history,
        training_plan,
        events,
    ) -> None:

        self.history = history
        self.training_plan = training_plan
        self.events = events

    @staticmethod
    def _calendar_day(
        value,
    ) -> date | None:
        """
        Converts dates and datetimes into calendar days.
        """

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

    def _outcome_indexes(
        self,
        *,
        reference_day: date,
    ) -> tuple[
        dict[object, str],
        dict[str, str],
    ]:
        """
        Indexes outcome status by planned and completed workout.
        """

        outcomes = (
            self.training_plan
            .assess_outcomes(
                history=self.history,
                reference_day=reference_day,
            )
        )

        planned_statuses = {
            outcome.planned_workout: (
                outcome.status.value
            )
            for outcome in outcomes
        }

        completed_statuses = {
            str(
                outcome
                .completed_workout
                .workout_id
            ): outcome.status.value
            for outcome in outcomes
            if (
                outcome.completed_workout
                is not None
            )
        }

        return (
            planned_statuses,
            completed_statuses,
        )

    @staticmethod
    def _event_status(
        entry,
    ) -> str:
        """
        Returns the current status of an event entry.
        """

        if entry.dns:
            return "dns"

        if entry.dnf:
            return "dnf"

        if entry.finished:
            return "finished"

        return "pending"

    def build(
        self,
        *,
        year: int,
        month: int,
        reference_day: date,
    ) -> CalendarMonthData:
        """
        Builds one Monday-first calendar month.
        """

        if not 1 <= month <= 12:
            raise ValueError(
                "month must be between 1 and 12."
            )

        (
            planned_statuses,
            completed_statuses,
        ) = self._outcome_indexes(
            reference_day=reference_day
        )

        planned_by_day = {}

        for workout in self.training_plan:

            planned_by_day.setdefault(
                workout.day,
                [],
            ).append(
                CalendarItemData(
                    kind="planned",
                    title=(
                        workout.title
                        or "Planned workout"
                    ),
                    sport=workout.sport,
                    status=(
                        planned_statuses.get(
                            workout
                        )
                    ),
                    duration=workout.duration,
                )
            )

        completed_by_day = {}

        for workout in self.history:

            workout_day = self._calendar_day(
                workout.date
            )

            if workout_day is None:
                continue

            completed_by_day.setdefault(
                workout_day,
                [],
            ).append(
                CalendarItemData(
                    kind="completed",
                    title=repair_mojibake(
                        str(
                            workout.info.title
                            or workout.sport
                            or "Activity"
                        )
                    ),
                    sport=workout.sport,
                    entity_id=str(
                        workout.workout_id
                    ),
                    status=(
                        completed_statuses.get(
                            str(workout.workout_id),
                            "completed",
                        )
                    ),
                    duration=workout.duration,
                )
            )

        events_by_day = {}

        for entry in self.events:

            event = entry.event
            event_day = self._calendar_day(
                event.date
            )

            if event_day is None:
                continue

            events_by_day.setdefault(
                event_day,
                [],
            ).append(
                CalendarItemData(
                    kind="event",
                    title=repair_mojibake(
                        str(
                            event.name
                            or "Event"
                        )
                    ),
                    sport=event.sport or None,
                    entity_id=str(
                        event.event_id
                    ),
                    status=(
                        self._event_status(
                            entry
                        )
                    ),
                    priority=(
                        entry.priority
                        or None
                    ),
                )
            )

        calendar = Calendar(
            firstweekday=0
        )

        calendar_weeks = (
            calendar.monthdatescalendar(
                year,
                month,
            )
        )

        weeks = tuple(
            tuple(
                CalendarDayData(
                    day=day,
                    is_current_month=(
                        day.month == month
                    ),
                    is_today=(
                        day == reference_day
                    ),
                    phase=(
                        self.training_plan.phase_on(
                            day
                        )
                    ),
                    items=tuple(
                        [
                            *events_by_day.get(
                                day,
                                (),
                            ),
                            *completed_by_day.get(
                                day,
                                (),
                            ),
                            *planned_by_day.get(
                                day,
                                (),
                            ),
                        ]
                    ),
                )
                for day in week
            )
            for week in calendar_weeks
        )

        return CalendarMonthData(
            year=year,
            month=month,
            weeks=weeks,
        )