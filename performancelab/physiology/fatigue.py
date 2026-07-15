"""
PerformanceLab

Fatigue Physiology

Utilities for simple workload and fatigue indicators.
"""


# ======================================================
# Acute : Chronic Ratio
# ======================================================

def acute_chronic_ratio(
    acute_load: float | None,
    chronic_load: float | None,
) -> float | None:

    """
    Calculates the acute-to-chronic workload ratio.

    This ratio describes the relationship between acute
    and chronic load. It should not be interpreted alone
    as an injury-risk prediction.
    """

    if acute_load is None or chronic_load is None:

        return None

    if acute_load < 0 or chronic_load <= 0:

        return None

    return acute_load / chronic_load


# ======================================================
# Training Monotony
# ======================================================

def monotony(
    mean_load: float | None,
    std_load: float | None,
) -> float | None:

    """
    Calculates Foster training monotony.

    Monotony = mean daily load / standard deviation
    of daily load.
    """

    if mean_load is None or std_load is None:

        return None

    if mean_load < 0 or std_load <= 0:

        return None

    return mean_load / std_load


# ======================================================
# Training Strain
# ======================================================

def strain(
    total_load: float | None,
    monotony_value: float | None,
) -> float | None:

    """
    Calculates Foster training strain.

    Strain = total weekly load × training monotony.
    """

    if total_load is None or monotony_value is None:

        return None

    if total_load < 0 or monotony_value < 0:

        return None

    return total_load * monotony_value


# ======================================================
# Fatigue Index
# ======================================================

def fatigue_index(
    acute_load: float | None,
    chronic_load: float | None,
) -> float | None:

    """
    Returns a simple acute-to-chronic fatigue indicator.

    Values above 1 mean that acute load exceeds
    chronic load.
    """

    return acute_chronic_ratio(

        acute_load,

        chronic_load,

    )


# ======================================================
# Freshness Score
# ======================================================

def freshness_score(
    fatigue: float | None,
) -> float | None:

    """
    Converts a fatigue indicator into a heuristic score.

    Returns a value between 0 and 100.

    This is a simple presentation score, not a validated
    physiological measure of readiness or recovery.
    """

    if fatigue is None or fatigue < 0:

        return None

    score = 100 - fatigue * 20

    return max(

        0,

        min(100, score),

    )


# ======================================================
# Workload Ratio Band
# ======================================================

def risk_score(
    acwr: float | None,
) -> str | None:

    """
    Returns a simple workload-ratio classification.

    The returned label is only a heuristic description
    of the ratio and must not be interpreted as an
    individualized injury-risk prediction.

    Returns:
        Low
        Moderate
        High
    """

    if acwr is None or acwr < 0:

        return None

    if acwr < 0.8:

        return "Low"

    if acwr <= 1.3:

        return "Moderate"

    return "High"