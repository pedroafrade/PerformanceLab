"""
PerformanceLab

Activities page.
"""

from datetime import date, timedelta

import streamlit as st

from performancelab.presentation import (
    ActivitiesPresenter,
    ActivityFilters,
)
from .activity_analysis import (
    show_activity_analysis,
)
from .activity_input import (
    show_activity_input,
)
from .workout_details import (
    show_workout_details,
)
from .workout_table import (
    format_distance,
    format_duration,
    format_elevation,
    format_workout_date,
)


_PERIOD_OPTIONS = (
    "All time",
    "Last 30 days",
    "Last 90 days",
    "This year",
)


_OUTCOME_OPTIONS = (
    "All results",
    "Equivalent",
    "Modified",
    "Substitute",
    "Unplanned",
    "Outside plan",
)

def _outcome_label(
    status: str | None,
) -> str:
    """
    Returns a readable plan-result label.
    """

    if status is None:
        return "Not assessed"

    return (
        status
        .replace("_", " ")
        .title()
    )

def _activity_rows(
    activities,
    *,
    history=None,
) -> list[dict]:
    """
    Converts activity presentation data into table rows.
    """

    return [
        {
            "Date": format_workout_date(
                activity.workout_date
            ),
            "Activity": activity.title,
            "Sport": activity.sport,
            "Analysis": (
                _analysis_available(
                    history,
                    activity,
                )
                if history is not None
                else "—"
            ),
            "Distance": format_distance(
                activity.distance
            ),
            "Duration": format_duration(
                activity.duration
            ),
            "Elevation": format_elevation(
                activity.elevation_gain
            ),
            "RPE": (
                activity.rpe
                if activity.rpe is not None
                else "—"
            ),
            "Plan result": (
                _outcome_label(
                    activity.outcome_status
                )
            ),
            "Planned": (
                activity.planned_title
                or "—"
            ),
        }
        for activity in activities
    ]


def _total_duration(
    activities,
) -> timedelta:
    """
    Returns the accumulated duration of the activities.
    """

    return sum(
        (
            activity.duration
            or timedelta()
            for activity in activities
        ),
        timedelta(),
    )



def _format_load(
    value: float | None,
    *,
    signed: bool = False,
) -> str:
    """
    Formats session-RPE load in arbitrary units.
    """

    if value is None:
        return "—"

    if signed:
        return f"{value:+.0f} AU"

    return f"{value:.0f} AU"


def _outcome_filter_value(
    label: str,
) -> str | None:
    """
    Converts the visible outcome label into a filter value.
    """

    if label == "All results":
        return None

    return (
        label
        .casefold()
        .replace(" ", "_")
    )

def _period_start_date(
    period: str,
    *,
    reference_day: date,
) -> date | None:
    """
    Converts a visible period option into a start date.
    """

    if period == "Last 30 days":

        return reference_day - timedelta(
            days=29
        )

    if period == "Last 90 days":

        return reference_day - timedelta(
            days=89
        )

    if period == "This year":

        return reference_day.replace(
            month=1,
            day=1,
        )

    return None


def _workout_for_activity(
    history,
    activity,
):
    """
    Resolves a presentation item to its domain workout.
    """

    for workout in history:

        if (
            str(workout.workout_id)
            == activity.workout_id
        ):
            return workout

    return None

def _analysis_available(
    history,
    activity,
) -> str:
    """
    Indicates whether the complete workout contains
    GPS and detailed sensor streams.
    """

    workout = (
        _workout_for_activity(
            history,
            activity,
        )
    )

    if workout is None:
        return "—"

    has_gps = bool(
        workout.sensors.get(
            "gps"
        )
    )

    has_performance = any(
        bool(
            workout.sensors.get(
                sensor
            )
        )
        for sensor in (
            "heart_rate",
            "power",
            "cadence",
        )
    )

    if (
        has_gps
        and has_performance
    ):
        return "Route + sensors"

    if has_gps:
        return "Route"

    if has_performance:
        return "Sensors"

    return "Basic"



