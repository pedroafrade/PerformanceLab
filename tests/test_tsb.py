from performancelab.analysis.performance.tsb import (
    fatigue,
    form,
    training_stress_balance,
    tsb,
    tsb_curve,
)


# ======================================================

def test_training_stress_balance():

    assert training_stress_balance(80, 60) == 20


# ======================================================

def test_tsb_alias():

    assert tsb(100, 90) == 10


# ======================================================

def test_form():

    assert form(75, 60) == 15


# ======================================================

def test_fatigue():

    assert fatigue(75, 100) == 25


# ======================================================

def test_tsb_curve():

    curve = tsb_curve(

        [50, 60, 70, 80, 90]

    )

    assert len(curve) == 5

    assert isinstance(curve[-1], float)