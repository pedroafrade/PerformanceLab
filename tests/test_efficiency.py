from performancelab.physiology.efficiency import (
    efficiency_factor,
    normalized_efficiency,
    power_per_heart_rate,
    speed_per_heart_rate,
    speed_per_watt,
    vertical_speed,
)


# ======================================================

def test_speed_per_heart_rate():

    assert speed_per_heart_rate(

        15,

        150,

    ) == 0.1


# ======================================================

def test_power_per_heart_rate():

    assert power_per_heart_rate(

        300,

        150,

    ) == 2


# ======================================================

def test_speed_per_watt():

    assert speed_per_watt(

        36,

        300,

    ) == 0.12


# ======================================================

def test_vertical_speed():

    assert vertical_speed(

        900,

        3,

    ) == 300


# ======================================================

def test_efficiency_factor():

    assert efficiency_factor(

        280,

        140,

    ) == 2


# ======================================================

def test_normalized_efficiency():

    assert normalized_efficiency(

        90,

        100,

    ) == 90


# ======================================================

def test_invalid_values():

    assert speed_per_heart_rate(None, 150) is None

    assert power_per_heart_rate(None, 150) is None

    assert speed_per_watt(None, 300) is None

    assert vertical_speed(None, 2) is None

    assert efficiency_factor(None, 140) is None

    assert normalized_efficiency(None, 100) is None