def _apply_activities_page_styles() -> None:
    """
    Keeps Activities within the viewport and turns the
    history into one compact internally scrolling panel.
    """

    st.markdown(
        """
        <style>
        div[data-testid="stMainBlockContainer"] {
            padding-top: 3.65rem;
            padding-bottom: 0 !important;
        }

        section[data-testid="stMain"] > div {
            padding-bottom: 0 !important;
        }

        div[data-testid="stMainBlockContainer"]
        > div:last-child {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }

        .activities-page-header {
            margin: 0 0 0.55rem 0;
            padding: 0;
        }

        .activities-page-title {
            margin: 0;
            font-size: 2.25rem;
            font-weight: 750;
            line-height: 1.05;
        }

        .activities-page-subtitle {
            margin-top: 0.32rem;
            font-size: 0.76rem;
            line-height: 1.15;
            opacity: 0.58;
        }

        .activities-section-heading {
            margin: 0 0 0.08rem 0;
            font-size: 1.25rem;
            font-weight: 700;
            line-height: 1.1;
        }

        .activities-section-copy {
            margin-bottom: 0.38rem;
            font-size: 0.68rem;
            line-height: 1.2;
            opacity: 0.58;
        }

        /* =================================================
           Scrollable activity browser
           ================================================= */

        .st-key-activities_browser {
            border-color:
                rgba(128, 128, 128, 0.22) !important;
            border-radius: 0.6rem !important;
        }

        .st-key-activities_browser
        div[data-testid="stVerticalBlock"] {
            gap: 0 !important;
        }

        .st-key-activities_browser
        div[data-testid="stElementContainer"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }

        /*
        Activity rows become table-like lines instead
        of separate floating cards.
        */
        .st-key-activities_browser
        div[data-testid="stButton"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        .st-key-activities_browser
        div[data-testid="stButton"] > button {
            width: 100%;
            min-height: 2.15rem;
            height: 2.15rem;
            margin: 0 !important;
            padding: 0.22rem 0.55rem !important;

            border: 0 !important;
            border-bottom:
                1px solid
                rgba(128, 128, 128, 0.15) !important;

            border-radius: 0 !important;

            background:
                transparent !important;

            box-shadow: none !important;

            text-align: left !important;

            font-size: 0.69rem !important;
            font-weight: 500 !important;
            line-height: 1.05 !important;
        }

        .st-key-activities_browser
        div[data-testid="stButton"]
        > button:hover {
            background:
                rgba(128, 128, 128, 0.055)
                !important;
        }

        /*
        Primary = currently expanded activity.
        Keep it subtle instead of a full red row.
        */
        .st-key-activities_browser
        div[data-testid="stButton"]
        > button[kind="primary"] {
            background:
                rgba(255, 75, 75, 0.065)
                !important;

            border-left:
                2px solid #ff4b4b
                !important;

            color: inherit !important;
        }

        /* =================================================
           Expanded activity
           ================================================= */

        .activities-selected-header {
            margin: 0;
            padding: 0.48rem 0.6rem;

            border: 0;
            border-bottom:
                1px solid rgba(128, 128, 128, 0.16);

            border-radius: 0;

            background:
                rgba(128, 128, 128, 0.025);
        }

        .activities-selected-title {
            font-size: 0.88rem;
            font-weight: 720;
            line-height: 1.1;
        }

        .activities-selected-meta {
            margin-top: 0.1rem;
            font-size: 0.62rem;
            line-height: 1.15;
            opacity: 0.58;
        }

        .st-key-activities_browser
        div[data-testid="stMetric"] {
            padding: 0.18rem 0 !important;
        }

        .st-key-activities_browser
        div[data-testid="stMetricLabel"] {
            font-size: 0.62rem !important;
        }

        .st-key-activities_browser
        div[data-testid="stMetricValue"] {
            font-size: 0.9rem !important;
        }

        .st-key-activities_browser
        div[data-testid="stTabs"] {
            margin-top: 0.1rem;
        }

        .st-key-activities_browser
        button[data-baseweb="tab"] {
            min-height: 1.8rem !important;
            padding-top: 0.15rem !important;
            padding-bottom: 0.15rem !important;
            font-size: 0.7rem !important;
        }

        /* =================================================
           Right utility cards
           ================================================= */

        .activities-summary-grid {
            display: grid;
            grid-template-columns:
                repeat(2, minmax(0, 1fr));
            gap: 0.42rem;
        }

        .activities-summary-item {
            padding: 0.52rem 0.58rem;
            border:
                1px solid rgba(128, 128, 128, 0.18);
            border-radius: 0.5rem;
            box-sizing: border-box;
        }

        .activities-summary-label {
            margin-bottom: 0.08rem;
            font-size: 0.6rem;
            opacity: 0.55;
        }

        .activities-summary-value {
            font-size: 0.92rem;
            font-weight: 720;
            line-height: 1.05;
        }

        @media (max-width: 900px) {
            .activities-summary-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>

        <div class="activities-page-header">
            <div class="activities-page-title">
                Activities
            </div>
            <div class="activities-page-subtitle">
                Completed training, route analysis
                and performance progression.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _activity_row_label(
    activity,
) -> str:
    """
    Builds one dense activity-history row.
    """

    primary = (
        f"{format_workout_date(activity.workout_date)}"
        " · "
        f"{activity.title or 'Activity'}"
    )

    metadata = [
        activity.sport or "—",
        format_distance(
            activity.distance
        ),
        format_duration(
            activity.duration
        ),
    ]

    if activity.elevation_gain is not None:
        metadata.append(
            format_elevation(
                activity.elevation_gain
            )
        )

    if activity.rpe is not None:
        metadata.append(
            f"RPE {activity.rpe:g}"
        )

    if activity.outcome_status:
        metadata.append(
            _outcome_label(
                activity.outcome_status
            )
        )

    return (
        primary
        + "  ·  "
        + " · ".join(
            str(value)
            for value in metadata
            if value
        )
    )

def _activities_summary_html(
    *,
    activities,
    sports,
    total_duration,
) -> str:

    items = (
        (
            "Activities",
            str(
                len(activities)
            ),
        ),
        (
            "Sports",
            str(
                len(sports)
            ),
        ),
        (
            "Total duration",
            format_duration(
                total_duration
            ),
        ),
        (
            "Matching",
            str(
                len(activities)
            ),
        ),
    )

    content = "".join(
        (
            '<div class="activities-summary-item">'
            '<div class="activities-summary-label">'
            f"{label}"
            "</div>"
            '<div class="activities-summary-value">'
            f"{value}"
            "</div>"
            "</div>"
        )
        for label, value in items
    )

    return (
        '<div class="activities-summary-grid">'
        f"{content}"
        "</div>"
    )


def _selected_activity_header_html(
    activity,
) -> str:

    return (
        '<div class="activities-selected-header">'
        '<div class="activities-selected-title">'
        f"{activity.title}"
        "</div>"
        '<div class="activities-selected-meta">'
        f"{activity.sport}"
        " · "
        f"{format_workout_date(activity.workout_date)}"
        " · "
        f"{format_distance(activity.distance)}"
        " · "
        f"{format_duration(activity.duration)}"
        "</div>"
        "</div>"
    )

def _show_selected_activity_dashboard(
    *,
    activity,
    workout,
    athlete,
) -> None:
    """
    Compact dashboard rendered inside the scrolling
    activity browser itself.
    """

    st.markdown(
        _selected_activity_header_html(
            activity
        ),
        unsafe_allow_html=True,
    )

    if (
        activity.outcome_status
        is not None
    ):
        (
            planned_column,
            completed_column,
            difference_column,
        ) = st.columns(
            3,
            gap="small",
        )

        with planned_column:
            st.metric(
                "Planned",
                _format_load(
                    activity.planned_load
                ),
            )

        with completed_column:
            st.metric(
                "Completed",
                _format_load(
                    activity.completed_load
                ),
            )

        with difference_column:
            st.metric(
                "Δ load",
                _format_load(
                    activity.load_difference,
                    signed=True,
                ),
            )

    analysis_tab, details_tab = (
        st.tabs(
            [
                "Performance",
                "Details",
            ]
        )
    )

    with analysis_tab:

        show_activity_analysis(
            workout,
            history=athlete.history,
            key_prefix=(
                "activities_inline_"
                f"{activity.workout_id}"
            ),
            show_heading=False,
            compact=True,
        )

    with details_tab:

        show_workout_details(
            workout
        )

def show_activities_page(
    athlete,
) -> None:
    """
    Displays a compact activity browser with inline
    performance analysis.
    """

    _apply_activities_page_styles()

    presenter = ActivitiesPresenter(
        athlete.history,
        training_plan=(
            athlete.training_plan
        ),
        reference_day=date.today(),
    )

    all_activities = presenter.build()

    if not all_activities:
        st.info(
            "No activities are available yet. "
            "Import a file or add an activity manually."
        )
        return

    available_sports = sorted(
        {
            activity.sport
            for activity
            in all_activities
        },
        key=str.casefold,
    )

    (
        activity_column,
        utility_column,
    ) = st.columns(
        [1.85, 1],
        gap="large",
        vertical_alignment="top",
    )

    # ==================================================
    # RIGHT — filters / summary
    # ==================================================

    with utility_column:

        with st.container(
            border=True
        ):
            st.markdown(
                "**Find activities**"
            )

            query = st.text_input(
                "Search",
                placeholder=(
                    "Search by activity name"
                ),
                key="activities_search",
            )

            selected_sport = (
                st.selectbox(
                    "Sport",
                    options=(
                        "All sports",
                        *available_sports,
                    ),
                    key="activities_sport",
                )
            )

            selected_outcome = (
                st.selectbox(
                    "Plan result",
                    options=(
                        _OUTCOME_OPTIONS
                    ),
                    key="activities_outcome",
                )
            )

            selected_period = (
                st.selectbox(
                    "Period",
                    options=(
                        _PERIOD_OPTIONS
                    ),
                    key="activities_period",
                )
            )

            with st.expander(
                "Add activity",
                expanded=False,
            ):
                show_activity_input(
                    athlete,
                    key_prefix=(
                        "activities_page"
                    ),
                    show_header=False,
                )

        today = date.today()

        activities = presenter.build(
            filters=ActivityFilters(
                query=query,
                sport=(
                    None
                    if selected_sport
                    == "All sports"
                    else selected_sport
                ),
                outcome_status=(
                    _outcome_filter_value(
                        selected_outcome
                    )
                ),
                start_date=(
                    _period_start_date(
                        selected_period,
                        reference_day=today,
                    )
                ),
                end_date=today,
            )
        )

        total_duration = (
            _total_duration(
                activities
            )
        )

        sports = {
            activity.sport
            for activity
            in activities
        }

        with st.container(
            border=True
        ):
            st.markdown(
                "**Activity summary**"
            )

            st.html(
                _activities_summary_html(
                    activities=activities,
                    sports=sports,
                    total_duration=(
                        total_duration
                    ),
                )
            )

    # ==================================================
    # LEFT — activity browser
    # ==================================================

    with activity_column:

        st.markdown(
            (
                '<div class="activities-section-heading">'
                "Activity history"
                "</div>"
                '<div class="activities-section-copy">'
                "Select a session to expand its route, "
                "sensor analysis and historical comparison."
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        if not activities:

            st.info(
                "No activities match the "
                "selected filters."
            )

            return

        selected_id = (
            st.session_state.get(
                "activities_selected_id"
            )
        )

        activity_ids = {
            str(
                activity.workout_id
            )
            for activity in activities
        }

        if (
            selected_id is not None
            and selected_id
            not in activity_ids
        ):
            selected_id = None

            st.session_state[
                "activities_selected_id"
            ] = None

        with st.container(
            height=500,
            border=True,
            key="activities_browser",
        ):

            for activity in activities:

                activity_id = str(
                    activity.workout_id
                )

                is_selected = (
                    selected_id
                    == activity_id
                )

                clicked = st.button(
                    _activity_row_label(
                        activity
                    ),
                    key=(
                        "activity_row_"
                        f"{activity_id}"
                    ),
                    use_container_width=True,
                    type=(
                        "primary"
                        if is_selected
                        else "secondary"
                    ),
                )

                if clicked:

                    st.session_state[
                        "activities_selected_id"
                    ] = (
                        None
                        if is_selected
                        else activity_id
                    )

                    st.rerun()

                if not is_selected:
                    continue

                selected_workout = (
                    _workout_for_activity(
                        athlete.history,
                        activity,
                    )
                )

                if selected_workout is None:

                    st.warning(
                        "The selected activity is "
                        "no longer available."
                    )

                    continue

                _show_selected_activity_dashboard(
                    activity=activity,
                    workout=selected_workout,
                    athlete=athlete,
                )