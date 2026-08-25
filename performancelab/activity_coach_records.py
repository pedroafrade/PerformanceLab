"""
PerformanceLab

Persistent Training Coach interpretation records.
"""

from __future__ import annotations

import hashlib
import json

from collections.abc import (
    Iterator,
    Mapping,
)
from dataclasses import dataclass
from datetime import (
    datetime,
    timezone,
)
from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from performancelab.coaching import (
        ActivityCoachNarrative,
    )


def activity_coach_context_hash(
    payload: Mapping[
        str,
        object,
    ],
) -> str:
    """
    Returns a deterministic hash of the complete prompt payload.
    """

    serialized = json.dumps(
        dict(
            payload
        ),
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )

    return hashlib.sha256(
        serialized.encode(
            "utf-8"
        )
    ).hexdigest()


@dataclass(frozen=True)
class ActivityCoachInterpretation:
    """
    Immutable generated interpretation for one context version.
    """

    workout_id: str
    contract_version: str
    context_hash: str
    generated_at: datetime
    narrative: ActivityCoachNarrative

    @property
    def identity(
        self,
    ) -> tuple[
        str,
        str,
        str,
    ]:

        return (
            self.workout_id,
            self.contract_version,
            self.context_hash,
        )


class ActivityCoachInterpretationBook:
    """
    Persistent collection of generated interpretations.
    """

    def __init__(
        self,
        records: tuple[
            ActivityCoachInterpretation,
            ...,
        ] = (),
    ) -> None:

        self._records = []

        ordered_records = sorted(
            records,
            key=(
                self
                ._generated_timestamp
            ),
        )

        for record in ordered_records:

            self.add(
                record
            )

    def __iter__(
        self,
    ) -> Iterator[
        ActivityCoachInterpretation
    ]:

        return iter(
            tuple(
                self._records
            )
        )

    def __len__(
        self,
    ) -> int:

        return len(
            self._records
        )

    def find(
        self,
        *,
        workout_id: str,
        contract_version: str,
        context_hash: str,
    ) -> ActivityCoachInterpretation | None:

        identity = (
            workout_id,
            contract_version,
            context_hash,
        )

        return next(
            (
                record
                for record in self._records
                if record.identity == identity
            ),
            None,
        )

    @staticmethod
    def _generated_timestamp(
        record,
    ) -> float:
        """
        Return a comparable generation timestamp.
        """

        generated_at = (
            record.generated_at
        )

        if (
            generated_at.tzinfo
            is None
        ):

            generated_at = (
                generated_at.replace(
                    tzinfo=timezone.utc
                )
            )

        return generated_at.timestamp()

    def latest_for_workout(
        self,
        *,
        workout_id: str,
    ) -> ActivityCoachInterpretation | None:
        """
        Return the latest saved interpretation for a workout.

        This fallback preserves a previous interpretation when
        the current factual context no longer has the same hash.
        """

        candidates = tuple(
            record
            for record in self._records
            if (
                record.workout_id
                == workout_id
            )
        )

        if not candidates:

            return None

        return max(
            candidates,
            key=(
                self
                ._generated_timestamp
            ),
        )

    def add(
        self,
        record: ActivityCoachInterpretation,
    ) -> None:
        """
        Keep only the latest interpretation for a workout.
        """

        self._records = [
            existing
            for existing in self._records
            if (
                existing.workout_id
                != record.workout_id
            )
        ]

        self._records.append(
            record
        )


    def remove_for_workouts(
        self,
        workout_ids,
    ) -> int:
        """
        Remove interpretations belonging to workouts.

        Returns the number of removed records.
        """

        normalized_ids = {
            workout_id
            for workout_id in workout_ids
        }

        previous_count = len(
            self._records
        )

        self._records = [
            record
            for record in self._records
            if (
                record.workout_id
                not in normalized_ids
            )
        ]

        return (
            previous_count
            - len(
                self._records
            )
        )