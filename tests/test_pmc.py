from performancelab.analysis.performance.pmc import (
    PerformanceManagementChart,
)


# ======================================================

def test_empty_chart():

    pmc = PerformanceManagementChart()

    assert len(pmc) == 0

    assert pmc.current_ctl == 0

    assert pmc.current_atl == 0

    assert pmc.current_tsb == 0


# ======================================================

def test_curves():

    pmc = PerformanceManagementChart(

        [50, 60, 70, 80, 90]

    )

    assert len(pmc.ctl) == 5

    assert len(pmc.atl) == 5

    assert len(pmc.tsb) == 5


# ======================================================

def test_current_values():

    pmc = PerformanceManagementChart(

        [50, 60, 70, 80, 90]

    )

    assert pmc.current_ctl == pmc.ctl[-1]

    assert pmc.current_atl == pmc.atl[-1]

    assert pmc.current_tsb == pmc.tsb[-1]


# ======================================================

def test_aliases():

    pmc = PerformanceManagementChart(

        [50, 60, 70, 80]

    )

    assert pmc.fitness == pmc.current_ctl

    assert pmc.fatigue == pmc.current_atl

    assert pmc.form == pmc.current_tsb


# ======================================================

def test_repr():

    pmc = PerformanceManagementChart(

        [1, 2, 3]

    )

    assert "PerformanceManagementChart" in repr(pmc)

# ======================================================

def test_empty_chart_has_no_load_data():

    pmc = PerformanceManagementChart()

    assert pmc.history_days == 0
    assert pmc.has_data is False
    assert (
        pmc.has_complete_atl_window
        is False
    )
    assert (
        pmc.has_complete_ctl_window
        is False
    )


# ======================================================

def test_seven_days_complete_only_atl_window():

    pmc = PerformanceManagementChart(
        [0.0] * 7
    )

    assert pmc.history_days == 7
    assert pmc.has_data is True
    assert (
        pmc.has_complete_atl_window
        is True
    )
    assert (
        pmc.has_complete_ctl_window
        is False
    )


# ======================================================

def test_forty_two_days_complete_both_windows():

    pmc = PerformanceManagementChart(
        [0.0] * 42
    )

    assert pmc.history_days == 42
    assert pmc.has_data is True
    assert (
        pmc.has_complete_atl_window
        is True
    )
    assert (
        pmc.has_complete_ctl_window
        is True
    )