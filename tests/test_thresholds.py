from performancelab.physiology.thresholds import (
    aerobic_threshold,
    anaerobic_threshold,
    lthr,
    threshold_pace,
    threshold_power,
    threshold_speed,
)


# ======================================================

def test_lthr():

    assert lthr(190) == 171


# ======================================================

def test_aerobic_threshold():

    assert aerobic_threshold(190) == 152


# ======================================================

def test_anaerobic_threshold():

    assert anaerobic_threshold(190) == 171


# ======================================================

def test_threshold_speed():

    speed = threshold_speed(

        10,

        1,

    )

    assert speed == 10


# ======================================================

def test_threshold_pace():

    pace = threshold_pace(

        10,

        1,

    )

    assert pace == 0.1


# ======================================================

def test_threshold_power():

    assert threshold_power(285) == 285


# ======================================================

def test_invalid_values():

    assert lthr(None) is None

    assert aerobic_threshold(None) is None

    assert anaerobic_threshold(None) is None

    assert threshold_speed(None, 1) is None

    assert threshold_speed(10, 0) is None

    assert threshold_pace(None, 1) is None

    assert threshold_pace(10, 0) is None