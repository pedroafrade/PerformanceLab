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
from datetime import datetime
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

        self._records = list(
            records
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

    def add(
        self,
        record: ActivityCoachInterpretation,
    ) -> None:
        """
        Adds or replaces the same interpretation identity.
        """

        self._records = [
            existing
            for existing in self._records
            if (
                existing.identity
                != record.identity
            )
        ]

        self._records.append(
            record
        )