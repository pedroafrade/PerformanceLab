"""
PerformanceLab

Today page.
"""

from datetime import datetime, timedelta
from html import escape

import streamlit as st

from performancelab.presentation import (
    TodayPresenter,
)

from .activity_analysis import (
    show_activity_analysis,
)


def _navigate_to(
    page: str,
) -> None:
    """
    Opens another application page from Today.
    """

    st.session_state.page = page


def _duration_label(
    duration: timedelta | None,
) -> str | None:
    """
    Formats a duration for the daily session.
    """

    if duration is None:
        return None

    total_minutes = round(
        duration.total_seconds()
        / 60
    )

    hours, minutes = divmod(
        total_minutes,
        60,
    )

    if hours and minutes:
        return (
            f"{hours}h {minutes:02d}m"
        )

    if hours:
        return f"{hours}h"

    return f"{minutes} min"


def _readiness_score_label(
    value: int | float,
) -> str:
    """
    Formats the daily recovery score.
    """

    return f"{round(value)}/100"

def _recovery_context_label(
    readiness,
) -> str:
    """
    Explains whether the recovery value uses intraday
    timing or the daily fallback.
    """

    values = [
        readiness.recovery_status,
        (
            "Balance "
            f"{readiness.recovery_balance:+.1f}"
        ),
    ]

    if (
        readiness.recovery_is_time_aware
    ):
        hours = (
            readiness
            .hours_since_last_workout
        )

        if hours is not None:
            values.append(
                f"{round(hours)} h since "
                "last session"
            )
        else:
            values.append(
                "Time-aware estimate"
            )
    else:
        values.append(
            "Daily estimate"
        )

    return " · ".join(
        values
    )


def _recovery_updated_label(
    readiness,
) -> str | None:
    """
    Formats the instant represented by the recovery
    estimate.
    """

    if (
        readiness.reference_time
        is None
    ):
        return None

    return (
        "Updated "
        f"{readiness.reference_time:%H:%M}"
    )

def _form_label(
    value: float,
) -> str:
    """
    Formats the current physiological form.
    """

    return f"{value:+.1f}"


def _recent_load_label(
    value: float,
) -> str:
    """
    Formats the recent training load.
    """

    return f"{value:.1f}"


def _today_session_title(
    session,
) -> str:
    """
    Returns the most relevant title for today.
    """

    if session is None:
        return "Rest day"

    if session.completed:
        return (
            session.completed_title
            or session.title
            or "Completed activity"
        )

    return (
        session.title
        or "Rest day"
    )


def _today_session_status(
    session,
) -> str:
    """
    Returns a readable daily session status.
    """

    if session is None:
        return "No planned training"

    if session.outcome_status:
        return (
            session.outcome_status
            .replace("_", " ")
            .title()
        )

    if session.completed:
        return "Completed"

    if session.title:
        return "Planned"

    return "Recovery"


def _today_session_metadata(
    session,
) -> str:
    """
    Returns concise session metadata.
    """

    if session is None:
        return "No training is planned."

    values = [
        value
        for value in (
            (
                session.completed_sport
                if session.completed
                else session.sport
            ),
            _duration_label(
                session.duration
            ),
            session.intensity,
        )
        if value
    ]

    if not values:
        return (
            "Use today for recovery "
            "and preparation."
        )

    return " · ".join(
        values
    )


def _session_step_html(
    *,
    index: int,
    step: str,
) -> str:
    """
    Builds one monochrome executable session row.
    """

    return (
        "<div style='"
        "display:grid;"
        "grid-template-columns:1.55rem minmax(0,1fr);"
        "align-items:center;"
        "gap:0.65rem;"
        "padding:0.42rem 0.15rem;"
        "border-bottom:1px solid rgba(128,128,128,0.22);"
        "'>"
        "<span style='"
        "display:flex;"
        "align-items:center;"
        "justify-content:center;"
        "width:1.35rem;"
        "height:1.35rem;"
        "border:1px solid rgba(128,128,128,0.45);"
        "border-radius:50%;"
        "font-size:0.72rem;"
        "font-weight:600;"
        "'>"
        f"{index}"
        "</span>"
        "<span style='"
        "font-size:0.88rem;"
        "line-height:1.35;"
        "'>"
        f"{escape(step)}"
        "</span>"
        "</div>"
    )

