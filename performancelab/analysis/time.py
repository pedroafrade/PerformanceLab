"""
PerformanceLab

Time Analytics

Utilities for analysing workouts over time.
"""

from datetime import date, datetime, timedelta


# ======================================================
# Date normalization
# ======================================================

def _calendar_date(value):

    if isinstance(value, datetime):

        return value.date()

    return value


# ======================================================
# Workouts between two dates
# ======================================================

def workouts_between(history, start_date, end_date):

    start = _calendar_date(start_date)
    end = _calendar_date(end_date)

    return [

        workout

        for workout in history

        if (
            workout.date is not None
            and start
            <= _calendar_date(workout.date)
            <= end
        )

    ]


# ======================================================
# Distance between two dates
# ======================================================

def distance_between(history, start_date, end_date):

    return sum(

        workout.distance or 0

        for workout in workouts_between(

            history,

            start_date,

            end_date,

        )

    )


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

        if workout.duration is not None:

            total += workout.duration

    return total


# ======================================================
# Elevation between two dates
# ======================================================

def elevation_between(history, start_date, end_date):

    return sum(

        workout.elevation_gain or 0

        for workout in workouts_between(

            history,

            start_date,

            end_date,

        )

    )


# ======================================================
# Average RPE between two dates
# ======================================================

def average_rpe_between(history, start_date, end_date):

    values = [

        workout.feedback.rpe

        for workout in workouts_between(

            history,

            start_date,

            end_date,

        )

        if workout.feedback.rpe is not None

    ]

    if not values:

        return None

    return sum(values) / len(values)


# ======================================================
# Number of training days between two dates
# ======================================================

def training_days_between(history, start_date, end_date):

    return len({

        _calendar_date(workout.date)

        for workout in workouts_between(

            history,

            start_date,

            end_date,

        )

        if workout.date is not None

    })


# ======================================================
# Number of training days
# ======================================================

def training_days(history):

    return len({

        _calendar_date(workout.date)

        for workout in history

        if workout.date is not None

    })


# ======================================================
# First training date
# ======================================================

def first_training_date(history):

    dates = [

        _calendar_date(workout.date)

        for workout in history

        if workout.date is not None

    ]

    if not dates:

        return None

    return min(dates)


# ======================================================
# Last training date
# ======================================================

def last_training_date(history):

    dates = [

        _calendar_date(workout.date)

        for workout in history

        if workout.date is not None

    ]

    if not dates:

        return None

    return max(dates)