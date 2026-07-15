from performancelab.physiology.power import (
    average,
    ftp_from_relative,
    minimum,
    peak,
    percent_ftp,
    relative_power,
)


# ======================================================

def test_relative_power():

    assert relative_power(

        280,

        70,

    ) == 4.0


# ======================================================

def test_percent_ftp():

    assert percent_ftp(

        240,

        300,

    ) == 80


# ======================================================

def test_ftp_from_relative():

    assert ftp_from_relative(

        4.0,

        70,

    ) == 280


# ======================================================

def test_average():

    assert average(

        [200, 220, 240]

    ) == 220


# ======================================================

def test_peak():

    assert peak(

        [180, 400, 250]

    ) == 400


# ======================================================

def test_minimum():

    assert minimum(

        [180, 400, 250]

    ) == 180


# ======================================================

def test_average_ignores_none():

    assert average(

        [200, None, 240]

    ) == 220


# ======================================================

def test_average_empty():

    assert average([]) is None


# ======================================================

def test_invalid_values():

    assert relative_power(

        None,

        70,

    ) is None

    assert relative_power(

        250,

        0,

    ) is None

    assert percent_ftp(

        None,

        300,

    ) is None

    assert percent_ftp(

        250,

        0,

    ) is None