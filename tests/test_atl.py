from performancelab.analysis.performance.atl import (
    atl,
    atl_curve,
)


# ======================================================

def test_atl_empty():

    assert atl([]) == 0.0


# ======================================================

def test_atl_constant_load():

    loads = [100] * 20

    value = atl(loads)

    assert 0 < value < 100

    assert round(value, 1) == 94.3


# ======================================================

def test_atl_increasing():

    loads = [50, 60, 70, 80, 90]

    value = atl(loads)

    assert value > 0

    assert value < 90


# ======================================================

def test_atl_curve():

    curve = atl_curve([50, 60, 70])

    assert len(curve) == 3

    assert 0 < curve[0] < 50

    assert curve[1] > curve[0]

    assert curve[2] > curve[1]