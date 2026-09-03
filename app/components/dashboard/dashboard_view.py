"""
PerformanceLab

Streamlit dashboard view.
"""

import streamlit as st
from datetime import datetime
from performancelab.presentation.recent_activity_summary import recent_activity_summary

from performancelab.presentation import (
    DashboardData,
    has_route,
)

from .cards import (
    next_workout_card,
    show_athlete_overview_card,
    show_performance_management_card,
    show_planning_card,
    show_training_summary_card,
)
from .cards.latest_activity_card import (
    latest_activity_card,
)
from .cards.next_event_card import (
    next_event_card,
)
from .cards.recovery_card import (
    recovery_card,
)
from .cards.training_load_card import (
    training_load_card,
)
from .event_manager import (
    open_event_manager,
)
from .grid import (
    dashboard_row,
)
from .widget import (
    DashboardAction,
    dashboard_widget,
)
from ..route_map import (
    show_route_map,
)


FIRST_ROW_HEIGHT = 277


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
    summary = dashboard_data["summary"]
    planning = dashboard_data["planning"]
    next_event = dashboard_data["next_event"]
    recovery = dashboard_data["recovery"]
    training_load = dashboard_data["training_load"]
    reference_time = datetime.now().astimezone()
    recent_summary = recent_activity_summary(athlete.history, reference_time.date())
    current_state = athlete.analytics.training_state_at(reference_time=reference_time)

    activity_col, planning_col, event_col = (
        dashboard_row(
            (1, 3.2, 1),
        )
    )

    with activity_col:

        with dashboard_widget(
            title="Latest Activity",
            icon=":material/history:",
            divider=False,
            height=FIRST_ROW_HEIGHT,
        ):

            latest_activity_card(
                latest_activity,
            )

    with planning_col:

        with dashboard_widget(
            title="Weekly Plan",
            center_text=(
                f"{planning.weekly_plan.start_date:%d %b} – "
                f"{planning.weekly_plan.end_date:%d %b}"
            ),
            icon=":material/calendar_view_week:",
            divider=False,
            height=FIRST_ROW_HEIGHT,
        ):

            show_planning_card(
                planning,
            )

    with event_col:

        with dashboard_widget(
            title="Next Event",
            icon=":material/event:",
            divider=False,
            height=FIRST_ROW_HEIGHT,
            action=DashboardAction(
                label="Manage Events",
                key="next-event-action",
                callback=lambda: open_event_manager(
                    athlete,
                ),
            ),
        ):

            next_event_card(
                next_event,
            )

    (
        physiology_col,
        workout_col,
        summary_col,
        status_col,
        recovery_col,
        load_col,
    ) = dashboard_row(
        (
            1.7,
            1.6,
            1,
            1,
            1,
            1,
        ),
    )

    with physiology_col:

        with dashboard_widget(
            title="Physiology",
            icon=":material/ecg_heart:",
            divider=False,
        ):

            show_athlete_overview_card(
                physiology,
            )

    with workout_col:

        with dashboard_widget(
            title="Next Workout",
            icon=":material/fitness_center:",
            divider=False,
        ):

            next_workout_card(
                planning.next_workout,
            )

    with summary_col:

        with dashboard_widget(
            title="Training Summary",
            icon=":material/calendar_month:",
            divider=False,
        ):

            show_training_summary_card(
                recent_summary,
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
            title="Estimated Recovery",
            icon=":material/favorite:",
            divider=False,
        ):

            recovery_card(
                recovery,
                current_state=current_state,
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

    return None


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