def _activity_distance_label(
    value: float | None,
) -> str:
    if value is None:
        return "—"

    return f"{value:.1f} km"


def _activity_elevation_label(
    value: float | None,
) -> str:
    if value is None:
        return "—"

    return f"+{value:.0f} m"


def _activity_load_label(
    value: float | None,
) -> str:
    if value is None:
        return "—"

    return f"{value:.0f} AU"


def _activity_rpe_label(
    value: float | None,
) -> str:
    if value is None:
        return "—"

    return f"{value:.1f}"


def _activity_metric_html(
    *,
    label: str,
    value: str,
) -> str:
    return (
        '<div class="today-activity-metric">'
        '<div class="today-activity-metric-label">'
        f"{escape(label)}"
        "</div>"
        '<div class="today-activity-metric-value">'
        f"{escape(value)}"
        "</div>"
        "</div>"
    )


def _activity_summary_html(
    activity,
) -> str:
    metrics = (
        _activity_metric_html(
            label="Distance",
            value=_activity_distance_label(
                activity.distance
            ),
        )
        + _activity_metric_html(
            label="Duration",
            value=(
                _duration_label(
                    activity.duration
                )
                or "—"
            ),
        )
        + _activity_metric_html(
            label="Elevation",
            value=_activity_elevation_label(
                activity.elevation_gain
            ),
        )
        + _activity_metric_html(
            label="RPE",
            value=_activity_rpe_label(
                activity.rpe
            ),
        )
        + _activity_metric_html(
            label="Completed load",
            value=_activity_load_label(
                activity.completed_load
            ),
        )
    )

    return (
        '<div class="today-activity-summary">'
        f"{metrics}"
        "</div>"
    )

def _show_today_session(
    session,
    today_activity,
) -> None:
    """
    Displays either today's prescription or the
    completed activity summary.

    Once today's activity has been completed, the
    completed session remains the main daily context
    until the calendar day changes.
    """

    completed_today = (
        today_activity is not None
    )

    with st.container(
        border=True
    ):
        st.markdown(
            (
                "**Today's activity**"
                if completed_today
                else "**Today's session**"
            )
        )

        if completed_today:
            st.subheader(
                today_activity.title
                or "Completed activity"
            )

            metadata = [
                value
                for value in (
                    today_activity.sport,
                    "Completed",
                )
                if value
            ]

            st.caption(
                " · ".join(metadata)
            )

            st.html(
                _activity_summary_html(
                    today_activity
                )
            )

            if (
                today_activity.outcome_status
                is not None
            ):
                st.markdown(
                    "**Result vs plan**"
                )

                comparison = []

                if today_activity.planned_title:
                    comparison.append(
                        (
                            "Planned",
                            today_activity.planned_title,
                        )
                    )

                comparison.append(
                    (
                        "Completed",
                        today_activity.title,
                    )
                )

                comparison_html = "".join(
                    (
                        '<div class="today-result-row">'
                        '<span class="today-result-label">'
                        f"{escape(label)}"
                        "</span>"
                        '<span class="today-result-value">'
                        f"{escape(value)}"
                        "</span>"
                        "</div>"
                    )
                    for label, value
                    in comparison
                )

                st.html(
                    (
                        '<div class="today-result-comparison">'
                        f"{comparison_html}"
                        "</div>"
                    )
                )

                st.caption(
                    (
                        "Outcome · "
                        f"{today_activity.outcome_status}"
                    )
                )

        else:
            st.subheader(
                _today_session_title(
                    session
                )
            )

            st.caption(
                _today_session_metadata(
                    session
                )
            )

            if (
                session is not None
                and session.structure
            ):
                steps = "".join(
                    _session_step_html(
                        index=index,
                        step=step,
                    )
                    for index, step in enumerate(
                        session.structure,
                        start=1,
                    )
                )

                st.html(
                    (
                        "<div style='"
                        "margin-top:0.55rem;"
                        "border-top:1px solid "
                        "rgba(128,128,128,0.22);"
                        "'>"
                        f"{steps}"
                        "</div>"
                    )
                )

            st.caption(
                (
                    "Status · "
                    f"{_today_session_status(session)}"
                )
            )

        activity_column, calendar_column = (
            st.columns(
                2,
                gap="small",
            )
        )

        with activity_column:
            st.button(
                (
                    "View activity"
                    if completed_today
                    else "Add activity"
                ),
                icon=(
                    ":material/directions_run:"
                    if completed_today
                    else ":material/add:"
                ),
                use_container_width=True,
                key="today_add_activity",
                on_click=_navigate_to,
                args=("activities",),
            )

        with calendar_column:
            st.button(
                "View calendar",
                icon=":material/calendar_month:",
                use_container_width=True,
                key="today_view_calendar",
                on_click=_navigate_to,
                args=("calendar",),
            )


