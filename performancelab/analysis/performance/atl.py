from ._ema import decay_constant, exponential_curve, exponential_load


def atl(loads, days=7):

    return exponential_load(loads, days)


def atl_curve(loads, days=7):

    return exponential_curve(loads, days)


def atl_from_weeks(weeks):

    return atl(

        [

            week.load

            for week in weeks

        ]

    )