"""
PerformanceLab

Historical factual VO2max observations.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class VO2MaxObservation:
    """
    One factual, dated VO2max observation.

    The value may originate from a device, laboratory test,
    manual entry, or a future PerformanceLab estimate. The
    source and method preserve that distinction.
    """

    observed_at: date | datetime
    value: float
    source: str
    method: str
    workout_id: str | None = None

    def __post_init__(
        self,
    ) -> None:

        if not isinstance(
            self.observed_at,
            (date, datetime),
        ):
            raise TypeError(
                "observed_at must be a date or datetime"
            )

        if not isinstance(
            self.value,
            (int, float),
        ):
            raise TypeError(
                "value must be numeric"
            )

        if self.value <= 0:
            raise ValueError(
                "value must be greater than zero"
            )

        if not self.source.strip():
            raise ValueError(
                "source must not be empty"
            )

        if not self.method.strip():
            raise ValueError(
                "method must not be empty"
            )

    @property
    def identity(
        self,
    ) -> tuple[
        date | datetime,
        str,
        str,
    ]:

        return (
            self.observed_at,
            self.source,
            self.method,
        )


class VO2MaxObservationBook:
    """
    Persistent historical collection of VO2max observations.
    """

    def __init__(
        self,
        observations: tuple[
            VO2MaxObservation,
            ...,
        ] = (),
    ) -> None:

        self._observations = list(
            observations
        )

    def __iter__(
        self,
    ) -> Iterator[
        VO2MaxObservation
    ]:

        return iter(
            tuple(
                sorted(
                    self._observations,
                    key=lambda observation: (
                        observation.observed_at
                    ),
                )
            )
        )

    def __len__(
        self,
    ) -> int:

        return len(
            self._observations
        )

    def add(
        self,
        observation: VO2MaxObservation,
    ) -> None:
        """
        Adds an observation or replaces the same factual
        identity.
        """

        self._observations = [
            existing
            for existing in self._observations
            if (
                existing.identity
                != observation.identity
            )
        ]

        self._observations.append(
            observation
        )