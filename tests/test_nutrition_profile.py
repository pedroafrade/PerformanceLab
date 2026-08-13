from dataclasses import (
    FrozenInstanceError,
)
from datetime import timedelta

import pytest

from performancelab.analysis import (
    NutritionProfile,
)


def test_default_profile_uses_endurance_ranges():

    profile = NutritionProfile()

    assert (
        profile.carbohydrate_per_hour
        == 80
    )

    assert (
        profile.fluid_lower_ml_per_hour
        == 450
    )

    assert (
        profile.fluid_upper_ml_per_hour
        == 600
    )

    assert (
        profile.sodium_lower_mg_per_hour
        == 400
    )

    assert (
        profile.sodium_upper_mg_per_hour
        == 600
    )


def test_calculates_long_trail_requirements():

    profile = NutritionProfile()

    duration = timedelta(
        minutes=201,
    )

    assert (
        profile.carbohydrate_for(
            duration
        )
        == 270
    )

    assert (
        profile.fluid_for(
            duration
        )
        == (
            1500,
            2000,
        )
    )

    assert (
        profile.sodium_for(
            duration
        )
        == (
            1350,
            2000,
        )
    )


def test_accepts_tested_athlete_values():

    profile = NutritionProfile(
        carbohydrate_per_hour=90,
        fluid_lower_ml_per_hour=450,
        fluid_upper_ml_per_hour=550,
        sodium_lower_mg_per_hour=450,
        sodium_upper_mg_per_hour=650,
        gel_carbohydrate_grams=25,
        pre_race_carbohydrate_lower=70,
        pre_race_carbohydrate_upper=90,
        source="manual",
    )

    assert (
        profile.carbohydrate_per_hour
        == 90
    )

    assert profile.source == "manual"


def test_rejects_inverted_fluid_range():

    with pytest.raises(
        ValueError,
        match="Fluid lower limit",
    ):
        NutritionProfile(
            fluid_lower_ml_per_hour=700,
            fluid_upper_ml_per_hour=500,
        )


def test_rejects_invalid_duration():

    profile = NutritionProfile()

    with pytest.raises(
        ValueError,
        match="duration must be positive",
    ):
        profile.carbohydrate_for(
            timedelta(0)
        )


def test_profile_is_immutable():

    profile = NutritionProfile()

    with pytest.raises(
        FrozenInstanceError
    ):
        profile.carbohydrate_per_hour = 90

def test_default_profile_is_not_athlete_tested():

    profile = NutritionProfile()

    assert profile.is_athlete_tested is False


def test_recorded_profile_is_athlete_tested():

    profile = NutritionProfile(
        source="athlete-tested",
    )

    assert profile.is_athlete_tested is True