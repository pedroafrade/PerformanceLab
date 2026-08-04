"""
PerformanceLab

Complete training-plan page.
"""

from datetime import date
from html import escape

import altair as alt
import streamlit as st

from performancelab.presentation import (
    PlanPresenter,
)
from .phase_timeline import (
    phase_timeline_from_phases_html,
    phase_timeline_styles,
)
from .summary_cards import (
    summary_cards_html,
    summary_cards_styles,
)
from .workout_table import (
    format_duration,
)


def _status_label(
    status: str,
) -> str:
    """
    Returns a readable planned-workout status.
    """

    return (
        str(status or "pending")
        .replace("_", " ")
        .title()
    )

def _progression_chart_data(
    weeks,
) -> list[dict]:
    """
    Converts planned sessions into chronological
    chart points.

    Rest days are omitted because they do not contain
    a planned workout.
    """

    return [
        {
            "Date": (
                workout.scheduled_at
                .isoformat()
            ),
            "Planned load": (
                workout.planned_load
            ),
            "Session": workout.title,
            "Session type": (
                "Race"
                if workout.is_race
                else "Training"
            ),
        }
        for week in weeks
        for workout in week.workouts
        if workout.planned_load is not None
    ]

def _plan_chart(
    chart_points,
):
    """
    Builds the planned-session chart.

    One point represents one planned workout.
    """

    import altair as alt
    import pandas as pd

    rows = []

    for point in chart_points:

        if point.planned_load is None:
            continue

        rows.append(
            {
                "Date": point.day,
                "Load": point.planned_load,
                "Title": point.title,
                "Phase": point.phase or "",
            }
        )

    if not rows:

        return alt.Chart(
            pd.DataFrame(
                {
                    "Date": [],
                    "Load": [],
                }
            )
        )

    dataframe = pd.DataFrame(
        rows
    )

    return (
        alt.Chart(
            dataframe
        )
        .mark_line(
            point=True,
        )
        .encode(
            x=alt.X(
                "Date:T",
                title=None,
            ),
            y=alt.Y(
                "Load:Q",
                title="Planned load",
            ),
            tooltip=[
                "Date:T",
                "Title:N",
                "Phase:N",
                "Load:Q",
            ],
        )
        .properties(
            height=300,
        )
    )
def _plan_summary_metrics(
    plan,
) -> dict[str, str]:
    """
    Builds concise summary values for the complete plan.
    """

    total_load = sum(
        week.planned_load
        for week in plan.weeks
    )

    max_distance = max(
        (
            point.distance
            for point in plan.progression
        ),
        default=0.0,
    )

    max_elevation = max(
        (
            point.elevation_gain
            for point in plan.progression
        ),
        default=0.0,
    )

    return {
        "Horizon": (
            f"{len(plan.weeks)} weeks"
        ),
        "Planned load": (
            f"{total_load:.0f} AU"
        ),
        "Max distance": (
            f"{max_distance:.0f} km/week"
        ),
        "Max elevation": (
            f"{max_elevation:.0f} m/week"
        ),
    }

def _current_plan_week(
    weeks,
    *,
    reference_day: date,
):
    """
    Returns the plan week containing the reference day.
    """

    return next(
        (
            week
            for week in weeks
            if (
                week.start_date
                <= reference_day
                <= week.end_date
            )
        ),
        None,
    )

def _week_duration_label(
    week,
) -> str:
    """
    Formats the total duration of a plan week.
    """

    total_seconds = sum(
        (
            workout.duration
            .total_seconds()
        )
        for workout in week.workouts
        if workout.duration is not None
    )

    total_minutes = round(
        total_seconds / 60
    )

    hours, minutes = divmod(
        total_minutes,
        60,
    )

    if hours and minutes:
        return f"{hours}h{minutes:02d}"

    if hours:
        return f"{hours}h"

    return f"{minutes} min"



def _week_is_current(
    week,
    *,
    reference_day: date,
) -> bool:
    """
    Returns whether the reference day belongs to the week.
    """

    return (
        week.start_date
        <= reference_day
        <= week.end_date
    )


