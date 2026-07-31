from dataclasses import (
    FrozenInstanceError,
)

import pytest

from performancelab.analysis import (
    HeartRateProfile,
    HeartRateZone,
    build_heart_rate_profile,
)


def test_builds_automatic_karvonen_zones():

    profile = build_heart_rate_profile(
        max_hr=190,
        resting_hr=50,
    )

    assert isinstance(
        profile,
        HeartRateProfile,
    )

    assert profile.source == "karvonen"
    assert profile.has_zones is True
    assert profile.uses_manual_zones is False

    assert profile.zone(
        "Z1"
    ) == HeartRateZone(
        name="Z1",
        lower_bpm=120,
        upper_bpm=134,
    )

    assert profile.zone(
        "Z5"
    ) == HeartRateZone(
        name="Z5",
        lower_bpm=176,
        upper_bpm=190,
    )


def test_manual_zones_override_automatic_zones():

    manual_zones = (
        HeartRateZone(
            name="Z1",
            lower_bpm=100,
            upper_bpm=130,
        ),
        HeartRateZone(
            name="Z2",
            lower_bpm=131,
            upper_bpm=150,
        ),
        HeartRateZone(
            name="Z3",
            lower_bpm=151,
            upper_bpm=165,
        ),
        HeartRateZone(
            name="Z4",
            lower_bpm=166,
            upper_bpm=180,
        ),
        HeartRateZone(
            name="Z5",
            lower_bpm=181,
            upper_bpm=197,
        ),
    )

    profile = build_heart_rate_profile(
        max_hr=197,
        resting_hr=50,
        threshold_hr=184,
        manual_zones=manual_zones,
    )

    assert profile is not None

    assert profile.source == "manual"
    assert profile.uses_manual_zones is True
    assert profile.zones == manual_zones
    assert profile.threshold_hr == 184


def test_finds_zone_for_heart_rate():

    profile = build_heart_rate_profile(
        max_hr=190,
        resting_hr=50,
    )

    assert profile is not None

    zone = profile.zone_for(
        170,
    )

    assert zone is not None
    assert zone.name == "Z4"


def test_profile_without_required_values_is_unknown():

    profile = build_heart_rate_profile(
        max_hr=None,
        resting_hr=None,
    )

    assert profile is None


def test_zone_rejects_invalid_range():

    with pytest.raises(
        ValueError,
        match="upper limit",
    ):
        HeartRateZone(
            name="Z1",
            lower_bpm=140,
            upper_bpm=120,
        )


def test_zone_is_immutable():

    zone = HeartRateZone(
        name="Z2",
        lower_bpm=130,
        upper_bpm=150,
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        zone.lower_bpm = 125