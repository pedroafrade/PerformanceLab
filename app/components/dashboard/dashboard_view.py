"""
PerformanceLab

Streamlit dashboard view.
"""

import streamlit as st

from performancelab.presentation import (
    DashboardData,
    has_route,
)
from performancelab.presentation.dashboard_models import (
    RecoveryCardData,
)

from .cards import (
    show_athlete_overview_card,
    show_performance_chart_card,
    show_performance_management_card,
    show_planning_card,
    show_training_summary_card,
    show_workout_history_card,
)
from .cards.recovery_card import recovery_card
from .grid import (
    dashboard_bottom_row,
    dashboard_row,
    dashboard_top_row,
)
from .widget import dashboard_widget
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
    """

    dashboard_data = DashboardData(
        athlete,
    ).build()

    athlete_data = dashboard_data["athlete"]
    summary = dashboard_data["summary"]
    performance = dashboard_data["performance"]
    planning = dashboard_data["planning"]

    recovery = RecoveryCardData(
        score=82,
        status="Good",
        recommendation=(
            "Ready for a normal training session."
        ),
        trend="↑ 4%",
    )

    # ==================================================
    # Header
    # ==================================================

    st.set_page_config(
        layout="wide",
    )

    # ==================================================
    # First row
    # ==================================================

    left, right = dashboard_top_row()

    with left:

        with dashboard_widget(
            title="Athlete",
            icon="🏃",
        ):

            show_athlete_overview_card(
                athlete_data,
            )

    with right:

        (
            summary_col,
            status_col,
            recovery_col,
        ) = dashboard_row(
            (1, 1, 1),
        )

        with summary_col:

            with dashboard_widget(
                title="This Week",
                icon="📅",
            ):

                show_training_summary_card(
                    summary,
                )

        with status_col:

            with dashboard_widget(
                title="Current Status",
                icon="📊",
            ):

                show_performance_management_card(
                    summary,
                )

        with recovery_col:

            with dashboard_widget(
                title="Recovery",
                icon="💚",
                subtitle="Readiness today",
            ):

                recovery_card(
                    recovery,
                )

    # ==================================================
    # Performance
    # ==================================================

    with dashboard_widget(
        title="Performance",
        icon="📈",
    ):

        show_performance_chart_card(
            performance,
        )

    # ==================================================
    # Bottom row
    # ==================================================

    left, right = dashboard_bottom_row()

    with left:

        with dashboard_widget(
            title="Planning",
            icon="🎯",
        ):

            show_planning_card(
                planning,
            )

    with right:

        with dashboard_widget(
            title="Workout History",
            icon="🕘",
        ):

            selected_workout = (
                show_workout_history_card(
                    athlete,
                )
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