def _week_html(
    week,
) -> str:
    """
    Renders the workouts of one plan week.
    """

    parts = [
        '<div class="complete-plan-week">'
    ]

    for workout in week.workouts:

        status = (
            str(
                workout.status
                or "pending"
            )
            .replace("_", "-")
        )

        title = escape(
            workout.title
        )

        sport = escape(
            str(
                workout.sport
                or "Rest"
            )
        )

        intensity = escape(
            str(
                workout.intensity
                or "—"
            )
        )

        duration = escape(
            format_duration(
                workout.duration
            )
        )

        prescription = (
            escape(
                workout.prescription_summary
            )
            if workout.prescription_summary
            else ""
        )

        parts.append(
            (
                '<div class="complete-plan-session '
                f'status-{escape(status)}">'
                '<div class="complete-plan-session-date">'
                f"{workout.scheduled_at.strftime('%a %d')}"
                "</div>"
                '<div class="complete-plan-session-main">'
                f"<strong>{title}</strong>"
                f"<span>{sport}</span>"
            )
        )

        if prescription:

            parts.append(
                (
                    '<span class="complete-plan-prescription">'
                    f"{prescription}"
                    "</span>"
                )
            )

        parts.append(
            (
                "</div>"
                '<div class="complete-plan-session-value">'
                f"{duration}"
                "</div>"
                '<div class="complete-plan-session-value">'
                f"{intensity}"
                "</div>"
                '<div class="complete-plan-session-status">'
                f"{escape(_status_label(workout.status))}"
                "</div>"
                "</div>"
            )
        )

    parts.append(
        "</div>"
    )

    return "".join(parts)


