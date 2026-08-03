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
from .activity_input import (
    show_activity_input,
)
from .route_map import (
    show_route_map,
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
)

def _activity_rows(
    activities,
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
                activity.outcome_status.title()
                if activity.outcome_status
                is not None
                else "Unplanned"
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

    return label.casefold()

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


def show_activities_page(
    athlete,
) -> None:
    """
    Displays the athlete's completed activity history.
    """

    st.title("Activities")

    st.caption(
        "Review completed training and imported activity data."
    )

    with st.expander(
        "Add activity",
        expanded=False,
    ):

        show_activity_input(
            athlete,
            key_prefix="activities_page",
            show_header=False,
        )

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
            for activity in all_activities
        },
        key=str.casefold,
    )

    (
        search_column,
        sport_column,
        outcome_column,
        period_column,
    ) = st.columns(
        [2, 1, 1, 1]
    )

    with search_column:

        query = st.text_input(
            "Search activities",
            placeholder="Search by activity name",
            key="activities_search",
        )

    with sport_column:

        selected_sport = st.selectbox(
            "Sport",
            options=(
                "All sports",
                *available_sports,
            ),
            key="activities_sport",
        )

    with outcome_column:

        selected_outcome = st.selectbox(
            "Plan result",
            options=_OUTCOME_OPTIONS,
            key="activities_outcome",
        )

    with period_column:

        selected_period = st.selectbox(
            "Period",
            options=_PERIOD_OPTIONS,
            key="activities_period",
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

    total_duration = _total_duration(
        activities
    )

    sports = {
        activity.sport
        for activity in activities
    }

    (
        activity_column,
        summary_sport_column,
        duration_column,
    ) = st.columns(3)

    with activity_column:

        st.metric(
            "Activities",
            len(activities),
        )

    with summary_sport_column:

        st.metric(
            "Sports",
            len(sports),
        )

    with duration_column:

        st.metric(
            "Total duration",
            format_duration(
                total_duration
            ),
        )

    st.divider()

    st.subheader(
        "Activity history"
    )

    if not activities:

        st.info(
            "No activities match the selected filters."
        )

        return

    selection_event = st.dataframe(
        _activity_rows(
            activities
        ),
        width="stretch",
        hide_index=True,
        key="activities_history_table",
        on_select="rerun",
        selection_mode="single-row",
    )

    selected_rows = (
        selection_event.selection.rows
    )

    if not selected_rows:

        st.caption(
            "Select an activity to view its details."
        )

        return

    selected_index = selected_rows[0]

    if selected_index >= len(activities):
        return

    selected_activity = activities[
        selected_index
    ]

    selected_workout = _workout_for_activity(
        athlete.history,
        selected_activity,
    )

    if selected_workout is None:

        st.warning(
            "The selected activity is no longer available."
        )

        return

    st.divider()

    st.subheader(
        selected_activity.title
    )

    st.caption(
        f"{selected_activity.sport} · "
        f"{format_workout_date(selected_activity.workout_date)}"
    )

    if (
        selected_activity.outcome_status
        is not None
    ):

        outcome_label = (
            selected_activity
            .outcome_status
            .title()
        )

        planned_label = (
            selected_activity.planned_title
            or "Planned workout"
        )

        st.info(
            f"{outcome_label} · "
            f"Planned: {planned_label}"
        )
        (
            planned_load_column,
            completed_load_column,
            difference_column,
        ) = st.columns(3)

        with planned_load_column:

            st.metric(
                "Planned load",
                _format_load(
                    selected_activity.planned_load
                ),
            )

        with completed_load_column:

            st.metric(
                "Completed load",
                _format_load(
                    selected_activity.completed_load
                ),
            )

        with difference_column:

            st.metric(
                "Load difference",
                _format_load(
                    selected_activity.load_difference,
                    signed=True,
                ),
            )

        st.caption(
            "Session-RPE load is calculated from "
            "duration × RPE. Planned running load may "
            "also include the conservative elevation "
            "adjustment defined by PerformanceLab."
        )

    else:

        st.caption(
            "This activity was not associated "
            "with a planned workout."
        )

    show_workout_details(
        selected_workout
    )

    show_route_map(
        selected_workout
    )