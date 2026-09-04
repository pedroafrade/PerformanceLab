"""
PerformanceLab

Streamlit dashboard view.
"""

import streamlit as st
from datetime import datetime, timezone

from performancelab.presentation import (
    DashboardData,
    ActivitiesPresenter,
    CalendarPresenter,
    TodayPresenter,
    has_route,
)

from .cards import (
    next_workout_card,
    show_planning_card,
)
from .cards.latest_activity_card import (
    latest_activity_card,
)
from .cards.next_event_card import (
    next_event_card,
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
from ..current_state_summary import (
    CurrentStateSummaryData,
    current_state_summary_html,
    current_state_summary_styles,
)


def _daily_brief_metadata(resolution) -> str | None:
    """Return safe, human-readable generation metadata for the card."""

    if resolution is None:
        return None
    generated_at = getattr(resolution, "generated_at", None)
    if not isinstance(generated_at, str) or not generated_at.strip():
        return None
    try:
        instant = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=timezone.utc)
        instant = instant.astimezone(timezone.utc)
    except ValueError:
        return None

    reasons = {
        "daily_or_context_refresh": "Daily or context refresh",
    }
    reason = reasons.get(getattr(resolution, "reason", None), "Daily update")
    status = getattr(resolution, "status", None)
    state = "Reused" if status == "cached" else "Updated"
    return f"{state} {instant:%d %b %Y · %H:%M} UTC · {reason}"


def show_dashboard(
    athlete,
    *,
    daily_brief_resolution=None,
):
    """Keep the dashboard within the reference desktop viewport."""
    st.html("""<style>
    [data-testid="stMainBlockContainer"]:has(.st-key-dashboard_page) {
        padding-top: 4.75rem;
        padding-bottom: 1.25rem;
    }
    .st-key-dashboard_page {gap: 0.75rem;}
    .st-key-dashboard_top_latest,.st-key-dashboard_top_plan,.st-key-dashboard_top_event {gap:0.4rem;}
    .st-key-dashboard_page .activities-summary-grid {
        display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0.42rem;
    }
    .st-key-dashboard_page .activities-summary-item {
        padding:0.52rem 0.58rem;border:1px solid rgba(128,128,128,0.18);border-radius:0.5rem;
    }
    .st-key-dashboard_page .activities-summary-label {font-size:0.6rem;opacity:0.65;}
    .st-key-dashboard_page .activities-summary-value {font-size:0.92rem;font-weight:720;}
    .st-key-dashboard_page .next-workout-steps {gap:0.25rem;}
    .st-key-dashboard_page .next-workout-step {padding:0.28rem 0.35rem;}
    .st-key-dashboard_page .next-workout-context {margin-top:0.4rem;padding-top:0.35rem;}
    .st-key-dashboard_page .next-workout-meta,
    .st-key-dashboard_page .next-workout-label {color:inherit;opacity:0.65;}
    </style>""")
    with st.container(key="dashboard_page"):
        return _show_dashboard_content(
            athlete,
            daily_brief_resolution=daily_brief_resolution,
        )


def _show_dashboard_content(athlete, *, daily_brief_resolution=None):
    """
    Displays the main athlete dashboard.
    """

    dashboard = DashboardData(
        athlete,
    )
    dashboard_data = dashboard.build()

    latest_activity = dashboard_data["latest_activity"]
    planning = dashboard_data["planning"]
    next_event = dashboard_data["next_event"]
    reference_time = datetime.now().astimezone()
    current_state = athlete.analytics.training_state_at(reference_time=reference_time)
    upcoming_events = CalendarPresenter(
        history=athlete.history,
        training_plan=athlete.training_plan,
        events=athlete.events,
    ).upcoming_events(
        reference_day=reference_time.date(),
    )
    training_load = dashboard.training_load_at(
        reference_time=reference_time,
    )

    activity_col, planning_col, event_col = (
        dashboard_row(
            (1, 3.2, 1),
            gap="small",
        )
    )

    with activity_col:

        with dashboard_widget(
            title="Latest Activity",
            icon=":material/history:",
            divider=False,
            key="dashboard_top_latest",
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
            key="dashboard_top_plan",
        ):

            show_planning_card(
                planning,
            )

    with event_col:

        with dashboard_widget(
            title="Upcoming Events",
            icon=":material/event:",
            divider=False,
            key="dashboard_top_event",
            action=DashboardAction(
                label="Manage Events",
                key="next-event-action",
                callback=lambda: open_event_manager(
                    athlete,
                ),
            ),
        ):

            next_event_card(
                upcoming_events,
            )

    state_col, brief_col, workout_col, summary_col = dashboard_row((2, 1.7, 1.6, 1.6), gap="small")

    with state_col:
        with dashboard_widget(title="Training Load & Recovery", icon=":material/monitoring:",
                              divider=False, key="dashboard_current_state"):
            summary = CurrentStateSummaryData(
                recovery_score=current_state.recovery_score,
                recovery_balance=current_state.recovery_balance,
                recovery_status=current_state.recovery_status,
                chronic_load=current_state.ctl,
                acute_load=current_state.atl,
                load_status=training_load.status,
                form=current_state.form,
                recovery_recommendation=(
                    current_state.recovery_recommendation
                ),
                load_score=training_load.score,
                ramp_rate=training_load.ramp_rate,
                recovery_reference_time=current_state.reference_time,
                hours_since_last_workout=current_state.hours_since_last_workout,
                recovery_is_time_aware=current_state.recovery_is_time_aware,
            )
            st.markdown(
                "<style>" + current_state_summary_styles() + "</style>"
                + current_state_summary_html(summary, compact=True),
                unsafe_allow_html=True,
            )

    with brief_col:
        with dashboard_widget(title="Daily Brief", icon=":material/today:",
                              divider=False, key="dashboard_brief"):
            narrative = getattr(daily_brief_resolution, "narrative", None)
            if isinstance(narrative, str) and narrative.strip():
                st.write(narrative.strip())
                metadata = _daily_brief_metadata(daily_brief_resolution)
                st.caption(
                    "Automatic Training Coach"
                    + (f" · {metadata}" if metadata else " · Generated for today")
                )
            else:
                st.caption("Local guidance from Today · Fallback")
                today = TodayPresenter(athlete).build(reference_time=reference_time)
                st.markdown(f"**{today.guidance.title}**")
                st.write(today.guidance.action)
                if planning.next_workout is not None:
                    st.caption(f"Next planned session: {planning.next_workout.title}")
                if next_event is not None:
                    st.caption(f"Next event: {next_event.name} · {next_event.event_date:%d %b %Y}")
            st.caption("This guidance does not change your training plan.")

    with workout_col:
        with dashboard_widget(title="Next Workout", icon=":material/fitness_center:",
                              divider=False, key="dashboard_next_workout"):
            next_workout_card(planning.next_workout)

    with summary_col:
        from ..activities_page import _show_activity_summary
        with dashboard_widget(title="Activities Summary", icon=":material/assessment:",
                              divider=False, key="dashboard_summary"):
            activities = ActivitiesPresenter(
                athlete.history, training_plan=athlete.training_plan,
                reference_day=reference_time.date(),
            ).build()
            _show_activity_summary(activities, reference_day=reference_time.date(), show_title=False)

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
