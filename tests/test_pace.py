from datetime import timedelta

from performancelab.physiology.pace import (
    average,
    duration,
    fastest,
    pace,
    pace_from_speed,
    slowest,
    speed,
    speed_from_pace,
)


# ======================================================

def test_speed():

    assert speed(

        10,

        timedelta(hours=1),

    ) == 10


# ======================================================

def test_pace():

    assert pace(

        10,

        timedelta(minutes=50),

    ) == 5


# ======================================================

def test_duration():

    assert duration(

        10,

        5,

    ) == timedelta(minutes=50)


# ======================================================

def test_pace_from_speed():

    assert pace_from_speed(12) == 5


# ======================================================

def test_speed_from_pace():

    assert speed_from_pace(5) == 12


# ======================================================

def test_fastest():

    assert fastest(

        [5.5, 4.8, 6.0]

    ) == 4.8


# ======================================================

def test_slowest():

    assert slowest(

        [5.5, 4.8, 6.0]

    ) == 6.0


# ======================================================

def test_average():

    assert average(

        [5, 6, 4]

    ) == 5


# ======================================================

def test_invalid_values():

    assert speed(

        None,

        timedelta(hours=1),

    ) is None

    assert pace(

        None,

        timedelta(hours=1),

    ) is None

    assert duration(

        None,

        5,

    ) is None

    assert pace_from_speed(None) is None

    assert speed_from_pace(None) is None