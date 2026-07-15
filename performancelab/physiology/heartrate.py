"""
PerformanceLab

Heart Rate Physiology

Utilities for heart rate calculations.
"""


# ======================================================
# Heart Rate Reserve
# ======================================================

def heart_rate_reserve(max_hr, resting_hr):

    if max_hr is None or resting_hr is None:

        return None

    return max_hr - resting_hr


# ======================================================
# Percentage of Maximum Heart Rate
# ======================================================

def percent_max_hr(hr, max_hr):

    if hr is None or max_hr in (None, 0):

        return None

    return (hr / max_hr) * 100


# ======================================================
# Percentage of Heart Rate Reserve (Karvonen)
# ======================================================

def percent_hrr(hr, max_hr, resting_hr):

    reserve = heart_rate_reserve(

        max_hr,

        resting_hr,

    )

    if hr is None or reserve in (None, 0):

        return None

    return (

        (hr - resting_hr)

        / reserve

    ) * 100


# ======================================================
# Karvonen Target Heart Rate
# ======================================================

def karvonen(percent, max_hr, resting_hr):

    reserve = heart_rate_reserve(

        max_hr,

        resting_hr,

    )

    if reserve is None:

        return None

    return resting_hr + (

        reserve * percent / 100

    )


# ======================================================
# Average Heart Rate
# ======================================================

def average(values):

    values = [

        value

        for value in values

        if value is not None

    ]

    if not values:

        return None

    return sum(values) / len(values)