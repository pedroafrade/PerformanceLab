from datetime import timedelta

from performancelab.physiology.pace import (
    average,
    duration,
    fastest,
    pace,
    pace_from_speed,
    round_pace,
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

def test_round_pace_to_five_seconds():

    assert round_pace(
        5 + 12 / 60
    ) == 5 + 10 / 60

    assert round_pace(
        5 + 13 / 60
    ) == 5 + 15 / 60

    assert round_pace(
        4 + 57 / 60
    ) == 4 + 55 / 60

    assert round_pace(
        4 + 58 / 60
    ) == 5


# ======================================================

def test_round_pace_custom_interval():

    assert round_pace(
        5 + 7 / 60,
        interval_seconds=10,
    ) == 5 + 10 / 60


# ======================================================

def test_round_pace_rejects_invalid_values():

    assert round_pace(None) is None
    assert round_pace(0) is None

    assert round_pace(
        5,
        interval_seconds=0,
    ) is None
    
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