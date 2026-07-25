"""
PerformanceLab

Coach Context

Collects the athlete information required by the coaching
engine.
"""

from dataclasses import dataclass
from datetime import date

from performancelab.athlete import Athlete


@dataclass(frozen=True)
class CoachContext:
    """
    Snapshot of athlete data used by the coaching engine.
    """

    athlete: Athlete

    today: date

    ctl: float
    atl: float
    tsb: float

    next_event: object | None
    days_until_event: int | None

    sports: tuple[str, ...]
    average_rpe: float | None

    training_plan: object

    previous_event: object | None = None
    days_since_event: int | None = None

    # ======================================================

    @classmethod
    def from_athlete(
        cls,
        athlete: Athlete,
        today: date | None = None,
    ) -> "CoachContext":
        """
        Creates a coaching context from an athlete.
        """

        if (
            today is not None
            and not isinstance(
                today,
                date,
            )
        ):
            raise TypeError(
                "today must be a date"
            )

        reference_date = today or date.today()
        analytics = athlete.analytics

        previous_event = cls._previous_event(
            athlete=athlete,
            today=reference_date,
        )

        days_since_event = (
            cls._days_since_event(
                previous_event=previous_event,
                today=reference_date,
            )
        )

        return cls(
            athlete=athlete,
            today=reference_date,
            ctl=analytics.ctl,
            atl=analytics.atl,
            tsb=analytics.tsb,
            next_event=analytics.next_event,
            days_until_event=(
                analytics.days_until_next_event
            ),
            sports=tuple(
                analytics.sports
            ),
            average_rpe=analytics.average_rpe,
            training_plan=analytics.training_plan,
            previous_event=previous_event,
            days_since_event=days_since_event,
        )

    # ======================================================

    @staticmethod
    def _previous_event(
        *,
        athlete: Athlete,
        today: date,
    ) -> object | None:
        """
        Returns the most recent registered event before today.
        """

        event_book = getattr(
            athlete,
            "events",
            None,
        )

        if event_book is None:
            return None

        candidates = [
            entry
            for entry in event_book
            if (
                getattr(
                    getattr(
                        entry,
                        "event",
                        None,
                    ),
                    "date",
                    None,
                )
                is not None
                and entry.event.date < today
            )
        ]

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda entry: entry.event.date,
        )

    # ======================================================

    @staticmethod
    def _days_since_event(
        *,
        previous_event: object | None,
        today: date,
    ) -> int | None:
        """
        Returns the number of days since the previous event.
        """

        if previous_event is None:
            return None

        event = getattr(
            previous_event,
            "event",
            None,
        )

        if event is None:
            return None

        event_date = getattr(
            event,
            "date",
            None,
        )

        if event_date is None:
            return None

        days = (
            today - event_date
        ).days

        if days < 0:
            return None

        return days