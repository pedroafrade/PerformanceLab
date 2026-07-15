from performancelab.physiology.cadence import (
    average,
    cadence_reserve,
    maximum,
    minimum,
    percent_maximum,
    recommended_cycling,
    recommended_running,
)


# ======================================================

def test_average():

    assert average(

        [170, 175, 180]

    ) == 175


# ======================================================

def test_maximum():

    assert maximum(

        [170, 182, 176]

    ) == 182


# ======================================================

def test_minimum():

    assert minimum(

        [170, 182, 176]

    ) == 170


# ======================================================

def test_cadence_reserve():

    assert cadence_reserve(

        190,

        175,

    ) == 15


# ======================================================

def test_percent_maximum():

    assert percent_maximum(

        180,

        200,

    ) == 90


# ======================================================

def test_running_range():

    assert recommended_running() == (

        170,

        190,

    )


# ======================================================

def test_cycling_range():

    assert recommended_cycling() == (

        80,

        100,

    )


# ======================================================

def test_invalid_values():

    assert average([]) is None

    assert maximum([]) is None

    assert minimum([]) is None

    assert cadence_reserve(None, 170) is None

    assert percent_maximum(None, 190) is None