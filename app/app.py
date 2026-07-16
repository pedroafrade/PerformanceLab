"""
PerformanceLab

Streamlit application with manual workout entry
and session-based athlete state.
"""

from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

from components import (
    show_route_map,
    show_sidebar,
    show_workout_details,
    show_workout_table,
)

from performancelab import Athlete

from performancelab.presentation import (
    DashboardData,
    has_route,

)
from performancelab.builders import (
    create_workout,
)

# ======================================================
# Page configuration
# ======================================================

st.set_page_config(
    page_title="PerformanceLab",
    page_icon="📈",
    layout="wide",
)


# ======================================================
# Formatting helpers
# ======================================================

def format_workout_date(value):

    if value is None:

        return "—"

    if isinstance(value, datetime):

        return value.strftime(
            "%Y-%m-%d %H:%M"
        )

    return value.strftime(
        "%Y-%m-%d"
    )

def format_duration(value: timedelta | None) -> str:

    if value is None:

        return "—"

    total_seconds = int(value.total_seconds())

    hours, remainder = divmod(
        total_seconds,
        3600,
    )

    minutes = remainder // 60

    return f"{hours}h {minutes:02d}m"


# ======================================================

def format_distance(value: float | None) -> str:

    if value is None:

        return "—"

    return f"{value:.2f} km"


# ======================================================

def format_elevation(value: float | None) -> str:

    if value is None:

        return "—"

    return f"{value:.0f} m"

# ======================================================
# Demonstration athlete
# ======================================================

def create_demo_athlete() -> Athlete:

    athlete = Athlete(
        name="Pedro",
        weight=70,
        ftp=280,
        max_hr=190,
        resting_hr=50,
    )

    demo_workouts = [

        create_workout(
            sport="Running",
            workout_date=date.today() - timedelta(days=13),
            distance=8,
            duration=timedelta(minutes=45),
            elevation_gain=120,
            rpe=5,
            title="Easy Run",
        ),

        create_workout(
            sport="Cycling",
            workout_date=date.today() - timedelta(days=11),
            distance=42,
            duration=timedelta(
                hours=1,
                minutes=30,
            ),
            elevation_gain=450,
            rpe=6,
            title="Endurance Ride",
        ),

        create_workout(
            sport="Running",
            workout_date=date.today() - timedelta(days=9),
            distance=12,
            duration=timedelta(
                hours=1,
                minutes=5,
            ),
            elevation_gain=210,
            rpe=7,
            title="Tempo Run",
        ),

        create_workout(
            sport="Swimming",
            workout_date=date.today() - timedelta(days=7),
            distance=2.5,
            duration=timedelta(minutes=50),
            elevation_gain=0,
            rpe=5,
            title="Pool Session",
        ),

        create_workout(
            sport="Cycling",
            workout_date=date.today() - timedelta(days=5),
            distance=55,
            duration=timedelta(hours=2),
            elevation_gain=700,
            rpe=7,
            title="Long Ride",
        ),

        create_workout(
            sport="Running",
            workout_date=date.today() - timedelta(days=3),
            distance=10,
            duration=timedelta(minutes=52),
            elevation_gain=160,
            rpe=6,
            title="Steady Run",
        ),

        create_workout(
            sport="Running",
            workout_date=date.today(),
            distance=16,
            duration=timedelta(
                hours=1,
                minutes=25,
            ),
            elevation_gain=320,
            rpe=8,
            title="Long Run",
        ),

    ]

    for workout in demo_workouts:

        athlete.history.add(workout)

    return athlete


# ======================================================
# Session state initialization
# ======================================================

def initialize_session_state() -> None:

    if "athlete" not in st.session_state:

        st.session_state.athlete = (
            create_demo_athlete()
        )

    if "notice" not in st.session_state:

        st.session_state.notice = None

# ======================================================
# Delete confirmation
# ======================================================

if "confirm_delete" not in st.session_state:

    st.session_state.confirm_delete = False

# ======================================================
# Edit mode
# ======================================================

if "edit_workout" not in st.session_state:

    st.session_state.edit_workout = False

# ======================================================
# Session actions
# ======================================================

