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
_ACTIVITIES_PAGE_SIZE = 8


def _apply_activities_page_styles() -> None:
    """
    Aligns Activities with the Development page and
    keeps the activity browser compact.
    """

    st.markdown(
        """
        <style>
        div[data-testid="stMainBlockContainer"] {
            padding-top: 3.65rem;
            padding-bottom: 0.6rem;
        }

        section[data-testid="stMain"] > div {
            padding-bottom: 0 !important;
        }

        .activities-page-header {
            margin: 0 0 0.65rem 0;
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
            margin: 0 0 0.15rem 0;
            font-size: 1.25rem;
            font-weight: 700;
            line-height: 1.1;
        }

        .activities-section-copy {
            margin-bottom: 0.55rem;
            font-size: 0.7rem;
            opacity: 0.58;
        }

        .activities-summary-grid {
            display: grid;
            grid-template-columns:
                repeat(2, minmax(0, 1fr));
            gap: 0.5rem;
        }

        .activities-summary-item {
            padding: 0.65rem 0.7rem;
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 0.55rem;
            box-sizing: border-box;
        }

        .activities-summary-label {
            margin-bottom: 0.12rem;
            font-size: 0.64rem;
            opacity: 0.55;
        }

        .activities-summary-value {
            font-size: 1.05rem;
            font-weight: 720;
            line-height: 1.1;
        }

        .activities-selected-header {
            margin: 0.4rem 0 0.55rem;
            padding: 0.6rem 0.7rem;
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-radius: 0.6rem;
            background: rgba(128, 128, 128, 0.025);
        }

        .activities-selected-title {
            font-size: 1rem;
            font-weight: 720;
        }

        .activities-selected-meta {
            margin-top: 0.12rem;
            font-size: 0.68rem;
            opacity: 0.58;
        }

        div[data-testid="stButton"] > button[
            kind="secondary"
        ] {
            text-align: left;
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
    Compact single-line activity browser label.
    """

    values = [
        format_workout_date(
            activity.workout_date
        ),
        activity.title or "Activity",
        activity.sport or "—",
        format_distance(
            activity.distance
        ),
        format_duration(
            activity.duration
        ),
    ]

    if activity.elevation_gain is not None:
        values.append(
            format_elevation(
                activity.elevation_gain
            )
        )

    if activity.rpe is not None:
        values.append(
            f"RPE {activity.rpe:g}"
        )

    if activity.outcome_status:
        values.append(
            _outcome_label(
                activity.outcome_status
            )
        )

    return "  ·  ".join(
        str(value)
        for value in values
        if value
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
            "Displayed",
            (
                f"{min(len(activities), _ACTIVITIES_PAGE_SIZE)}"
                f" / {len(activities)}"
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


def _activity_page_slice(
    activities,
    *,
    page: int,
):
    """
    Returns one compact page of activity rows.
    """

    if not activities:
        return ()

    page = max(
        0,
        page,
    )

    start = (
        page
        * _ACTIVITIES_PAGE_SIZE
    )

    end = (
        start
        + _ACTIVITIES_PAGE_SIZE
    )

    return tuple(
        activities[
            start:end
        ]
    )


def _show_selected_activity_dashboard(
    *,
    activity,
    workout,
    athlete,
) -> None:
    """
    Inline dashboard opened directly below the
    selected activity row.
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
                "Planned load",
                _format_load(
                    activity.planned_load
                ),
            )

        with completed_column:
            st.metric(
                "Completed load",
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

    (
        analysis_tab,
        details_tab,
    ) = st.tabs(
        [
            "Performance",
            "Details",
        ]
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

        if (
            "activities_browser_page"
            not in st.session_state
        ):
            st.session_state[
                "activities_browser_page"
            ] = 0

        page_count = max(
            1,
            (
                len(activities)
                + _ACTIVITIES_PAGE_SIZE
                - 1
            )
            // _ACTIVITIES_PAGE_SIZE,
        )

        page = min(
            st.session_state[
                "activities_browser_page"
            ],
            page_count - 1,
        )

        st.session_state[
            "activities_browser_page"
        ] = page

        visible_activities = (
            _activity_page_slice(
                activities,
                page=page,
            )
        )

        selected_id = (
            st.session_state.get(
                "activities_selected_id"
            )
        )

        visible_ids = {
            str(
                activity.workout_id
            )
            for activity
            in visible_activities
        }

        if (
            selected_id is not None
            and selected_id
            not in visible_ids
        ):
            selected_id = None

        for activity in (
            visible_activities
        ):

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

                if is_selected:
                    st.session_state[
                        "activities_selected_id"
                    ] = None

                else:
                    st.session_state[
                        "activities_selected_id"
                    ] = activity_id

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
                    "The selected activity "
                    "is no longer available."
                )

                continue

            _show_selected_activity_dashboard(
                activity=activity,
                workout=selected_workout,
                athlete=athlete,
            )

        # ==============================================
        # Pagination
        # ==============================================

        if page_count > 1:

            previous_column, page_column, next_column = (
                st.columns(
                    [1, 2, 1],
                    gap="small",
                )
            )

            with previous_column:

                if st.button(
                    "Previous",
                    disabled=(
                        page <= 0
                    ),
                    use_container_width=True,
                    key=(
                        "activities_previous_page"
                    ),
                ):
                    st.session_state[
                        "activities_browser_page"
                    ] = (
                        page - 1
                    )

                    st.session_state[
                        "activities_selected_id"
                    ] = None

                    st.rerun()

            with page_column:

                st.caption(
                    (
                        f"Page {page + 1} "
                        f"of {page_count}"
                    )
                )

            with next_column:

                if st.button(
                    "Next",
                    disabled=(
                        page
                        >= page_count - 1
                    ),
                    use_container_width=True,
                    key=(
                        "activities_next_page"
                    ),
                ):
                    st.session_state[
                        "activities_browser_page"
                    ] = (
                        page + 1
                    )

                    st.session_state[
                        "activities_selected_id"
                    ] = None

                    st.rerun()