def _guidance_item_html(
    *,
    index: int,
    text: str,
) -> str:
    """
    Builds one monochrome guidance row.
    """

    return (
        "<div style='"
        "display:grid;"
        "grid-template-columns:1.35rem minmax(0,1fr);"
        "gap:0.55rem;"
        "padding:0.42rem 0;"
        "align-items:start;"
        "'>"
        "<span style='"
        "font-size:0.72rem;"
        "font-weight:600;"
        "line-height:1.45;"
        "'>"
        f"{index}"
        "</span>"
        "<span style='"
        "font-size:0.82rem;"
        "line-height:1.4;"
        "'>"
        f"{escape(text)}"
        "</span>"
        "</div>"
    )


def _adaptation_change_label(
    adaptation,
) -> str:
    """
    Formats the duration change of the latest adaptation.
    """

    return (
        f"{adaptation.previous_minutes} min"
        " → "
        f"{adaptation.revised_minutes} min"
    )

def _adaptation_metric_rows(
    adaptation,
    *,
    adjusted: bool,
) -> tuple[str, ...]:
    """
    Builds the visible before/after metrics for one
    adaptation column.
    """

    prefix = (
        "revised"
        if adjusted
        else "previous"
    )

    rows = []

    minutes = getattr(
        adaptation,
        f"{prefix}_minutes",
        None,
    )

    if minutes is not None:
        rows.append(
            f"{minutes} min"
        )

    distance = getattr(
        adaptation,
        f"{prefix}_distance",
        None,
    )

    if distance is not None:
        rows.append(
            f"{distance:g} km"
        )

    elevation = getattr(
        adaptation,
        f"{prefix}_elevation_gain",
        None,
    )

    if elevation is not None:
        rows.append(
            f"+{elevation:g} m D+"
        )

    prescription = getattr(
        adaptation,
        f"{prefix}_prescription",
        None,
    )

    if prescription:
        rows.append(
            str(
                prescription
            )
        )

    return tuple(
        rows
    )


def _adaptation_column_html(
    *,
    label: str,
    title: str,
    rows: tuple[str, ...],
    adjusted: bool,
) -> str:
    """
    Builds one side of the adaptation comparison card.
    """

    modifier = (
        " adjusted"
        if adjusted
        else ""
    )

    metrics = "".join(
        (
            '<div class="today-adaptation-metric">'
            f"{escape(row)}"
            "</div>"
        )
        for row in rows
    )

    return (
        '<div class="today-adaptation-column'
        f'{modifier}">'
        '<div class="today-adaptation-column-label">'
        f"{escape(label)}"
        "</div>"
        '<div class="today-adaptation-column-title">'
        f"{escape(title)}"
        "</div>"
        '<div class="today-adaptation-metrics">'
        f"{metrics}"
        "</div>"
        "</div>"
    )

