"""
PerformanceLab

Power Physiology

Utilities for power calculations.
"""


# ======================================================
# Relative Power
# ======================================================

def relative_power(power, weight):

    if power is None or weight in (None, 0):

        return None

    return power / weight


# ======================================================
# Percentage of FTP
# ======================================================

def percent_ftp(power, ftp):

    if power is None or ftp in (None, 0):

        return None

    return (power / ftp) * 100


# ======================================================
# Functional Threshold Power from W/kg
# ======================================================

def ftp_from_relative(relative, weight):

    if relative is None or weight is None:

        return None

    return relative * weight


# ======================================================
# Average Power
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


# ======================================================
# Peak Power
# ======================================================

def peak(values):

    values = [

        value

        for value in values

        if value is not None

    ]

    if not values:

        return None

    return max(values)


# ======================================================
# Minimum Power
# ======================================================

def minimum(values):

    values = [

        value

        for value in values

        if value is not None

    ]

    if not values:

        return None

    return min(values)