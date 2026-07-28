from performancelab.physiology.exertion import (
    estimate_rpe_from_heart_rate,
)


def test_estimates_rpe_from_relative_heart_rate():

    estimate = estimate_rpe_from_heart_rate(
        [
            120,
            134,
            148,
            162,
            176,
        ],
        max_hr=190,
        resting_hr=50,
    )

    assert estimate == 5.6


def test_same_heart_rate_depends_on_athlete_profile():

    lower_reserve_estimate = estimate_rpe_from_heart_rate(
        [150],
        max_hr=170,
        resting_hr=50,
    )

    higher_reserve_estimate = estimate_rpe_from_heart_rate(
        [150],
        max_hr=200,
        resting_hr=40,
    )

    assert (
        lower_reserve_estimate
        > higher_reserve_estimate
    )


def test_missing_heart_rate_returns_none():

    assert estimate_rpe_from_heart_rate(
        [],
        max_hr=190,
        resting_hr=50,
    ) is None


def test_missing_athlete_profile_returns_none():

    assert estimate_rpe_from_heart_rate(
        [150],
        max_hr=None,
        resting_hr=50,
    ) is None


def test_ignores_missing_samples():

    estimate = estimate_rpe_from_heart_rate(
        [
            None,
            120,
            None,
        ],
        max_hr=190,
        resting_hr=50,
    )

    assert estimate == 3.0