from datetime import datetime

from performancelab import Workout

from app.components.activity_analysis import (
    _distance_domain,
    _route_similarity_score,
)


def _workout_with_route(
    points,
):
    workout = Workout()

    workout.info.sport = (
        "Trail Running"
    )

    workout.info.date = datetime(
        2026,
        8,
        9,
        8,
        0,
    )

    workout.sensors.add(
        "gps",
        [
            {
                "latitude": latitude,
                "longitude": longitude,
                "elevation": elevation,
                "time": (
                    datetime(
                        2026,
                        8,
                        9,
                        8,
                        index,
                    ).isoformat()
                ),
            }
            for index, (
                latitude,
                longitude,
                elevation,
            )
            in enumerate(points)
        ],
    )

    return workout


def test_route_similarity_is_high_for_same_route():

    route = [
        (
            38.70,
            -9.40,
            100,
        ),
        (
            38.705,
            -9.395,
            130,
        ),
        (
            38.710,
            -9.390,
            160,
        ),
        (
            38.715,
            -9.385,
            120,
        ),
    ]

    first = _workout_with_route(
        route
    )

    second = _workout_with_route(
        route
    )

    assert (
        _route_similarity_score(
            first,
            second,
        )
        >= 95
    )


def test_route_similarity_rejects_different_route():

    first = _workout_with_route(
        [
            (
                38.70,
                -9.40,
                100,
            ),
            (
                38.71,
                -9.39,
                120,
            ),
            (
                38.72,
                -9.38,
                140,
            ),
        ]
    )

    second = _workout_with_route(
        [
            (
                39.20,
                -8.90,
                100,
            ),
            (
                39.21,
                -8.89,
                120,
            ),
            (
                39.22,
                -8.88,
                140,
            ),
        ]
    )

    assert (
        _route_similarity_score(
            first,
            second,
        )
        < 20
    )

def test_distance_domain_ends_at_last_record():

    result = _distance_domain(
        [
            {
                "Distance": 0.0,
            },
            {
                "Distance": 5.25,
            },
            {
                "Distance": 10.40,
            },
        ]
    )

    assert result == (
        0.0,
        10.40,
    )


def test_distance_domain_uses_route_end():

    result = _distance_domain(
        [
            {
                "Distance": 0.0,
            },
            {
                "Distance": 10.40,
            },
        ],
        [
            {
                "Distance": 0.2,
            },
            {
                "Distance": 10.1,
            },
        ],
    )

    assert result == (
        0.0,
        10.40,
    )