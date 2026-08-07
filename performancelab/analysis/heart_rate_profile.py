"""
PerformanceLab

Heart Rate Profile

Represents an athlete's heart-rate thresholds and
training zones.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from statistics import median

from performancelab.physiology import (
    heart_rate_zones,
)


@dataclass(frozen=True, slots=True)
class HeartRateZone:
    """
    Immutable heart-rate training zone.
    """

    name: str
    lower_bpm: int
    upper_bpm: int

    def __post_init__(self) -> None:

        normalized_name = (
            str(self.name)
            .strip()
            .upper()
        )

        if not normalized_name:
            raise ValueError(
                "Heart-rate zone name cannot be empty."
            )

        if self.lower_bpm <= 0:
            raise ValueError(
                "Heart-rate zone lower limit must "
                "be positive."
            )

        if self.upper_bpm < self.lower_bpm:
            raise ValueError(
                "Heart-rate zone upper limit cannot "
                "be lower than its lower limit."
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )

    # ======================================================

    def contains(
        self,
        heart_rate: float,
    ) -> bool:
        """
        Returns whether a heart-rate value belongs
        to this zone.
        """

        return (
            self.lower_bpm
            <= heart_rate
            <= self.upper_bpm
        )


@dataclass(frozen=True, slots=True)
class HeartRateProfile:
    """
    Immutable athlete heart-rate profile.

    Manual zones take precedence over zones calculated
    from maximum and resting heart rate.
    """

    max_hr: int | None
    resting_hr: int | None
    threshold_hr: int | None

    zones: tuple[HeartRateZone, ...]

    source: str

    def __post_init__(self) -> None:

        normalized_zones = tuple(
            self.zones
        )

        zone_names = tuple(
            zone.name
            for zone in normalized_zones
        )

        if (
            len(zone_names)
            != len(set(zone_names))
        ):
            raise ValueError(
                "Heart-rate zone names must be unique."
            )

        object.__setattr__(
            self,
            "zones",
            normalized_zones,
        )

    # ======================================================

    @property
    def has_zones(self) -> bool:
        """
        Returns whether the athlete has usable zones.
        """

        return bool(
            self.zones
        )

    # ======================================================

    @property
    def uses_manual_zones(self) -> bool:
        """
        Returns whether the zones were defined manually.
        """

        return self.source == "manual"

    # ======================================================

    def zone(
        self,
        name: str,
    ) -> HeartRateZone | None:
        """
        Returns a zone by name.
        """

        normalized_name = (
            str(name)
            .strip()
            .upper()
        )

        return next(
            (
                zone
                for zone in self.zones
                if zone.name
                == normalized_name
            ),
            None,
        )

    # ======================================================

    def zone_for(
        self,
        heart_rate: float,
    ) -> HeartRateZone | None:
        """
        Returns the zone containing a heart-rate value.
        """

        return next(
            (
                zone
                for zone in self.zones
                if zone.contains(
                    heart_rate
                )
            ),
            None,
        )


def build_heart_rate_profile(
    *,
    max_hr: int | None,
    resting_hr: int | None,
    threshold_hr: int | None = None,
    manual_zones: tuple[
        HeartRateZone,
        ...,
    ] = (),
) -> HeartRateProfile | None:
    """
    Builds the athlete's heart-rate profile.

    Manually defined zones take precedence. When no manual
    zones exist, Karvonen zones are calculated from maximum
    and resting heart rate.
    """

    normalized_manual_zones = tuple(
        manual_zones
    )

    if normalized_manual_zones:

        return HeartRateProfile(
            max_hr=max_hr,
            resting_hr=resting_hr,
            threshold_hr=threshold_hr,
            zones=normalized_manual_zones,
            source="manual",
        )

    calculated_zones = heart_rate_zones(
        max_hr,
        resting_hr,
    )

    if calculated_zones is None:
        return None

    zones = tuple(
        HeartRateZone(
            name=name,
            lower_bpm=round(
                limits[0]
            ),
            upper_bpm=round(
                limits[1]
            ),
        )
        for name, limits
        in calculated_zones.items()
    )

    return HeartRateProfile(
        max_hr=max_hr,
        resting_hr=resting_hr,
        threshold_hr=threshold_hr,
        zones=zones,
        source="karvonen",
    )

def _heart_rate_sample_timestamp(
    value,
) -> datetime | None:
    """
    Normalizes a sensor timestamp.
    """

    if isinstance(
        value,
        datetime,
    ):
        return value

    if isinstance(
        value,
        str,
    ):

        try:

            return datetime.fromisoformat(
                value.replace(
                    "Z",
                    "+00:00",
                )
            )

        except ValueError:

            return None

    return None


def heart_rate_zone_durations(
    workout,
    profile: HeartRateProfile | None,
) -> dict[str, float]:
    """
    Returns recorded seconds spent in each
    heart-rate zone.

    Timestamped samples use the interval until the
    next sample. Large recording gaps are replaced by
    the normal sampling interval so pauses do not
    artificially inflate time in zone.
    """

    if (
        profile is None
        or not profile.has_zones
    ):

        return {}

    totals = {
        zone.name: 0.0
        for zone in profile.zones
    }

    sensor = workout.sensors.get(
        "heart_rate"
    )

    if not isinstance(
        sensor,
        (list, tuple),
    ):

        return totals

    samples = []

    for item in sensor:

        if isinstance(
            item,
            dict,
        ):

            value = item.get(
                "value"
            )

            timestamp = (
                _heart_rate_sample_timestamp(
                    item.get(
                        "time"
                    )
                )
            )

        else:

            value = item
            timestamp = None

        if (
            not isinstance(
                value,
                (int, float),
            )
            or isinstance(
                value,
                bool,
            )
            or value <= 0
        ):

            continue

        samples.append(
            {
                "time": timestamp,
                "value": float(
                    value
                ),
            }
        )

    if not samples:

        return totals

    timestamped = [
        sample
        for sample in samples
        if sample["time"] is not None
    ]

    if len(timestamped) >= 2:

        timestamped.sort(
            key=lambda sample: (
                sample["time"]
            )
        )

        positive_intervals = []

        for current, following in zip(
            timestamped,
            timestamped[1:],
            strict=False,
        ):

            interval = (
                following["time"]
                - current["time"]
            ).total_seconds()

            if (
                interval > 0
                and interval <= 60
            ):

                positive_intervals.append(
                    interval
                )

        nominal_interval = (
            median(
                positive_intervals
            )
            if positive_intervals
            else 1.0
        )

        maximum_interval = max(
            30.0,
            nominal_interval * 5,
        )

        for index, sample in enumerate(
            timestamped
        ):

            if (
                index
                < len(timestamped) - 1
            ):

                following = (
                    timestamped[
                        index + 1
                    ]
                )

                interval = (
                    following["time"]
                    - sample["time"]
                ).total_seconds()

                if (
                    interval <= 0
                    or interval
                    > maximum_interval
                ):

                    interval = (
                        nominal_interval
                    )

            else:

                interval = (
                    nominal_interval
                )

            zone = profile.zone_for(
                sample["value"]
            )

            if zone is not None:

                totals[
                    zone.name
                ] += interval

        return totals

    # Fallback for sensor streams without timestamps.
    # Each sample receives equal weight.
    for sample in samples:

        zone = profile.zone_for(
            sample["value"]
        )

        if zone is not None:

            totals[
                zone.name
            ] += 1.0

    return totals