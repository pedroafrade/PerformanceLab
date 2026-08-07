from datetime import (
    datetime,
    timedelta,
)
from types import SimpleNamespace

from performancelab.analysis import (
    HeartRateProfile,
    HeartRateZone,
    heart_rate_zone_durations,
)


def test_calculates_time_in_heart_rate_zones():

    profile = HeartRateProfile(
        max_hr=190,
        resting_hr=50,
        threshold_hr=177,
        zones=(
            HeartRateZone(
                "Z1",
                100,
                119,
            ),
            HeartRateZone(
                "Z2",
                120,
                139,
            ),
            HeartRateZone(
                "Z3",
                140,
                159,
            ),
            HeartRateZone(
                "Z4",
                160,
                179,
            ),
            HeartRateZone(
                "Z5",
                180,
                200,
            ),
        ),
        source="manual",
    )

    start = datetime(
        2026,
        8,
        7,
        8,
        0,
    )

    workout = SimpleNamespace(
        sensors={
            "heart_rate": [
                {
                    "time": start,
                    "value": 110,
                },
                {
                    "time": (
                        start
                        + timedelta(
                            seconds=10
                        )
                    ),
                    "value": 130,
                },
                {
                    "time": (
                        start
                        + timedelta(
                            seconds=20
                        )
                    ),
                    "value": 150,
                },
                {
                    "time": (
                        start
                        + timedelta(
                            seconds=30
                        )
                    ),
                    "value": 170,
                },
                {
                    "time": (
                        start
                        + timedelta(
                            seconds=40
                        )
                    ),
                    "value": 185,
                },
            ]
        }
    )

    result = (
        heart_rate_zone_durations(
            workout,
            profile,
        )
    )

    assert result == {
        "Z1": 10.0,
        "Z2": 10.0,
        "Z3": 10.0,
        "Z4": 10.0,
        "Z5": 10.0,
    }