def _plan_styles() -> None:
    """
    Applies visual styling to the complete plan.
    """

    st.markdown(
        """
        <style>
        .complete-plan-week {
            display: flex;
            flex-direction: column;
            gap: 0.45rem;
            padding-top: 0.35rem;
        }

        .complete-plan-session {
            display: grid;
            grid-template-columns:
                minmax(70px, 0.7fr)
                minmax(220px, 3fr)
                minmax(80px, 0.8fr)
                minmax(100px, 1fr)
                minmax(90px, 0.9fr);
            gap: 0.75rem;
            align-items: center;
            padding: 0.7rem 0.8rem;
            border: 1px solid rgba(128, 128, 128, 0.22);
            border-left: 4px solid #4f86f7;
            border-radius: 0.5rem;
            background: var(--background-color);
        }

        .complete-plan-session.status-equivalent {
            border-left-color: #39a96b;
        }

        .complete-plan-session.status-modified,
        .complete-plan-session.status-substitute {
            border-left-color: #d28b27;
        }

        .complete-plan-session.status-missed {
            border-left-color: #e05a5a;
            opacity: 0.72;
        }

        .complete-plan-session-date {
            font-size: 0.76rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .complete-plan-session-main {
            min-width: 0;
            display: flex;
            flex-direction: column;
            gap: 0.12rem;
        }

        .complete-plan-session-main strong,
        .complete-plan-session-main span {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .complete-plan-session-main span,
        .complete-plan-session-value {
            color: rgba(128, 128, 128, 0.95);
            font-size: 0.76rem;
        }

        .complete-plan-prescription {
            color: inherit !important;
        }

        .complete-plan-session-status {
            font-size: 0.72rem;
            font-weight: 700;
            text-align: right;
        }

        @media (max-width: 900px) {
            .complete-plan-session {
                grid-template-columns:
                    minmax(60px, 0.7fr)
                    minmax(160px, 2fr)
                    minmax(80px, 0.8fr);
            }

            .complete-plan-session-value {
                display: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_plan_page(
    athlete,
    *,
    on_generate_plan=None,
) -> None:
    """
    Displays the athlete's complete persistent plan.
    """

    today = date.today()

    title_column, action_column = (
        st.columns(
            [5, 1]
        )
    )

    with title_column:

        st.title(
            "Plan"
        )

        st.caption(
            "Review the complete persistent plan "
            "through the target event and recovery."
        )

    with action_column:

        st.write("")

        st.button(
            "Generate plan",
            icon=":material/auto_awesome:",
            type="primary",
            use_container_width=True,
            key="plan_generate",
            on_click=on_generate_plan,
            disabled=(
                on_generate_plan is None
            ),
        )

    plan = PlanPresenter(
        plan=athlete.training_plan,
        history=athlete.history,
    ).build(
        reference_day=today
    )

    if not plan.weeks:

        st.info(
            "No training plan is available. "
            "Generate a plan to begin."
        )

        return

    summary = (
        _plan_summary_metrics(
            plan
        )
    )

    current_week = (
        _current_plan_week(
            plan.weeks,
            reference_day=today,
        )
    )

    main_column, sidebar_column = (
        st.columns(
            [3, 1],
            gap="large",
        )
    )

    with main_column:

        timeline_visible_start = (
            current_week.start_date
            if current_week is not None
            else today
        )

        timeline_visible_end = (
            current_week.end_date
            if current_week is not None
            else today
        )

        timeline_html = (
            phase_timeline_from_phases_html(
                phases=plan.phases,
                current_date=today,
                visible_start=(
                    timeline_visible_start
                ),
                visible_end=(
                    timeline_visible_end
                ),
            )
        )

        if timeline_html:

            st.markdown(
                (
                    "<style>"
                    + phase_timeline_styles()
                    + "</style>"
                    + timeline_html
                ),
                unsafe_allow_html=True,
            )

        st.divider()

        summary_html = (
            summary_cards_html(
                (
                    (
                        "calendar_month",
                        "Horizon",
                        summary["Horizon"],
                    ),
                    (
                        "monitoring",
                        "Planned load",
                        summary["Planned load"],
                    ),
                    (
                        "route",
                        "Max distance",
                        summary["Max distance"],
                    ),
                    (
                        "terrain",
                        "Max elevation",
                        summary["Max elevation"],
                    ),
                )
            )
        )

        st.markdown(
            (
                "<style>"
                + summary_cards_styles()
                + "</style>"
                + summary_html
            ),
            unsafe_allow_html=True,
        )

        st.divider()

        st.subheader(
            "Plan progression"
        )

        st.caption(
            "Planned load for each session on its exact "
            "calendar date. Rest days are omitted."
        )

        st.altair_chart(
            _plan_chart(
                plan.chart_points
            ),
            use_container_width=True,
        )

        st.divider()

        _plan_styles()

        for week in plan.weeks:

            phase = (
                week.phase
                or "Unassigned"
            )

            label = (
                f"{week.start_date.strftime('%d %b')} – "
                f"{week.end_date.strftime('%d %b')} · "
                f"{phase} · "
                f"{week.planned_load:.0f} AU"
            )

            with st.expander(
                label,
                expanded=_week_is_current(
                    week,
                    reference_day=today,
                ),
            ):

                st.markdown(
                    _week_html(
                        week
                    ),
                    unsafe_allow_html=True,
                )
                
    with sidebar_column:

        with st.container(
            border=True
        ):

            st.markdown(
                "**Current phase**"
            )

            if plan.current_phase is None:

                st.caption(
                    "No current phase."
                )

            else:

                current_phase = (
                    plan.current_phase
                )

                st.markdown(
                    f"### {current_phase.name}"
                )

                st.caption(
                    (
                        f"{current_phase.start_date.strftime('%d %b')} "
                        "– "
                        f"{current_phase.end_date.strftime('%d %b')}"
                    )
                )

                st.write(
                    current_phase.objective
                )

                st.metric(
                    "Weeks remaining",
                    current_phase.weeks_remaining,
                )

        with st.container(
            border=True
        ):

            st.markdown(
                "**Current week**"
            )

            if current_week is None:

                st.caption(
                    "No current plan week."
                )

            else:

                phase = (
                    current_week.phase
                    or "Unassigned"
                )

                st.markdown(
                    (
                        f"### {current_week.start_date.strftime('%d %b')} "
                        "– "
                        f"{current_week.end_date.strftime('%d %b')}"
                    )
                )

                st.caption(
                    phase
                )

                sessions_column, duration_column = (
                    st.columns(2)
                )

                with sessions_column:

                    st.metric(
                        "Sessions",
                        len(
                            current_week.workouts
                        ),
                    )

                with duration_column:

                    st.metric(
                        "Duration",
                        _week_duration_label(
                            current_week
                        ),
                    )

                st.metric(
                    "Planned load",
                    (
                        f"{current_week.planned_load:.0f} AU"
                    ),
                )

        with st.container(
            border=True
        ):

            st.markdown(
                "**Latest adaptation**"
            )

            st.caption(
                "Coming soon"
            )