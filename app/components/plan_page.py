"""
PerformanceLab

Complete training-plan page.
"""

from datetime import date
from html import escape

import streamlit as st

from performancelab.presentation import (
    PlanPresenter,
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

    total_load = sum(
        week.planned_load
        for week in plan.weeks
    )

    horizon_column, weeks_column, load_column = (
        st.columns(3)
    )

    with horizon_column:

        horizon = (
            (
                f"{plan.start_date.strftime('%d %b %Y')} – "
                f"{plan.end_date.strftime('%d %b %Y')}"
            )
            if (
                plan.start_date is not None
                and plan.end_date is not None
            )
            else "—"
        )

        st.metric(
            "Plan horizon",
            horizon,
        )

    with weeks_column:

        st.metric(
            "Training weeks",
            len(plan.weeks),
        )

    with load_column:

        st.metric(
            "Planned load",
            f"{total_load:.0f} AU",
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