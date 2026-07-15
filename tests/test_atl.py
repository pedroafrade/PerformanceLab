from datetime import date

from performancelab.analysis.performance.atl import (
    atl,
    atl_curve,
    atl_from_weeks,
    decay_constant,
)

from performancelab.training.weekly import WeeklySummary



# ======================================================

def test_atl_empty():

    assert atl([]) == 0.0


# ======================================================

def test_atl_constant_load():

    loads = [100] * 20

    assert round(atl(loads), 1) == 100.0


# ======================================================

def test_atl_increasing():

    loads = [50, 60, 70, 80, 90]

    assert atl(loads) > 50


# ======================================================

def test_atl_curve():

    curve = atl_curve([50, 60, 70])

    assert len(curve) == 3

    assert curve[0] == 50

    assert curve[-1] > 50
