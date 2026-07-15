from datetime import timedelta

from performancelab.physiology.recovery import (
    heart_rate_recovery,
    is_recovered,
    recovery_days,
    recovery_score,
    training_strain,
)


# ======================================================

def test_recovery_score():

    assert recovery_score(5) == 50


# ======================================================

def test_recovery_score_limits():

    assert recovery_score(0) == 100

    assert recovery_score(10) == 0


# ======================================================

def test_recovery_days():

    assert recovery_days(2) == 0

    assert recovery_days(5) == 1

    assert recovery_days(7) == 2

    assert recovery_days(9) == 3

    assert recovery_days(10) == 4


# ======================================================

def test_heart_rate_recovery():

    assert heart_rate_recovery(

        190,

        150,

    ) == 40


# ======================================================

def test_is_recovered():

    assert is_recovered(

        3,

        2,

    ) is True

    assert is_recovered(

        1,

        2,

    ) is False


# ======================================================

def test_training_strain():

    strain = training_strain(

        timedelta(hours=1),

        7,

    )

    assert strain == 420


# ======================================================

def test_invalid_values():

    assert recovery_score(None) is None

    assert recovery_days(None) is None

    assert heart_rate_recovery(None, 150) is None

    assert is_recovered(None, 2) is None

    assert training_strain(None, 5) is None