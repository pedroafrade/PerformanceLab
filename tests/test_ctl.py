from datetime import date

from performancelab.analysis.performance.ctl import (
    ctl,
    ctl_curve,
    ctl_from_weeks,
    decay_constant,
)

from performancelab.training.weekly import WeeklySummary


# ======================================================

def test_ctl_empty():

    assert ctl([]) == 0.0


# ======================================================

def test_ctl_constant_load():

    loads = [100] * 20

    assert round(ctl(loads), 1) == 100.0


# ======================================================

def test_ctl_increasing():

    loads = [50, 60, 70, 80, 90]

    assert ctl(loads) > 50


# ======================================================

def test_ctl_curve():

    curve = ctl_curve([50, 60, 70])

    assert len(curve) == 3

    assert curve[0] == 50

    assert curve[-1] > 50
