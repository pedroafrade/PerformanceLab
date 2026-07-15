from performancelab.physiology.vo2max import (
    oxygen_cost,
    relative_intensity,
    running_economy,
    vdot,
    vo2_reserve,
    vo2max_from_cooper,
    vo2max_from_speed,
)


# ======================================================

def test_cooper():

    value = vo2max_from_cooper(3000)

    assert round(value, 1) == 55.8


# ======================================================

def test_speed():

    value = vo2max_from_speed(12)

    assert round(value, 1) == 43.5


# ======================================================

def test_oxygen_cost():

    assert oxygen_cost(12) == vo2max_from_speed(12)


# ======================================================

def test_running_economy():

    value = running_economy(

        12,

        43.5,

    )

    assert round(value, 1) == 217.5


# ======================================================

def test_vdot():

    assert round(vdot(12), 1) == 43.5


# ======================================================

def test_relative_intensity():

    assert relative_intensity(

        40,

        50,

    ) == 80


# ======================================================

def test_vo2_reserve():

    assert vo2_reserve(55) == 51.5


# ======================================================

def test_invalid():

    assert vo2max_from_cooper(None) is None

    assert vo2max_from_speed(None) is None

    assert running_economy(None, 40) is None

    assert relative_intensity(None, 50) is None

    assert vo2_reserve(None) is None