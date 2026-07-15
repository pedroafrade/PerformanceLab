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

    return (

        (current - previous)

        / previous

        * 100

    )


# ======================================================
# Distance by sport
# ======================================================

def distance_progression(previous, current, sport):

    return progression(

        previous.distance_for(sport),

        current.distance_for(sport),

    )


# ======================================================
# Duration by sport
# ======================================================

def duration_progression(previous, current, sport):

    previous_duration = previous.duration_for(

        sport,

    )

    current_duration = current.duration_for(

        sport,

    )

    return progression(

        previous_duration.total_seconds(),

        current_duration.total_seconds(),

    )


# ======================================================
# Elevation by sport
# ======================================================

def elevation_progression(previous, current, sport):

    return progression(

        previous.elevation_for(sport),

        current.elevation_for(sport),

    )


# ======================================================
# Combined physiological load
# ======================================================

def load_progression(previous, current):

    return progression(

        previous.load,

        current.load,

    )