def _show_latest_adaptation(
    adaptation,
) -> None:
    """
    Displays the latest persisted plan adaptation.
    """

    if adaptation is None:
        return

    planned_rows = (
        _adaptation_metric_rows(
            adaptation,
            adjusted=False,
        )
    )

    adjusted_rows = (
        _adaptation_metric_rows(
            adaptation,
            adjusted=True,
        )
    )

    planned_html = (
        _adaptation_column_html(
            label="Planned session",
            title=(
                adaptation.workout_title
                or "Planned workout"
            ),
            rows=planned_rows,
            adjusted=False,
        )
    )

    adjusted_html = (
        _adaptation_column_html(
            label="Adjusted session",
            title=(
                adaptation.workout_title
                or "Adjusted workout"
            ),
            rows=adjusted_rows,
            adjusted=True,
        )
    )

    comparison_html = (
        '<div class="today-adaptation-comparison">'
        f"{planned_html}"
        '<div class="today-adaptation-arrow">'
        "&rarr;"
        "</div>"
        f"{adjusted_html}"
        "</div>"
    )

    with st.container(
        border=True
    ):
        st.markdown(
            "**Latest plan adaptation**"
        )

        st.caption(
            adaptation.reason
        )

        st.html(
            comparison_html
        )

def _show_guidance_card(
    *,
    title: str,
    items: tuple[str, ...],
) -> None:
    """
    Displays one compact daily-guidance card.
    """

    with st.container(
        border=True
    ):
        st.markdown(
            f"**{title}**"
        )

        content = "".join(
            _guidance_item_html(
                index=index,
                text=item,
            )
            for index, item in enumerate(
                items,
                start=1,
            )
        )

        st.html(
            content
        )


