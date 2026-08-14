"""
PerformanceLab

Monthly training calendar presenter.
"""

from calendar import Calendar, monthrange
from datetime import date, datetime, timedelta

from performancelab.text import (
    repair_mojibake,
)

from .calendar_models import (
    CalendarDayData,
    CalendarItemData,
    CalendarMonthData,
    CalendarUpcomingEventData,
)


class CalendarPresenter:
    """
    Combines plan, history and events into a monthly
    calendar.
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

    @staticmethod
    def _duration_label(
        duration: timedelta | None,
    ) -> str | None:
        """
        Formats a factual duration without changing it.
        """

        if duration is None:
            return None

        total_minutes = round(
            duration.total_seconds()
            / 60
        )

        hours, minutes = divmod(
            total_minutes,
            60,
        )

        if hours and minutes:
            return (
                f"{hours}h{minutes:02d}"
            )

        if hours:
            return f"{hours}h"

        return f"{minutes} min"

    @staticmethod
    def _distance_label(
        distance: float | None,
    ) -> str | None:
        """
        Formats a factual distance with at most two
        decimal places.
        """

        if distance is None:
            return None

        formatted = (
            f"{distance:.2f}"
            .rstrip("0")
            .rstrip(".")
        )

        return f"{formatted} km"
    
    @staticmethod
    def _elevation_label(
        elevation_gain: float | None,
    ) -> str | None:
        """
        Formats factual elevation gain.
        """

        if elevation_gain is None:
            return None

        formatted = (
            f"{elevation_gain:.0f}"
        )

        return f"+{formatted} m"
    
    @staticmethod
    def _execution_target(
        workout,
    ) -> str | None:
        """
        Selects the most useful available execution target.
        """

        for step in getattr(
            workout,
            "structure",
            (),
        ):
            value = str(
                step
                or ""
            ).strip()

            if not value:
                continue

            lowered = value.lower()

            if lowered.startswith(
                "heart rate target:"
            ):
                return value.split(
                    ":",
                    1,
                )[1].strip()

        prescription = str(
            getattr(
                workout,
                "prescription_summary",
                "",
            )
            or ""
        ).strip()

        if prescription:
            return prescription

        intensity = str(
            getattr(
                workout,
                "intensity",
                "",
            )
            or ""
        ).strip()

        return (
            intensity
            or None
        )

    @classmethod
    def _planned_summary(
        cls,
        workout,
    ) -> str | None:
        """
        Builds the concise planned-workout summary.
        """

        values = tuple(
            value
            for value in (
                cls._duration_label(
                    workout.duration
                ),
                cls._execution_target(
                    workout
                ),
            )
            if value
        )

        return (
            " · ".join(values)
            or None
        )

    @classmethod
    def _completed_summary(
        cls,
        workout,
    ) -> str | None:
        """
        Builds the concise completed-activity summary.
        """

        values = tuple(
            value
            for value in (
                cls._duration_label(
                    workout.duration
                ),
                cls._distance_label(
                    workout.distance
                ),
            )
            if value
        )

        return (
            " · ".join(values)
            or None
        )

    @staticmethod
    def _add_months(
        value: date,
        months: int,
    ) -> date:
        """
        Adds calendar months while preserving a valid day.
        """

        month_index = (
            value.year * 12
            + value.month
            - 1
            + months
        )

        year, zero_based_month = divmod(
            month_index,
            12,
        )

        month = (
            zero_based_month
            + 1
        )

        day = min(
            value.day,
            monthrange(
                year,
                month,
            )[1],
        )

        return date(
            year,
            month,
            day,
        )

    def _outcome_indexes(
        self,
        *,
        reference_day: date,
    ) -> tuple[
        dict[object, str],
        dict[str, str],
    ]:
        """
        Indexes outcome status by planned and completed
        workout.
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

    def _phase_progress(
        self,
    ) -> dict[
        date,
        tuple[int, int],
    ]:
        """
        Indexes each plan day within its contiguous phase.
        """

        start_day = (
            self.training_plan.start_date
        )
        end_day = (
            self.training_plan.end_date
        )

        if (
            start_day is None
            or end_day is None
        ):
            return {}

        phases = {}
        cursor = start_day

        while cursor <= end_day:
            phase = (
                self.training_plan.phase_on(
                    cursor
                )
            )

            if phase is None:
                cursor += timedelta(
                    days=1
                )
                continue

            phase_start = cursor
            phase_days = []

            while (
                cursor <= end_day
                and (
                    self.training_plan
                    .phase_on(cursor)
                    == phase
                )
            ):
                phase_days.append(
                    cursor
                )
                cursor += timedelta(
                    days=1
                )

            total_days = len(
                phase_days
            )

            for index, phase_day in enumerate(
                phase_days,
                start=1,
            ):
                phases[phase_day] = (
                    index,
                    total_days,
                )

            if cursor == phase_start:
                cursor += timedelta(
                    days=1
                )

        return phases

    def _upcoming_events(
        self,
        *,
        reference_day: date,
    ) -> tuple[
        CalendarUpcomingEventData,
        ...,
    ]:
        """
        Returns factual events scheduled in the next
        six calendar months.
        """

        window_end = self._add_months(
            reference_day,
            6,
        )

        events = []

        for entry in self.events:
            event = entry.event

            event_day = self._calendar_day(
                event.date
            )

            if (
                event_day is None
                or event_day < reference_day
                or event_day > window_end
            ):
                continue

            events.append(
                CalendarUpcomingEventData(
                    event_id=str(
                        event.event_id
                    ),
                    name=repair_mojibake(
                        str(
                            event.name
                            or "Event"
                        )
                    ),
                    event_date=event_day,
                    sport=(
                        event.sport
                        or None
                    ),
                    priority=(
                        entry.priority
                        or None
                    ),
                    distance=(
                        event.distance
                    ),
                    elevation_gain=(
                        event.elevation_gain
                    ),
                )
            )

        return tuple(
            sorted(
                events,
                key=lambda item: (
                    item.event_date,
                    item.name,
                ),
            )
        )

    def build(
        self,
        *,
        year: int,
        month: int,
        reference_day: date,
        selected_day: date | None = None,
    ) -> CalendarMonthData:
        """
        Builds one Monday-first calendar month.
        """

        if not 1 <= month <= 12:
            raise ValueError(
                "month must be between 1 and 12."
            )

        selected_day = (
            selected_day
            or reference_day
        )

        (
            planned_statuses,
            completed_statuses,
        ) = self._outcome_indexes(
            reference_day=reference_day
        )

        planned_by_day = {}

        event_days = {
            event_day
            for entry in self.events
            for event_day in (
                self._calendar_day(
                    entry.event.date
                ),
            )
            if event_day is not None
        }

        for workout in self.training_plan:
            is_race_session = (
                str(
                    workout.intensity
                    or ""
                ).strip().lower()
                == "race effort"
                or str(
                    workout.title
                    or ""
                ).strip().lower()
                == "race"
            )

            if (
                workout.is_rest
                or (
                    workout.day
                    in event_days
                    and is_race_session
                )
            ):
                continue

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
                    summary=(
                        self._planned_summary(
                            workout
                        )
                    ),
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
                            str(
                                workout.workout_id
                            ),
                            "completed",
                        )
                    ),
                    duration=workout.duration,
                    summary=(
                        self._completed_summary(
                            workout
                        )
                    ),
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

            event_values = tuple(
                value
                for value in (
                    event.sport or None,
                    self._distance_label(
                        event.distance
                    ),
                    self._elevation_label(
                        event.elevation_gain
                                       ),
                )
                if value
            )

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
                    summary=(
                        " · ".join(
                            event_values
                        )
                        or None
                    ),
                )
            )

        phase_progress = (
            self._phase_progress()
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
                self._build_day(
                    day=day,
                    month=month,
                    reference_day=reference_day,
                    planned_items=tuple(
                        planned_by_day.get(
                            day,
                            (),
                        )
                    ),
                    completed_items=tuple(
                        completed_by_day.get(
                            day,
                            (),
                        )
                    ),
                    event_items=tuple(
                        events_by_day.get(
                            day,
                            (),
                        )
                    ),
                    phase_progress=(
                        phase_progress.get(
                            day
                        )
                    ),
                )
                for day in week
            )
            for week in calendar_weeks
        )

        selected = next(
            (
                day
                for week in weeks
                for day in week
                if day.day == selected_day
            ),
            None,
        )

        return CalendarMonthData(
            year=year,
            month=month,
            weeks=weeks,
            selected_day=selected,
            upcoming_events=(
                self._upcoming_events(
                    reference_day=(
                        reference_day
                    )
                )
            ),
        )

    def _build_day(
        self,
        *,
        day: date,
        month: int,
        reference_day: date,
        planned_items: tuple[
            CalendarItemData,
            ...,
        ],
        completed_items: tuple[
            CalendarItemData,
            ...,
        ],
        event_items: tuple[
            CalendarItemData,
            ...,
        ],
        phase_progress: (
            tuple[int, int]
            | None
        ),
    ) -> CalendarDayData:
        """
        Builds one immutable calendar day.
        """

        phase = (
            self.training_plan.phase_on(
                day
            )
        )

        items = (
            event_items
            + completed_items
            + planned_items
        )

        is_plan_day = (
            self.training_plan.covers(
                day
            )
        )

        return CalendarDayData(
            day=day,
            is_current_month=(
                day.month == month
            ),
            is_today=(
                day == reference_day
            ),
            phase=phase,
            items=items,
            phase_day_number=(
                phase_progress[0]
                if phase_progress
                is not None
                else None
            ),
            phase_total_days=(
                phase_progress[1]
                if phase_progress
                is not None
                else None
            ),
            is_rest_day=(
                is_plan_day
                and not items
            ),
        )