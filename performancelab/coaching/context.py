"""
PerformanceLab

Coach Context

Collects the athlete information required by the coaching
engine.
"""

from dataclasses import dataclass
from datetime import date, timedelta

from performancelab.athlete import Athlete

from performancelab.analysis.performance_profile import PerformanceProfile
from performancelab.analysis.training_state import TrainingState

COMPETITION_CLUSTER_MAX_DAYS = 56

EVENT_PRIORITY_RANK = {
    "A": 3,
    "B": 2,
    "C": 1,
}

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

    upcoming_events: tuple[object, ...] = ()

    # ======================================================

    @property
    def training_state(self):
        """
        Returns the athlete's physiological training state.

        Test doubles that do not expose analytics continue to work by
        returning None.
        """

        analytics = getattr(
            self.athlete,
            "analytics",
            None,
        )

        if analytics is None:
            return None

        return getattr(
            analytics,
            "training_state",
            None,
        )
    
    # ======================================================

    @property
    def needs_recovery(self) -> bool:
        """
        Returns whether the athlete should prioritise recovery.

        New code uses TrainingState when available.
        Older tests and lightweight context doubles continue to
        work through the legacy TSB heuristic.
        """

        training_state = self.training_state

        if training_state is not None:
            return training_state.needs_recovery

        return self.tsb < -20

    # ======================================================

    @property
    def readiness(self) -> str:
        """
        Returns the athlete's current training readiness.
        """

        training_state = self.training_state

        if training_state is not None:
            return training_state.readiness

        if self.tsb < -20:
            return "recovery"

        if self.tsb < 0:
            return "easy"

        return "ready"

    # ======================================================

    @property
    def should_reduce_volume(self) -> bool:
        """
        Indicates whether planned volume should be reduced.
        """

        training_state = self.training_state

        if training_state is not None:
            return training_state.should_reduce_volume

        return self.tsb < -10

    # ======================================================

    @property
    def can_tolerate_intensity(self) -> bool:
        """
        Indicates whether intensity sessions are appropriate.
        """

        training_state = self.training_state

        if training_state is not None:
            return training_state.can_tolerate_intensity

        return self.tsb >= 0

    # ======================================================

    @property
    def can_absorb_more_volume(self) -> bool:
        """
        Indicates whether additional volume can be tolerated.
        """

        training_state = self.training_state

        if training_state is not None:
            return training_state.can_absorb_more_volume

        return self.tsb > -10

    # ======================================================

    @property
    def performance_profile(self):
        """
        Returns the athlete's physiological performance profile.

        Test doubles that do not expose analytics continue to work by
        returning None.
        """

        analytics = getattr(
            self.athlete,
            "analytics",
            None,
        )

        if analytics is None:
            return None

        return analytics.performance_profile

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

        upcoming_events = cls._upcoming_events(
            athlete=athlete,
            today=reference_date,
        )

        next_event = (
            upcoming_events[0]
            if upcoming_events
            else analytics.next_event
        )

        days_until_event = cls._days_until_event(
            event_entry=next_event,
            today=reference_date,
        )

        if (
            days_until_event is None
            and next_event is analytics.next_event
        ):
            days_until_event = (
                analytics.days_until_next_event
            )

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

            next_event=next_event,
            days_until_event=days_until_event,
            sports=tuple(
                analytics.sports
            ),
            average_rpe=analytics.average_rpe,
            training_plan=analytics.training_plan,
            previous_event=previous_event,
            days_since_event=days_since_event,
            upcoming_events=upcoming_events,
        )

    # ======================================================

    @staticmethod
    def _upcoming_events(
        *,
        athlete: Athlete,
        today: date,
        horizon_days: int = 365,
    ) -> tuple[object, ...]:
        """
        Returns registered events occurring from today through
        the configured planning horizon, ordered chronologically.
        """

        event_book = getattr(
            athlete,
            "events",
            None,
        )

        if event_book is None:
            return ()

        horizon_date = (
            today
            + timedelta(
                days=horizon_days,
            )
        )

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
                and today <= entry.event.date <= horizon_date
            )
        ]

        return tuple(
            sorted(
                candidates,
                key=lambda entry: entry.event.date,
            )
        )

    # ======================================================

    @staticmethod
    def _days_until_event(
        *,
        event_entry: object | None,
        today: date,
    ) -> int | None:
        """
        Returns the number of days until an event.
        """

        if event_entry is None:
            return None

        event = getattr(
            event_entry,
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

        return (
            event_date - today
        ).days

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

    # ======================================================

    @property
    def is_post_race(self) -> bool:
        """
        Indicates whether the athlete is inside the automatic
        post-race recovery window.
        """

        return (
            self.days_since_event is not None
            and 0 <= self.days_since_event <= 7
        )

    # ======================================================

    @property
    def is_fatigue_regeneration(self) -> bool:
        """
        Indicates whether regeneration was triggered by fatigue
        rather than by a recent race.
        """

        return (
            self.needs_recovery
            and not self.is_post_race
        )

    # ======================================================

    @property
    def has_upcoming_event(self) -> bool:
        """
        Indicates whether at least one upcoming event exists.
        """

        return self.next_event is not None

    # ======================================================

    @property
    def has_multiple_events(self) -> bool:
        """
        Indicates whether the competition calendar contains
        more than one upcoming event.
        """

        return len(self.upcoming_events) > 1

    # ======================================================

    @property
    def next_event_after_current(
        self,
    ) -> object | None:
        """
        Returns the event following the current next event.
        """

        if len(self.upcoming_events) < 2:
            return None

        return self.upcoming_events[1]

    # ======================================================

    @property
    def competition_block_events(
        self,
    ) -> tuple[object, ...]:
        """
        Returns the first chronological block of upcoming events.

        Consecutive events belong to the same block when they
        are no more than eight weeks apart.
        """

        if not self.upcoming_events:
            return ()

        block = [
            self.upcoming_events[0]
        ]

        for event_entry in self.upcoming_events[1:]:

            previous_date = getattr(
                getattr(
                    block[-1],
                    "event",
                    None,
                ),
                "date",
                None,
            )

            event_date = getattr(
                getattr(
                    event_entry,
                    "event",
                    None,
                ),
                "date",
                None,
            )

            if (
                previous_date is None
                or event_date is None
            ):
                break

            gap_days = (
                event_date
                - previous_date
            ).days

            if (
                gap_days
                > COMPETITION_CLUSTER_MAX_DAYS
            ):
                break

            block.append(
                event_entry
            )

        return tuple(block)

    # ======================================================

    @property
    def primary_event(
        self,
    ) -> object | None:
        """
        Selects the primary event from the current competition block.

        Selection order:
        1. athlete priority;
        2. running effort distance;
        3. target duration;
        4. chronological order.
        """

        if not self.competition_block_events:
            return None

        return max(
            self.competition_block_events,
            key=self._event_priority_key,
        )

    # ======================================================

    @staticmethod
    def _event_priority_key(
        event_entry,
    ) -> tuple[int, float, float, int]:
        """
        Builds the comparison key used to select a primary event.
        """

        priority = str(
            getattr(
                event_entry,
                "priority",
                "",
            )
        ).strip().upper()

        priority_rank = (
            EVENT_PRIORITY_RANK.get(
                priority,
                0,
            )
        )

        event = getattr(
            event_entry,
            "event",
            None,
        )

        effort_distance = getattr(
            event,
            "effort_distance",
            None,
        )

        if effort_distance is None:
            effort_distance = 0.0

        target_time = getattr(
            event_entry,
            "target_time",
            None,
        )

        target_seconds = (
            target_time.total_seconds()
            if target_time is not None
            else 0.0
        )

        event_date = getattr(
            event,
            "date",
            None,
        )

        chronological_priority = (
            -event_date.toordinal()
            if event_date is not None
            else 0
        )

        return (
            priority_rank,
            float(effort_distance),
            target_seconds,
            chronological_priority,
        )

    # ======================================================

    @property
    def days_between_events(
        self,
    ) -> int | None:
        """
        Returns the distance in days between the consecutive
        events relevant to the current competition cycle.
        """

        first_event = None
        second_event = None

        if (
            self.previous_event is not None
            and self.next_event is not None
        ):
            first_event = self.previous_event
            second_event = self.next_event

        elif (
            self.next_event is not None
            and self.next_event_after_current is not None
        ):
            first_event = self.next_event
            second_event = self.next_event_after_current

        if (
            first_event is None
            or second_event is None
        ):
            return None

        first_date = getattr(
            getattr(
                first_event,
                "event",
                None,
            ),
            "date",
            None,
        )

        second_date = getattr(
            getattr(
                second_event,
                "event",
                None,
            ),
            "date",
            None,
        )

        if (
            first_date is None
            or second_date is None
        ):
            return None

        days = (
            second_date - first_date
        ).days

        if days < 0:
            return None

        return days

    # ======================================================

    @property
    def competition_block(self) -> str:
        """
        Classifies the current competition calendar.

        Returns ``season_end`` when no future event exists,
        ``cluster`` when consecutive events are no more than
        eight weeks apart, and ``single`` otherwise.
        """

        if self.next_event is None:
            return "season_end"

        days_between_events = (
            self.days_between_events
        )

        if (
            days_between_events is not None
            and days_between_events
            <= COMPETITION_CLUSTER_MAX_DAYS
        ):
            return "cluster"

        return "single"