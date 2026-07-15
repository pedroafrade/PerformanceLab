from performancelab.physiology.fatigue import (
    acute_chronic_ratio,
    fatigue_index,
    freshness_score,
    monotony,
    risk_score,
    strain,
)


# ======================================================

def test_acwr():

    assert acute_chronic_ratio(

        600,

        500,

    ) == 1.2


# ======================================================

def test_monotony():

    assert monotony(

        80,

        20,

    ) == 4


# ======================================================

def test_strain():

    assert strain(

        600,

        2,

    ) == 1200


# ======================================================

def test_fatigue_index():

    assert fatigue_index(

        700,

        500,

    ) == 1.4


# ======================================================

def test_freshness_score():

    assert freshness_score(2) == 60


# ======================================================

def test_risk_score():

    assert risk_score(0.7) == "Low"

    assert risk_score(1.1) == "Moderate"

    assert risk_score(1.6) == "High"


# ======================================================

def test_invalid_values():

    assert acute_chronic_ratio(None, 10) is None

    assert monotony(None, 10) is None

    assert strain(None, 2) is None

    assert fatigue_index(None, 10) is None

    assert freshness_score(None) is None

    assert risk_score(None) is None