"""
PerformanceLab

JSON Training Coach usage repository.
"""

import json

from datetime import (
    date,
    datetime,
    timezone,
)
from pathlib import (
    Path,
)

from performancelab.training_coach_usage import (
    TrainingCoachUsageEvent,
    TrainingCoachUsageStatus,
)
from performancelab.training_coach_usage_limits import (
    TrainingCoachUsageCounts,
)


class JsonTrainingCoachUsageRepository:
    """
    Persist factual Training Coach usage as JSON files.
    """

    def __init__(
        self,
        directory: str | Path = (
            "data/training_coach_usage"
        ),
    ) -> None:

        self._directory = Path(
            directory
        )

        self._directory.mkdir(
            parents=True,
            exist_ok=True,
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

    def _path_for(
        self,
        usage_id: str,
    ) -> Path:

        if not isinstance(
            usage_id,
            str,
        ):

            raise TypeError(
                "usage_id must be a string."
            )

        normalized_usage_id = (
            usage_id.strip()
        )

        if not normalized_usage_id:

            raise ValueError(
                "usage_id cannot be empty."
            )

        if (
            Path(
                normalized_usage_id
            ).name
            != normalized_usage_id
            or "/"
            in normalized_usage_id
            or "\\"
            in normalized_usage_id
        ):

            raise ValueError(
                "usage_id cannot contain "
                "a file path."
            )

        return (
            self._directory
            / f"{normalized_usage_id}.json"
        )

    @staticmethod
    def _load_from_path(
        path: Path,
    ) -> TrainingCoachUsageEvent:

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(
                file
            )

        version = data.get(
            "version"
        )

        if version not in (
            1,
            2,
        ):

            raise ValueError(
                "Unsupported Training Coach "
                "usage version."
            )

        return TrainingCoachUsageEvent(
            usage_id=data[
                "usage_id"
            ],
            user_id=data[
                "user_id"
            ],
            occurred_at=(
                datetime.fromisoformat(
                    data[
                        "occurred_at"
                    ]
                )
            ),
            status=(
                TrainingCoachUsageStatus(
                    data[
                        "status"
                    ]
                )
            ),
            provider=data.get(
                "provider"
            ),
            model=data.get(
                "model"
            ),
            error_code=data.get(
                "error_code"
            ),
            latency_ms=data.get(
                "latency_ms"
            ),
            remaining_user_requests=(
                data.get(
                    "remaining_user_requests"
                )
            ),
            remaining_global_requests=(
                data.get(
                    "remaining_global_requests"
                )
            ),
        )

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

        path = self._path_for(
            event.usage_id
        )

        if path.exists():

            existing = (
                self._load_from_path(
                    path
                )
            )

            if existing == event:

                return

            raise ValueError(
                "usage_id already belongs "
                "to another usage event."
            )

        data = {
            "version": 2,
            "usage_id": event.usage_id,
            "user_id": event.user_id,
            "occurred_at": (
                event.occurred_at
                .isoformat()
            ),
            "status": event.status.value,
            "provider": event.provider,
            "model": event.model,
            "error_code": (
                event.error_code
            ),
            "latency_ms": (
                event.latency_ms
            ),
            "remaining_user_requests": (
                event
                .remaining_user_requests
            ),
            "remaining_global_requests": (
                event
                .remaining_global_requests
            ),
        }

        temporary_path = (
            path.with_suffix(
                ".tmp"
            )
        )

        with temporary_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        temporary_path.replace(
            path
        )

    def list(
        self,
    ) -> tuple[
        TrainingCoachUsageEvent,
        ...,
    ]:

        events = tuple(
            self._load_from_path(
                path
            )
            for path
            in self._directory.glob(
                "*.json"
            )
        )

        return tuple(
            sorted(
                events,
                key=lambda event: (
                    event.occurred_at,
                    event.usage_id,
                ),
            )
        )

    def list_for_user(
        self,
        user_id: str,
    ) -> tuple[
        TrainingCoachUsageEvent,
        ...,
    ]:
        """
        Return only usage events belonging to one user.
        """

        normalized_user_id = (
            self._normalized_user_id(
                user_id
            )
        )

        return tuple(
            event
            for event in self.list()
            if (
                event.user_id
                == normalized_user_id
            )
        )

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
            for event in self.list()
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