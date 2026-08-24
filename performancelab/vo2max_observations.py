"""
PerformanceLab

Historical factual VO2max observations.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date, datetime
import re


_VO2MAX_PATTERN = re.compile(
    (
        r"\bvo(?:2|₂)\s*max"
        r"\s*[:=]\s*"
        r"(?P<value>\d{1,3}(?:[.,]\d{1,2})?)"
        r"\b"
    ),
    flags=re.IGNORECASE,
)


def _observation_sort_key(
    observation,
) -> tuple[
    int,
    int,
    int,
    int,
    int,
]:
    """
    Builds a comparable chronological key for date and
    datetime observations.
    """

    observed_at = (
        observation.observed_at
    )

    if isinstance(
        observed_at,
        datetime,
    ):
        return (
            observed_at.toordinal(),
            observed_at.hour,
            observed_at.minute,
            observed_at.second,
            observed_at.microsecond,
        )

    return (
        observed_at.toordinal(),
        0,
        0,
        0,
        0,
    )

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
                    key=(
                        _observation_sort_key
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

    def find_for_workout(
        self,
        workout_id: str,
    ) -> VO2MaxObservation | None:
        """
        Returns the factual observation associated with one
        activity.
        """

        return next(
            (
                observation
                for observation in self._observations
                if (
                    observation.workout_id
                    == workout_id
                )
            ),
            None,
        )


    def replace_for_workout(
        self,
        *,
        workout_id: str,
        observation: (
            VO2MaxObservation
            | None
        ),
    ) -> bool:
        """
        Reconciles the observation associated with one
        activity.

        Removing VO2max from the activity notes removes the
        corresponding manual observation.
        """

        if (
            observation is not None
            and observation.workout_id
            != workout_id
        ):
            raise ValueError(
                "observation workout_id must match"
            )

        previous = tuple(
            self._observations
        )

        self._observations = [
            existing
            for existing in self._observations
            if existing.workout_id != workout_id
        ]

        if observation is not None:
            self.add(
                observation
            )

        return (
            tuple(
                self._observations
            )
            != previous
        )


def _manual_method(
    notes: str,
) -> str:
    """
    Identifies only an explicitly declared measurement
    method. It does not infer one from the activity.
    """

    normalized = notes.casefold()

    if "apple watch" in normalized:

        return "apple-watch-estimate"

    if (
        "laboratory" in normalized
        or "laboratório" in normalized
        or re.search(
            r"\blab\b",
            normalized,
        )
    ):

        return "laboratory-test"

    if "garmin" in normalized:

        return "garmin-estimate"

    return "unspecified-estimate"


def parse_vo2max_observation(
    *,
    notes: str,
    observed_at: (
        date
        | datetime
        | None
    ),
    workout_id: str,
) -> VO2MaxObservation | None:
    """
    Extracts an explicit VO2max declaration from activity
    notes.

    Accepted examples include:

    VO2max: 52.4 Apple Watch
    VO₂max = 52,4
    """

    if observed_at is None:

        return None

    match = _VO2MAX_PATTERN.search(
        notes
    )

    if match is None:

        return None

    value = float(
        match.group(
            "value"
        ).replace(
            ",",
            ".",
        )
    )

    return VO2MaxObservation(
        observed_at=observed_at,
        value=value,
        source="manual",
        method=_manual_method(
            notes
        ),
        workout_id=workout_id,
    )


def synchronize_vo2max_observation_from_notes(
    *,
    observations: VO2MaxObservationBook,
    notes: str,
    observed_at: (
        date
        | datetime
        | None
    ),
    workout_id: str,
) -> bool:
    """
    Synchronizes one activity's explicit VO2max declaration
    with the athlete's factual history.
    """

    observation = (
        parse_vo2max_observation(
            notes=notes,
            observed_at=observed_at,
            workout_id=workout_id,
        )
    )

    return observations.replace_for_workout(
        workout_id=workout_id,
        observation=observation,
    )