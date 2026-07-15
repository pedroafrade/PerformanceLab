from ._ema import decay_constant, exponential_curve, exponential_load


def ctl(loads, days=42):

    return exponential_load(loads, days)


def ctl_curve(loads, days=42):

    return exponential_curve(loads, days)


def ctl_from_weeks(weeks):

    return ctl(

        [

            week.load

            for week in weeks

        ]

    )