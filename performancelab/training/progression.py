"""
PerformanceLab

Training Progression

Utilities for comparing two training periods.
"""


# ======================================================
# Generic progression
# ======================================================

def progression(previous, current):

    if previous is None or current is None:

        return None

    if previous == 0:

        return None

    return (current - previous) / previous * 100


# ======================================================
# Distance
# ======================================================

def distance_progression(previous, current):

    return progression(

        previous.total_distance,

        current.total_distance,

    )


# ======================================================
# Duration
# ======================================================

def duration_progression(previous, current):

    return progression(

        previous.total_duration.total_seconds(),

        current.total_duration.total_seconds(),

    )


# ======================================================
# Elevation
# ======================================================

def elevation_progression(previous, current):

    return progression(

        previous.total_elevation,

        current.total_elevation,

    )


# ======================================================
# Load
# ======================================================

def load_progression(previous, current):

    return progression(

        previous.load,

        current.load,

    )