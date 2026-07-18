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
)
from .cards.latest_activity_card import (
    latest_activity_card,
)
from .cards.recovery_card import recovery_card
from .cards.training_load_card import (
    training_load_card,
)
from .cards.monthly_summary_card import (
    monthly_summary_card,
)
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

    latest_activity = dashboard_data["latest_activity"]
    physiology = dashboard_data["physiology"]
    monthly_summary = dashboard_data["monthly_summary"]
    summary = dashboard_data["summary"]
    performance = dashboard_data["performance"]
    planning = dashboard_data["planning"]

    recovery = dashboard_data["recovery"]
    training_load = dashboard_data["training_load"]

    # ==================================================
    # Activity and planning strip
    # ==================================================

    activity_col, planning_col, goal_col = (
        dashboard_row(
            (1.1, 2.5, 1.2),
        )
    )

    with activity_col:

        with dashboard_widget(
            title="Latest Activity",
            icon=":material/history:",
            divider=False,
        ):

            latest_activity_card(
                latest_activity,
            )

    with planning_col:

        with dashboard_widget(
            title="Weekly Plan",
            icon=":material/calendar_view_week:",
            divider=False,
        ):

            st.caption(
                "Weekly plan will be added next."
            )

    with goal_col:

        with dashboard_widget(
            title="Next Goal",
            icon=":material/flag:",
            divider=False,
        ):

            st.caption(
                "Goal progress will be added next."
            )

    # ==================================================
    # Top row
    # ==================================================

    left, right = dashboard_top_row()

    with left:

        with dashboard_widget(
            title="Physiology",
            icon=":material/ecg_heart:",
            divider=False,
        ):

            show_athlete_overview_card(
                physiology,
            )

    with right:

        (
            summary_col,
            status_col,
            recovery_col,
            load_col,
        ) = dashboard_row(
            (1, 1, 1, 1),
        )

        with summary_col:

            with dashboard_widget(
                title="This Week",
                icon=":material/calendar_month:",
                divider=False,
            ):

                show_training_summary_card(
                    summary,
                )

        with status_col:

            with dashboard_widget(
                title="Performance Status",
                icon=":material/monitoring:",
                divider=False,
            ):

                show_performance_management_card(
                    summary,
                )

        with recovery_col:

            with dashboard_widget(
                title="Recovery",
                icon=":material/favorite:",
                divider=False,
            ):

                recovery_card(
                    recovery,
                )

        with load_col:

            with dashboard_widget(
                title="Training Load",
                icon=":material/monitoring:",
                divider=False,
            ):

                training_load_card(
                    training_load,
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
            title="Monthly Summary",
            icon=":material/assessment:",
            divider=False,
        ):

            monthly_summary_card(
                monthly_summary,
            )

    return None


# ======================================================
# Selected workout route
# ======================================================

def show_selected_workout_route(
    selected_workout,
) -> None:
    """
    Displays the selected workout route when available.
    """

    if selected_workout is None:
        return

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
            "The selected workout has no route."
        )