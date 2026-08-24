"""
PerformanceLab

In-memory Training Coach usage repository.
"""

from datetime import (
    date,
    datetime,
    timezone,
)

from performancelab.training_coach_usage import (
    TrainingCoachUsageEvent,
)
from performancelab.training_coach_usage_limits import (
    TrainingCoachUsageCounts,
)


class InMemoryTrainingCoachUsageRepository:
    """
    Deterministic usage repository for application tests.
    """

    def __init__(
        self,
        events=(),
    ) -> None:

        self._events: dict[
            str,
            TrainingCoachUsageEvent,
        ] = {}

        for event in events:

            self.save(
                event
            )

    @staticmethod
    def _normalized_user_id(
        user_id,
    ) -> str:

        if not isinstance(
            user_id,
            str,
        ):

            raise TypeError(
                "user_id must be a string."
            )

        normalized_user_id = (
            user_id.strip()
        )

        if not normalized_user_id:

            raise ValueError(
                "user_id cannot be empty."
            )

        return normalized_user_id

    @staticmethod
    def _validated_day(
        utc_day,
    ) -> date:

        if (
            not isinstance(
                utc_day,
                date,
            )
            or isinstance(
                utc_day,
                datetime,
            )
        ):

            raise TypeError(
                "utc_day must be a date."
            )

        return utc_day

    def save(
        self,
        event: TrainingCoachUsageEvent,
    ) -> None:

        if not isinstance(
            event,
            TrainingCoachUsageEvent,
        ):

            raise TypeError(
                "event must be a "
                "TrainingCoachUsageEvent."
            )

        existing = self._events.get(
            event.usage_id
        )

        if existing is not None:

            if existing == event:

                return

            raise ValueError(
                "usage_id already belongs "
                "to another usage event."
            )

        self._events[
            event.usage_id
        ] = event

    def counts_for_utc_day(
        self,
        *,
        user_id: str,
        utc_day: date,
    ) -> TrainingCoachUsageCounts:

        normalized_user_id = (
            self._normalized_user_id(
                user_id
            )
        )

        validated_day = (
            self._validated_day(
                utc_day
            )
        )

        successful_events = tuple(
            event
            for event in self._events.values()
            if (
                event.counts_toward_limit
                and (
                    event.occurred_at
                    .astimezone(
                        timezone.utc
                    )
                    .date()
                    == validated_day
                )
            )
        )

        user_count = sum(
            1
            for event in successful_events
            if (
                event.user_id
                == normalized_user_id
            )
        )

        return TrainingCoachUsageCounts(
            user_count=user_count,
            global_count=len(
                successful_events
            ),
        )