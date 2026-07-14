"""
PerformanceLab

Time Analytics

Utilities for analysing workouts over time.
"""

from datetime import timedelta


# ======================================================
# Workouts between two dates
# ======================================================

def workouts_between(history, start_date, end_date):

    return [

        workout

        for workout in history

        if (
        workout.info.date is not None
        and start_date <= workout.info.date <= end_date
        )

    ]


# ======================================================
# Distance between two dates
# ======================================================

def distance_between(history, start_date, end_date):

    total = 0.0

    for workout in workouts_between(

        history,

        start_date,

        end_date,

    ):

        distance = getattr(

            workout.info,

            "distance",

            None,

        )

        if distance is not None:

            total += distance

    return total


# ======================================================
# Duration between two dates
# ======================================================

def duration_between(history, start_date, end_date):

    total = timedelta()

    for workout in workouts_between(

        history,

        start_date,

        end_date,

    ):

        duration = getattr(

            workout.info,

            "duration",

            None,

        )

        if duration is not None:

            total += duration

    return total


# ======================================================
# Elevation between two dates
# ======================================================

def elevation_between(history, start_date, end_date):

    total = 0.0

    for workout in workouts_between(

        history,

        start_date,

        end_date,

    ):

        elevation = getattr(

            workout.info,

            "elevation_gain",

            None,

        )

        if elevation is not None:

            total += elevation

    return total


# ======================================================
# Average RPE between two dates
# ======================================================

def average_rpe_between(history, start_date, end_date):

    values = []

    for workout in workouts_between(

        history,

        start_date,

        end_date,

    ):

        rpe = getattr(

            workout.feedback,

            "rpe",

            None,

        )

        if rpe is not None:

            values.append(rpe)

    if not values:

        return None

    return sum(values) / len(values)


# ======================================================
# Number of training days
# ======================================================

def training_days_between(history, start_date, end_date):

    return len({

        workout.info.date

        for workout in workouts_between(

          history,

          start_date,

         end_date,

        )

         if workout.info.date is not None

    })

# ======================================================
# Number of training days
# ======================================================

def training_days(history):

    return len({

        workout.info.date

        for workout in history

        if workout.info.date is not None

    })


# ======================================================
# First training date
# ======================================================

def first_training_date(history):

    dates = [

        workout.info.date

        for workout in history

        if workout.info.date is not None

    ]

    if not dates:

        return None

    return min(dates)


# ======================================================
# Last training date
# ======================================================

def last_training_date(history):

    dates = [

        workout.info.date

        for workout in history

        if workout.info.date is not None

    ]

    if not dates:

        return None

    return max(dates)