"""
PerformanceLab

PostgreSQL Training Coach usage repository.
"""

from datetime import (
    date,
    datetime,
    time,
    timedelta,
    timezone,
)

from sqlalchemy import (
    delete,
    func,
    insert,
    select,
)
from sqlalchemy.engine import (
    Connection,
)

from performancelab.storage.postgresql_schema import (
    training_coach_usage,
)
from performancelab.training_coach_usage import (
    TrainingCoachUsageEvent,
    TrainingCoachUsageStatus,
)
from performancelab.training_coach_usage_limits import (
    TrainingCoachUsageCounts,
)


class PostgreSQLTrainingCoachUsageRepository:
    """
    Persist and count factual Training Coach usage.
    """

    def __init__(
        self,
        connection: Connection,
    ) -> None:

        if not isinstance(
            connection,
            Connection,
        ):

            raise TypeError(
                "connection must be a "
                "SQLAlchemy Connection."
            )

        self._connection = connection

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

    @staticmethod
    def _aware_datetime(
        value,
    ) -> datetime:

        if value.tzinfo is None:

            return value.replace(
                tzinfo=timezone.utc
            )

        return value

    @classmethod
    def _event_from_row(
        cls,
        row,
    ) -> TrainingCoachUsageEvent:

        return TrainingCoachUsageEvent(
            purpose=row["purpose"],
            prompt_tokens=row["prompt_tokens"],
            output_tokens=row["output_tokens"],
            total_tokens=row["total_tokens"],
            usage_id=row[
                "usage_id"
            ],
            user_id=row[
                "user_id"
            ],
            occurred_at=(
                cls._aware_datetime(
                    row[
                        "occurred_at"
                    ]
                )
            ),
            status=(
                TrainingCoachUsageStatus(
                    row[
                        "status"
                    ]
                )
            ),
            provider=row[
                "provider"
            ],
            model=row[
                "model"
            ],
            error_code=row[
                "error_code"
            ],
            latency_ms=row[
                "latency_ms"
            ],
            remaining_user_requests=(
                row[
                    "remaining_user_requests"
                ]
            ),
            remaining_global_requests=(
                row[
                    "remaining_global_requests"
                ]
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

        existing = self._connection.execute(
            select(
                training_coach_usage
            ).where(
                training_coach_usage
                .c
                .usage_id
                == event.usage_id
            )
        ).mappings().one_or_none()

        if existing is not None:

            stored_event = (
                self._event_from_row(
                    existing
                )
            )

            if stored_event == event:

                return

            raise ValueError(
                "usage_id already belongs "
                "to another usage event."
            )

        self._connection.execute(
            insert(
                training_coach_usage
            ).values(
                usage_id=event.usage_id,
                purpose=event.purpose,
                prompt_tokens=event.prompt_tokens,
                output_tokens=event.output_tokens,
                total_tokens=event.total_tokens,
                user_id=event.user_id,
                occurred_at=(
                    event.occurred_at
                    .astimezone(
                        timezone.utc
                    )
                ),
                status=event.status.value,
                provider=event.provider,
                model=event.model,
                error_code=(
                    event.error_code
                ),
                latency_ms=(
                    event.latency_ms
                ),
                remaining_user_requests=(
                    event
                    .remaining_user_requests
                ),
                remaining_global_requests=(
                    event
                    .remaining_global_requests
                ),
            )
        )

    def delete(
        self,
        usage_id: str,
    ) -> None:
        """
        Delete one Training Coach usage event.
        """

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

        result = self._connection.execute(
            delete(
                training_coach_usage
            ).where(
                training_coach_usage
                .c
                .usage_id
                == normalized_usage_id
            )
        )

        if result.rowcount != 1:

            raise KeyError(
                "Training Coach usage event not found: "
                f"{normalized_usage_id}"
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

        rows = (
            self._connection.execute(
                select(
                    training_coach_usage
                )
                .where(
                    training_coach_usage
                    .c
                    .user_id
                    == normalized_user_id
                )
                .order_by(
                    training_coach_usage
                    .c
                    .occurred_at,
                    training_coach_usage
                    .c
                    .usage_id,
                )
            )
            .mappings()
            .all()
        )

        return tuple(
            self._event_from_row(
                row
            )
            for row in rows
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

        day_start = datetime.combine(
            validated_day,
            time.min,
            tzinfo=timezone.utc,
        )

        next_day_start = (
            day_start
            + timedelta(
                days=1
            )
        )

        successful_on_day = (
            training_coach_usage
            .c
            .status
            == (
                TrainingCoachUsageStatus
                .GENERATED
                .value
            )
        )

        within_day = (
            training_coach_usage
            .c
            .occurred_at
            >= day_start
        ) & (
            training_coach_usage
            .c
            .occurred_at
            < next_day_start
        )

        global_count = (
            self._connection.execute(
                select(
                    func.count()
                )
                .select_from(
                    training_coach_usage
                )
                .where(
                    successful_on_day
                )
                .where(
                    within_day
                )
            )
            .scalar_one()
        )

        user_count = (
            self._connection.execute(
                select(
                    func.count()
                )
                .select_from(
                    training_coach_usage
                )
                .where(
                    successful_on_day
                )
                .where(
                    within_day
                )
                .where(
                    training_coach_usage
                    .c
                    .user_id
                    == normalized_user_id
                )
            )
            .scalar_one()
        )

        return TrainingCoachUsageCounts(
            user_count=user_count,
            global_count=global_count,
        )