def reset_demo_data() -> None:

    st.session_state.athlete = (
        create_demo_athlete()
    )

    st.session_state.notice = (
        "Demonstration data restored."
    )


# ======================================================

def clear_training_data() -> None:

    athlete = st.session_state.athlete

    athlete.history.clear()

    st.session_state.notice = (
        "Workout history cleared."
    )


# ======================================================
# Initialize state
# ======================================================

initialize_session_state()

athlete: Athlete = st.session_state.athlete



# ======================================================
# Sidebar
# ======================================================

athlete = show_sidebar(
        athlete
    )

st.session_state.athlete = athlete

# ======================================================
# Dashboard data
# ======================================================

dashboard = DashboardData(
    athlete,
).build()

summary = dashboard["summary"]
performance = dashboard["performance"]
planning = dashboard["planning"]


# ======================================================
# Header
# ======================================================

st.title("PerformanceLab")

st.caption(
    "Training, physiology and performance analytics."
)

if st.session_state.notice:

    st.success(
        st.session_state.notice
    )

    st.session_state.notice = None

st.subheader(
    dashboard["athlete"]["name"]
    or "Unnamed athlete"
)

sports = dashboard["athlete"]["sports"]

if sports:

    st.write(
        "**Sports:**",
        ", ".join(sports),
    )

else:

    st.write("**Sports:** —")


# ======================================================
# Training summary
# ======================================================

st.divider()

st.subheader("Training summary")

column_1, column_2, column_3, column_4 = (
    st.columns(4)
)

column_1.metric(
    "Workouts",
    summary["workouts"],
)

column_2.metric(
    "Training days",
    summary["training_days"],
)

column_3.metric(
    "Total duration",
    format_duration(
        summary["total_duration"]
    ),
)

average_rpe = summary["average_rpe"]

column_4.metric(
    "Average RPE",
    (
        f"{average_rpe:.1f}"
        if average_rpe is not None
        else "—"
    ),
)


# ======================================================
# Performance management
# ======================================================

st.divider()

st.subheader("Performance management")

column_1, column_2, column_3 = (
    st.columns(3)
)

column_1.metric(
    "CTL — Fitness",
    f"{summary['ctl']:.1f}",
)

column_2.metric(
    "ATL — Fatigue",
    f"{summary['atl']:.1f}",
)

column_3.metric(
    "TSB — Form",
    f"{summary['tsb']:.1f}",
)


# ======================================================
# Performance chart
# ======================================================

if performance["dates"]:

    chart_data = pd.DataFrame(

        {
            "Load": performance["load"],
            "CTL": performance["ctl"],
            "ATL": performance["atl"],
            "TSB": performance["tsb"],
        },

        index=pd.to_datetime(
            performance["dates"]
        ),

    )

    chart_data.index.name = "Date"

    st.line_chart(
        chart_data,
    )

    with st.expander(
        "Show performance data"
    ):

        st.dataframe(
            chart_data,
            width="stretch",
        )

else:

    st.info(
        "Add a workout to display "
        "performance data."
    )


# ======================================================
# Planning
# ======================================================

st.divider()

st.subheader("Planning")

column_1, column_2 = st.columns(2)

next_goal = planning["next_goal"]

with column_1:

    st.markdown("#### Next goal")

    if next_goal is None:

        st.write("No active goals.")

    else:

        st.write(
            next_goal.name
            or "Unnamed goal"
        )

        st.write(
            f"{planning['days_until_next_goal']} "
            "days remaining"
        )

next_event = planning["next_event"]

with column_2:

    st.markdown("#### Next event")

    if next_event is None:

        st.write("No upcoming events.")

    else:

        st.write(
            next_event.event.name
            or "Unnamed event"
        )

        st.write(
            f"{planning['days_until_next_event']} "
            "days remaining"
        )


# ======================================================
# Workout history
# ======================================================

selected_workout = show_workout_table(
    athlete
)

if selected_workout is not None:

    show_workout_details(
        selected_workout
    )



# ======================================================
# Workout actions
# ======================================================

st.divider()

