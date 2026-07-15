from performancelab.analysis.performance.ctl import (
    ctl,
    ctl_curve,
)


# ======================================================

def test_ctl_empty():

    assert ctl([]) == 0.0


# ======================================================

def test_ctl_constant_load():

    loads = [100] * 20

    value = ctl(loads)

    assert 0 < value < 100

    assert round(value, 1) == 37.9


# ======================================================

def test_ctl_increasing():

    loads = [50, 60, 70, 80, 90]

    value = ctl(loads)

    assert value > 0

    assert value < 90


# ======================================================

def test_ctl_curve():

    curve = ctl_curve([50, 60, 70])

    assert len(curve) == 3

    assert 0 < curve[0] < 50

    assert curve[1] > curve[0]

    assert curve[2] > curve[1]