def _apply_today_page_styles() -> None:
    """
    Reduces unused Streamlit spacing on the Today
    page without changing other application pages.
    """

    st.markdown(
        """
        <style>
        div[data-testid="stMainBlockContainer"] {
            padding-top: 2.25rem;
            padding-bottom: 0.75rem;
        }

        div[data-testid="stMainBlockContainer"] h1 {
            margin-bottom: 0;
        }
        .today-activity-summary {
            display: grid;
            grid-template-columns:
                repeat(3, minmax(0, 1fr));
            gap: 0.7rem;
            margin-top: 0.85rem;
            margin-bottom: 1rem;
        }

        .today-activity-metric {
            min-width: 0;
            padding: 0.7rem 0.75rem;
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 0.55rem;
            background: rgba(128, 128, 128, 0.025);
        }

        .today-activity-metric-label {
            margin-bottom: 0.2rem;
            font-size: 0.68rem;
            opacity: 0.58;
        }

        .today-activity-metric-value {
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.2;
        }

        .today-result-comparison {
            margin-top: 0.45rem;
            margin-bottom: 0.35rem;
            border-top: 1px solid rgba(128, 128, 128, 0.18);
        }

        .today-result-row {
            display: grid;
            grid-template-columns: 6rem minmax(0, 1fr);
            gap: 0.75rem;
            padding: 0.42rem 0;
            border-bottom:
                1px solid rgba(128, 128, 128, 0.14);
        }

        .today-result-label {
            font-size: 0.72rem;
            opacity: 0.58;
        }

        .today-result-value {
            font-size: 0.82rem;
            font-weight: 650;
        }

        .today-adaptation-comparison {
            display: grid;
            grid-template-columns:
                minmax(0, 1fr)
                2rem
                minmax(0, 1fr);
            gap: 0.45rem;
            align-items: stretch;
            margin-top: 0.55rem;
        }

        .today-adaptation-column {
            min-width: 0;
            padding: 0.55rem 0.6rem;
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 0.55rem;
            background: rgba(128, 128, 128, 0.018);
            box-sizing: border-box;
        }

        .today-adaptation-column.adjusted {
            background: rgba(57, 169, 107, 0.045);
        }

        .today-adaptation-column-label {
            margin-bottom: 0.3rem;
            font-size: 0.6rem;
            font-weight: 750;
            text-transform: uppercase;
            opacity: 0.55;
        }

        .today-adaptation-column-title {
            margin-bottom: 0.32rem;
            font-size: 0.82rem;
            font-weight: 700;
            line-height: 1.15;
        }

        .today-adaptation-metrics {
            display: flex;
            flex-direction: column;
            gap: 0.16rem;
        }

        .today-adaptation-metric {
            font-size: 0.72rem;
            line-height: 1.25;
        }

        .today-adaptation-arrow {
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.15rem;
            font-weight: 700;
            opacity: 0.55;
        }

        @media (max-width: 760px) {
            .today-adaptation-comparison {
                grid-template-columns: 1fr;
            }

            .today-adaptation-arrow {
                transform: rotate(90deg);
            }
            .today-activity-summary {
                grid-template-columns:
                    repeat(2, minmax(0, 1fr));
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def _show_daily_decision(
    today,
) -> None:
    """
    Displays the daily decision and the minimum
    physiological context required to understand it.
    """

    with st.container(
        border=True
    ):
        (
            decision_column,
            recovery_column,
            form_column,
            load_column,
        ) = st.columns(
            [3.4, 1, 1, 1],
            gap="medium",
            vertical_alignment="center",
        )

        with decision_column:
            st.markdown(
                f"### {today.coach.summary}"
            )

            st.caption(
                today.coach.recommendation
            )

        with recovery_column:
            st.metric(
                label=(
                    "Estimated recovery"
                ),
                value=_readiness_score_label(
                    today.readiness
                    .recovery_score
                ),
            )

            st.caption(
                _recovery_context_label(
                    today.readiness
                )
            )

            updated_label = (
                _recovery_updated_label(
                    today.readiness
                )
            )

            if updated_label:
                st.caption(
                    updated_label
                )

        with form_column:
            st.metric(
                label="Form",
                value=_form_label(
                    today.readiness.form
                ),
            )

        with load_column:
            st.metric(
                label="Recent load",
                value=_recent_load_label(
                    today.readiness
                    .recent_load
                ),
            )

def _today_completed_workout(
    athlete,
    activity_summary,
):
    """
    Resolves today's presentation summary back to the
    domain Workout so route and sensor data are available.
    """

    if activity_summary is None:
        return None

    workout_id = str(
        activity_summary.workout_id
    )

    return next(
        (
            workout
            for workout
            in athlete.history.workouts
            if str(
                workout.workout_id
            )
            == workout_id
        ),
        None,
    )
@st.fragment(
    run_every=timedelta(
        hours=3,
    )
)
def show_today_page(
    athlete,
) -> None:
    """
    Displays the athlete's daily decision page.
    """

    _apply_today_page_styles()

    today = TodayPresenter(
        athlete
    ).build(
        reference_time=(
            datetime.now().astimezone()
        )
    )

    today_workout = (
        _today_completed_workout(
            athlete,
            today.today_activity_summary,
        )
    )
    st.title(
        "Today"
    )

    st.caption(
        today.reference_day.strftime(
            "%A, %d %B %Y"
        )
    )

    _show_daily_decision(
        today
    )

    session_column, guidance_column = (
        st.columns(
            [1.7, 1],
            gap="large",
            vertical_alignment="top",
        )
    )

    with session_column:
        _show_today_session(
            today.today_session,
            today.today_activity_summary,
        )

        if today_workout is not None:
            show_activity_analysis(
                today_workout,
                history=athlete.history,
                key_prefix="today_activity_analysis",
            )

    with guidance_column:
        _show_guidance_card(
            title="Why this workout today",
            items=today.guidance.reasons,
        )

        _show_guidance_card(
            title="Attention during training",
            items=today.guidance.cautions,
        )

        _show_latest_adaptation(
            today.latest_adaptation
        )
