"""
PerformanceLab

Heart Rate Profile

Represents an athlete's heart-rate thresholds and
training zones.
"""

from __future__ import annotations

from dataclasses import dataclass

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