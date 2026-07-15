from performancelab.physiology.heartrate import (
    average,
    heart_rate_reserve,
    karvonen,
    percent_hrr,
    percent_max_hr,
)


# ======================================================

def test_heart_rate_reserve():

    assert heart_rate_reserve(190, 50) == 140


# ======================================================

def test_percent_max_hr():

    assert percent_max_hr(152, 190) == 80


# ======================================================

def test_percent_hrr():

    value = percent_hrr(

        162,

        190,

        50,

    )

    assert round(value, 1) == 80.0


# ======================================================

def test_karvonen():

    target = karvonen(

        80,

        190,

        50,

    )

    assert target == 162


# ======================================================

def test_average():

    assert average(

        [140, 150, 160]

    ) == 150


# ======================================================

def test_average_ignores_none():

    assert average(

        [140, None, 160]

    ) == 150


# ======================================================

def test_average_empty():

    assert average([]) is None


# ======================================================

def test_invalid_values():

    assert heart_rate_reserve(None, 50) is None

    assert percent_max_hr(None, 190) is None

    assert percent_hrr(None, 190, 50) is None

    assert karvonen(80, None, 50) is None