from performancelab.physiology.zones import (
    heart_rate_zones,
    pace_zones,
    power_zones,
    zone,
)


# ======================================================

def test_hr_zones():

    zones = heart_rate_zones(

        190,

        50,

    )

    assert "Z1" in zones

    assert "Z5" in zones


# ======================================================

def test_power_zones():

    zones = power_zones(300)

    assert zones["Z2"] == (

        165,

        225,

    )


# ======================================================

def test_pace_zones():

    zones = pace_zones(5)

    assert zones["Z4"] == (

        5.25,

        5,

    )


# ======================================================

def test_zone_lookup():

    zones = power_zones(300)

    assert zone(

        200,

        zones,

    ) == "Z2"


# ======================================================

def test_invalid_values():

    assert heart_rate_zones(None, 50) is None

    assert power_zones(None) is None

    assert pace_zones(None) is None

    assert zone(None, {}) is None

    assert zone(100, None) is None