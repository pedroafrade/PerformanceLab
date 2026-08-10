"""
Tests for the workout route map.
"""

import pytest

from app.components.route_map import (
    _route_view,
)


def test_route_view_contains_complete_route():

    latitude, longitude, zoom = (
        _route_view(
            [
                [
                    -9.40,
                    38.70,
                ],
                [
                    -9.20,
                    38.80,
                ],
                [
                    -9.30,
                    38.75,
                ],
            ]
        )
    )

    assert latitude == pytest.approx(
        38.75
    )
    assert longitude == pytest.approx(
        -9.30
    )
    assert 1 <= zoom <= 18


def test_longer_route_uses_smaller_zoom():

    short_route_zoom = _route_view(
        [
            [
                -9.400,
                38.700,
            ],
            [
                -9.395,
                38.705,
            ],
        ]
    )[2]

    long_route_zoom = _route_view(
        [
            [
                -9.40,
                38.70,
            ],
            [
                -8.90,
                39.10,
            ],
        ]
    )[2]

    assert (
        long_route_zoom
        < short_route_zoom
    )