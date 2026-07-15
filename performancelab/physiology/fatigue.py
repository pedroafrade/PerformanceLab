"""
PerformanceLab

Fatigue Physiology

Utilities for estimating fatigue.
"""


# ======================================================
# Acute : Chronic Ratio
# ======================================================

def acute_chronic_ratio(acute_load, chronic_load):

    """
    Acute : Chronic Workload Ratio (ACWR).
    """

    if (

        acute_load is None

        or chronic_load in (None, 0)

    ):

        return None

    return acute_load / chronic_load


# ======================================================
# Training Monotony
# ======================================================

def monotony(mean_load, std_load):

    """
    Foster Training Monotony.
    """

    if (

        mean_load is None

        or std_load in (None, 0)

    ):

        return None

    return mean_load / std_load


# ======================================================
# Training Strain
# ======================================================

def strain(total_load, monotony_value):

    """
    Foster Training Strain.
    """

    if (

        total_load is None

        or monotony_value is None

    ):

        return None

    return total_load * monotony_value


# ======================================================
# Fatigue Index
# ======================================================

def fatigue_index(acute_load, chronic_load):

    """
    Simple fatigue indicator.

    >1 means acute load exceeds chronic load.
    """

    return acute_chronic_ratio(

        acute_load,

        chronic_load,

    )


# ======================================================
# Freshness Score
# ======================================================

def freshness_score(fatigue):

    """
    Returns a freshness score (0–100).

    Higher is better.
    """

    if fatigue is None:

        return None

    score = 100 - fatigue * 20

    return max(0, min(100, score))


# ======================================================
# Risk Score
# ======================================================

def risk_score(acwr):

    """
    Injury risk estimate from ACWR.

    Returns:
        Low
        Moderate
        High
    """

    if acwr is None:

        return None

    if acwr < 0.8:

        return "Low"

    if acwr <= 1.3:

        return "Moderate"

    return "High"