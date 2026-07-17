"""
PerformanceLab

Streamlit dashboard view.
"""

import streamlit as st

from performancelab.presentation import (
    DashboardData,
    has_route,
)

from .cards import (
    show_athlete_overview_card,
    show_performance_chart_card,
    show_performance_management_card,
    show_planning_card,
    show_training_summary_card,
    show_workout_history_card,
)

from ..route_map import (
    show_route_map,
)


# ======================================================
# Dashboard
# ======================================================

def show_dashboard(
    athlete,
):
    """
    Displays the main athlete dashboard.

    Parameters
    ----------
    athlete
        Athlete displayed by the application.

    Returns
    -------
    Workout | None
        Workout selected in the history table.
    """

    dashboard_data = DashboardData(
        athlete,
    ).build()

    summary = dashboard_data["summary"]
    performance = dashboard_data["performance"]
    planning = dashboard_data["planning"]

    # ==================================================
    # Header
    # ==================================================

    st.title("PerformanceLab")

    st.caption(
        "Training, physiology and performance analytics."
    )

    show_athlete_overview_card(
        dashboard_data,
    )

    show_training_summary_card(
        summary,
    )

    show_performance_management_card(
        summary,
    )

    show_performance_chart_card(
        performance,
    )

    show_planning_card(
        planning,
    )

    selected_workout = show_workout_history_card(
        athlete,
    )

    return selected_workout


# ======================================================
# Selected workout route
# ======================================================

def show_selected_workout_route(
    selected_workout,
) -> None:
    """
    Displays the selected workout route when available.
    """

    if has_route(
        selected_workout
    ):

        st.markdown(
            "#### Route"
        )

        show_route_map(
            selected_workout
        )

    else:

        st.info(
            "No workout is available "
            "for inspection."
        )