if not st.session_state.confirm_delete:

    action_column_1, action_column_2 = st.columns(2)

    with action_column_1:

        if st.button(

            "🗑 Delete workout",

            use_container_width=True,

        ):

            st.session_state.confirm_delete = True

            st.rerun()

    with action_column_2:

        if st.button(

            "✏️ Edit workout",

            use_container_width=True,

        ):

            st.session_state.edit_workout = True

            st.rerun()

else:

    st.warning(

        "Are you sure you want to delete this workout?"

    )

    confirm_column, cancel_column = st.columns(2)

    with confirm_column:

        if st.button(

            "✅ Delete",

            type="primary",

            use_container_width=True,

        ):

            athlete.history.remove(

                selected_workout

            )

            st.session_state.confirm_delete = False

            st.success(

                "Workout deleted."

            )

            st.rerun()

    with cancel_column:

        if st.button(

            "Cancel",

            use_container_width=True,

        ):

            st.session_state.confirm_delete = False

            st.rerun()
# ======================================================
# Edit workout
# ======================================================

if st.session_state.edit_workout:

    st.divider()

    st.subheader("Edit workout")

    title = st.text_input(
        "Title",
        value=selected_workout.info.title or "",
    )

    sports = [
        "Running",
        "Cycling",
        "Swimming",
        "Walking",
        "Hiking",
        "Strength",
        "Other",
    ]

    current_sport = (
        selected_workout.sport
        if selected_workout.sport in sports
        else "Other"
    )

    sport = st.selectbox(
        "Sport",
        sports,
        index=sports.index(current_sport),
    )

    workout_date = st.date_input(
        "Date",
        value=selected_workout.date,
    )

    distance = st.number_input(
        "Distance (km)",
        min_value=0.0,
        value=float(
            selected_workout.distance or 0
        ),
        step=0.1,
    )

    duration = (
        selected_workout.duration
        if selected_workout.duration is not None
        else timedelta()
    )

    total_seconds = int(
        duration.total_seconds()
    )

    initial_hours = total_seconds // 3600
    initial_minutes = (
        total_seconds % 3600
    ) // 60
    initial_seconds = total_seconds % 60

    duration_column_1, \
        duration_column_2, \
        duration_column_3 = st.columns(3)

    with duration_column_1:

        hours = st.number_input(
            "Hours",
            min_value=0,
            value=initial_hours,
            step=1,
        )

    with duration_column_2:

        minutes = st.number_input(
            "Minutes",
            min_value=0,
            max_value=59,
            value=initial_minutes,
            step=1,
        )

    with duration_column_3:

        seconds = st.number_input(
            "Seconds",
            min_value=0,
            max_value=59,
            value=initial_seconds,
            step=1,
        )

    elevation = st.number_input(
        "Elevation gain (m)",
        min_value=0.0,
        value=float(
            selected_workout.elevation_gain or 0
        ),
        step=1.0,
    )

    rpe = st.slider(
        "RPE",
        min_value=1,
        max_value=10,
        value=int(
            selected_workout.feedback.rpe or 5
        ),
    )

    save_column, cancel_column = st.columns(2)

    with save_column:

        if st.button(
            "💾 Save",
            type="primary",
            use_container_width=True,
        ):

            selected_workout.info.title = title
            selected_workout.info.sport = sport
            selected_workout.info.date = workout_date
            selected_workout.info.distance = (
                distance if distance > 0 else None
            )

            selected_workout.info.duration = timedelta(
                hours=int(hours),
                minutes=int(minutes),
                seconds=int(seconds),
            )

            selected_workout.info.elevation_gain = (
                elevation
            )

            selected_workout.feedback.rpe = rpe

            athlete.history._sort()

            st.session_state.edit_workout = False
            st.session_state.notice = (
                "Workout updated."
            )

            st.rerun()

    with cancel_column:

        if st.button(
            "Cancel",
            use_container_width=True,
        ):

            st.session_state.edit_workout = False

            st.rerun()
# ======================================================
# Route
# ======================================================

if has_route(selected_workout):

    st.markdown("#### Route")

    show_route_map(

        selected_workout

    )

else:

    st.info(
        "No workout is available "
        "for inspection."
    )